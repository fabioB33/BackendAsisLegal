"""
LiveAvatar Service — liveavatar.com LITE mode
En modo LITE, LiveAvatar solo maneja el avatar visual (video + lip-sync).
El backend controla: STT (ElevenLabs) → LLM (Gemini) → TTS PCM (ElevenLabs) → avatar.

Flujo:
1. create_session() → obtiene session_token, livekit_url, livekit_client_token, ws_url
2. connect_websocket(session_id, ws_url) → conecta WS y espera "connected"
3. speak(session_id, pcm_bytes) → envía audio PCM al avatar para lip-sync
4. interrupt(session_id) → detiene al avatar mid-sentence
5. close_session(session_id) → cierra sesión y WS
"""
import os
import json
import base64
import asyncio
import logging
import httpx
import websockets
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://api.liveavatar.com/v1"


class LiveAvatarService:
    def __init__(self):
        self.api_key  = os.getenv("LIVEAVATAR_API_KEY")
        self.avatar_id = os.getenv("LIVEAVATAR_AVATAR_ID")

        # Dict: session_id → websocket connection
        self._ws_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self._ws_listeners:   Dict[str, asyncio.Task] = {}
        self._event_counters: Dict[str, int] = {}

        if not self.api_key:
            logger.warning("⚠️ LIVEAVATAR_API_KEY not configured")
        if not self.avatar_id:
            logger.warning("⚠️ LIVEAVATAR_AVATAR_ID not configured")
        else:
            logger.info(f"✅ LiveAvatar LITE Service ready (Avatar: {self.avatar_id})")

    def _headers(self) -> Dict:
        return {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

    def _event_id(self, session_id: str) -> str:
        n = self._event_counters.get(session_id, 0) + 1
        self._event_counters[session_id] = n
        return f"{session_id[:8]}_{n}_{datetime.now().strftime('%H%M%S%f')}"

    # ──────────────────────────────────────────────
    # 1. Create session (LITE mode)
    # ──────────────────────────────────────────────
    async def create_session(self, system_prompt: Optional[str] = None) -> Dict:
        """
        Crea sesión LITE en liveavatar.com.
        Returns: session_id, session_token, livekit_url, livekit_token, ws_url
        """
        if not self.api_key or not self.avatar_id:
            raise ValueError("LiveAvatar API key or avatar ID not configured")

        payload = {
            "mode": "LITE",
            "avatar_id": self.avatar_id,
        }

        logger.info(f"🔄 Creating LiveAvatar LITE session (avatar={self.avatar_id})")

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: get session token
            r = await client.post(
                f"{BASE_URL}/sessions/token",
                headers=self._headers(),
                json=payload
            )
            result = r.json()
            logger.info(f"Token response: code={result.get('code')} msg={result.get('message')}")

            if result.get("code") != 1000:
                raise Exception(f"LiveAvatar token error: {result.get('message')}")

            data          = result["data"]
            session_id    = data["session_id"]
            session_token = data["session_token"]

            # Step 2: start session → get LiveKit + WebSocket URLs
            logger.info(f"🔄 Starting LITE session: {session_id}")
            r2 = await client.post(
                f"{BASE_URL}/sessions/start",
                headers={
                    "Authorization": f"Bearer {session_token}",
                    "Content-Type": "application/json"
                }
            )
            start = r2.json()
            logger.info(f"Start response: code={start.get('code')}")

            if start.get("code") != 1000:
                raise Exception(f"LiveAvatar start error: {start.get('message')}")

            sd = start["data"]
            ws_url = sd.get("ws_url")
            logger.info(f"✅ LITE session ready. LiveKit={sd.get('livekit_url')} WS={ws_url}")

            return {
                "session_id":    session_id,
                "session_token": session_token,
                "livekit_url":   sd.get("livekit_url"),
                "livekit_token": sd.get("livekit_client_token"),
                "ws_url":        ws_url,
                "avatar_id":     self.avatar_id,
            }

    # ──────────────────────────────────────────────
    # 2. Connect WebSocket for this session
    # ──────────────────────────────────────────────
    async def connect_websocket(self, session_id: str, ws_url: str) -> None:
        """
        Conecta el WebSocket de la sesión LITE y espera estado 'connected'.
        Lanza una tarea en background para mantener el WS vivo.
        """
        if session_id in self._ws_connections:
            logger.info(f"WS already connected for session {session_id[:8]}")
            return

        logger.info(f"🔌 Connecting WebSocket for session {session_id[:8]}...")
        ws = await websockets.connect(ws_url, ping_interval=20, ping_timeout=10)
        self._ws_connections[session_id] = ws
        self._event_counters[session_id] = 0

        # LITE mode WS is ready immediately after connect — no handshake event needed
        logger.info(f"✅ WebSocket connected for session {session_id[:8]}")

        # Background listener (logs events, handles reconnect if needed)
        task = asyncio.create_task(self._ws_listener(session_id, ws))
        self._ws_listeners[session_id] = task

    async def _ws_listener(self, session_id: str, ws) -> None:
        """Background task: escucha eventos del WebSocket."""
        try:
            async for raw in ws:
                try:
                    evt = json.loads(raw) if isinstance(raw, (str, bytes)) else {}
                    etype = evt.get("type", "")
                    if etype == "agent.speak_started":
                        logger.info(f"🔊 Avatar speak started [{session_id[:8]}]")
                    elif etype == "agent.speak_ended":
                        logger.info(f"✅ Avatar speak ended [{session_id[:8]}]")
                    elif etype == "session.state_updated":
                        logger.info(f"Session state: {evt.get('state')} [{session_id[:8]}]")
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"WS listener ended for {session_id[:8]}: {e}")
        finally:
            self._ws_connections.pop(session_id, None)
            self._ws_listeners.pop(session_id, None)

    # ──────────────────────────────────────────────
    # 3. Send audio for lip-sync
    # ──────────────────────────────────────────────
    async def speak(self, session_id: str, pcm_bytes: bytes) -> None:
        """
        Envía audio PCM 16-bit 24kHz al avatar para lip-sync.
        Si el audio es muy largo lo divide en chunks de ~1 seg (96KB).
        """
        ws = self._ws_connections.get(session_id)
        if not ws:
            raise Exception(f"No WebSocket connection for session {session_id[:8]}")

        CHUNK = 96_000  # 1 segundo de PCM 16-bit 24kHz = 48000 samples × 2 bytes
        offset = 0
        chunk_n = 0
        while offset < len(pcm_bytes):
            chunk = pcm_bytes[offset:offset + CHUNK]
            offset += CHUNK
            chunk_n += 1
            audio_b64 = base64.b64encode(chunk).decode("utf-8")
            event = {
                "type":     "agent.speak",
                "event_id": self._event_id(session_id),
                "audio":    audio_b64,
            }
            await ws.send(json.dumps(event))
            logger.debug(f"Sent audio chunk {chunk_n} ({len(chunk)} bytes) [{session_id[:8]}]")

        logger.info(f"🎙️ Sent {chunk_n} audio chunk(s) to avatar [{session_id[:8]}]")

    # ──────────────────────────────────────────────
    # 4. Interrupt avatar
    # ──────────────────────────────────────────────
    async def interrupt(self, session_id: str) -> None:
        """Detiene al avatar inmediatamente."""
        ws = self._ws_connections.get(session_id)
        if not ws:
            logger.warning(f"No WS to interrupt for {session_id[:8]}")
            return
        event = {"type": "agent.interrupt", "event_id": self._event_id(session_id)}
        await ws.send(json.dumps(event))
        logger.info(f"⏹️ Interrupted avatar [{session_id[:8]}]")

    # ──────────────────────────────────────────────
    # 5. Keep-alive
    # ──────────────────────────────────────────────
    async def keep_alive(self, session_id: str) -> None:
        ws = self._ws_connections.get(session_id)
        if not ws:
            return
        event = {"type": "session.keep_alive", "event_id": self._event_id(session_id)}
        await ws.send(json.dumps(event))
        logger.debug(f"♻️ Keep-alive sent [{session_id[:8]}]")

    # ──────────────────────────────────────────────
    # 6. Close session
    # ──────────────────────────────────────────────
    async def close_session(self, session_id: str) -> bool:
        # Cancel listener task
        task = self._ws_listeners.pop(session_id, None)
        if task:
            task.cancel()

        # Close WS
        ws = self._ws_connections.pop(session_id, None)
        if ws:
            try:
                await ws.close()
            except Exception:
                pass

        self._event_counters.pop(session_id, None)
        logger.info(f"✅ Session {session_id[:8]} closed")
        return True

    def get_avatar_config(self) -> Dict:
        return {
            "avatar_id":   self.avatar_id,
            "avatar_name": "Valeria - Asistente Legal IA",
            "service":     "liveavatar-lite",
        }

    def is_connected(self, session_id: str) -> bool:
        return session_id in self._ws_connections
