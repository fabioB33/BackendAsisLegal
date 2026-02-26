from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
# Replacement for emergentintegrations using litellm
import litellm

class UserMessage:
    def __init__(self, text: str):
        self.text = text

class LlmChat:
    def __init__(self, api_key: str, session_id: str, system_message: str = ""):
        self._api_key = api_key
        self._session_id = session_id
        self._system_message = system_message
        self._model = "openai/gpt-4o-mini"

    def with_model(self, provider: str, model: str) -> "LlmChat":
        self._model = f"{provider}/{model}"
        return self

    async def send_message(self, message: "UserMessage") -> str:
        response = await litellm.acompletion(
            model=self._model,
            api_key=self._api_key,
            messages=[
                {"role": "system", "content": self._system_message},
                {"role": "user", "content": message.text},
            ],
        )
        return response.choices[0].message.content
import aiofiles
import json
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from elevenlabs import ElevenLabs, Voice, VoiceSettings

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# Prioridad: Gemini > OpenAI > Emergent
LLM_KEY = OPENAI_API_KEY or GEMINI_API_KEY or EMERGENT_LLM_KEY
LLM_MODEL_PROVIDER = "openai" if OPENAI_API_KEY else "gemini"
LLM_MODEL_NAME = "gpt-4o-mini" if OPENAI_API_KEY else "gemini-1.5-flash"
HEYGEN_API_KEY = os.environ.get('HEYGEN_API_KEY', '')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')

# Single source of truth for voice ID — override with ELEVENLABS_VOICE_ID env var
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "saqk76H0L3GCnuHtLDw6")  # Karla — Peruvian female

# Validate critical env vars at startup — fail fast with clear message
if not LLM_KEY:
    logger.error("❌ CRITICAL: No LLM API key configured. Set GEMINI_API_KEY, OPENAI_API_KEY, or EMERGENT_LLM_KEY")

# Initialize ElevenLabs client
elevenlabs_client = None
if ELEVENLABS_API_KEY:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        logger.info("✅ ElevenLabs client initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing ElevenLabs: {e}")

# Import custom services
from services.sqlite_knowledge import SQLiteKnowledgeBase
from services.liveavatar_service import LiveAvatarService as LiveAvatarAPIService

# Initialize SQLite Knowledge Base (reemplaza MongoDB)
_db_path = str(ROOT_DIR / "prados.db")
sqlite_kb = SQLiteKnowledgeBase(db_path=_db_path)
liveavatar_service = LiveAvatarAPIService()

# Per-session locks to prevent concurrent /liveavatar/speak calls
_session_locks: dict = {}
_session_lock_times: dict = {}  # tracks last-used timestamp for cleanup

def _get_session_lock(session_id: str) -> asyncio.Lock:
    import time as _time
    if session_id not in _session_locks:
        _session_locks[session_id] = asyncio.Lock()
    _session_lock_times[session_id] = _time.monotonic()
    # Prune locks idle for more than 2 hours (browser closed without DELETE)
    cutoff = _time.monotonic() - 7200
    stale = [sid for sid, t in _session_lock_times.items() if t < cutoff]
    for sid in stale:
        _session_locks.pop(sid, None)
        _session_lock_times.pop(sid, None)
    return _session_locks[session_id]

logger.info(f"✅ SQLite Knowledge Base initialized ({sqlite_kb.count_documents()} documents)")
logger.info("✅ LiveAvatar Service initialized (liveavatar.com)")


# HeyGen Configuration
HEYGEN_API_KEY = os.environ.get('HEYGEN_API_KEY', '')
HEYGEN_AVATAR_ID = os.environ.get('HEYGEN_AVATAR_ID', '')

from contextlib import asynccontextmanager

# Documentos oficiales de la base de conocimientos — se sincronizan al startup
_KB_SEED_DOCS = [
    {
        "titulo": "Prados de Paraíso - Base de Conocimientos Oficial (Preguntas 1 a 30)",
        "marker": "Desarrolladora Santa María del Norte SAC",  # detectar si ya es la versión oficial
        "contenido": """BASE DE CONOCIMIENTOS OFICIAL - PRADOS DE PARAÍSO

1. ¿Qué es Prados de Paraíso?
Prados de Paraíso es una marca comercial de Desarrolladora Santa María del Norte SAC, dedicada a desarrollar proyectos inmobiliarios con un enfoque ecológico y sostenible. Busca innovar en el sector, combinando eficiencia ambiental, diseño funcional y calidad de vida. Responde a la demanda de estilos de vida responsables y un desarrollo inmobiliario consciente.

2. ¿Qué proyectos tiene Prados del Paraíso?
Actualmente, la marca Prados de Paraíso cuenta con dos proyectos. Uno exitosamente entregado, denominado "Prados de Paraíso – Casa Huerto Ecológico"; y el segundo proyecto: "Prados de Paraíso Villa Eco-Sostenible", el cual se encuentra en desarrollo. Ambos proyectos están respaldados por una sólida trayectoria en el mercado inmobiliario y buscan ofrecer oportunidades de inversión segura con visión de futuro.

3. ¿Dónde se ubica el proyecto Villa Eco-Sostenible?
El proyecto Villa Eco-Sostenible se encuentra ubicado a la altura del 137.25 Km de la Carretera Panamericana Norte, distrito de Santa María, Provincia de Huaura y Departamento de Lima.

4. ¿Quién desarrolla el proyecto?
El proyecto es promovido por Desarrolladora Santa María del Norte S.A.C., una empresa con experiencia en el mercado inmobiliario. Además, cuenta con el respaldo y asesoramiento legal de DS CASAHIERRO ABOGADOS y tiene un convenio con la NOTARIA TAMBINI para garantizar la transparencia y seguridad jurídica en los procesos.

5. ¿La empresa es formal?
Sí, la empresa es formal y cuenta con el respaldo de la marca Prados de Paraíso, el cual tiene una trayectoria sólida en el desarrollo de proyectos inmobiliarios. Además, se encuentra inscrita en la Partida Electrónica N° 15437655 del Registro de Personas Jurídicas de Lima.

6. ¿Desde cuándo existe el proyecto?
El proyecto "Villa Eco-Sostenible" inicia en octubre del 2023.

7. ¿Qué es exactamente lo que ofrecen?
Prados del Paraíso ofrece transferencia de posesión de lotes, lo que permite a los adquirentes disfrutar y el uso efectivo del lote. Es importante que sepas que la condición legal del predio es la posesión, no la propiedad titulada. Nuestra empresa tiene una posesión del terreno desde 1998, respaldada por escrituras públicas y reconocida por la Municipalidad de Santa María a través de cartillas municipales PR y HR. Al adquirir un lote con nosotros, formalizamos esta transferencia mediante un Contrato de Transferencia de Posesión, lo que te otorga el derecho de uso y disfrute del lote. En resumen, no solo adquieres un lote, sino una oportunidad de inversión segura y con visión de futuro, con el respaldo de una comunidad de más de 800 clientes satisfechos.

8. ¿Es lo mismo transferencia de posesión que comprar un terreno?
No, no es exactamente lo mismo, aunque en la práctica ambos te permiten usar el terreno. Comprar la Propiedad (Título de Propiedad) significa que te conviertes en el dueño legal absoluto y tu nombre aparece inscrito en los Registros Públicos (SUNARP). La Transferencia de Posesión (lo que ofrecemos) significa que adquieres el uso, disfrute y control del lote con respaldo mediante Contrato de Transferencia de Posesión y Escritura Pública, pero no se inscribe inmediatamente como propiedad en SUNARP.

9. ¿Qué diferencia hay entre posesión y propiedad?
La Propiedad es el derecho real pleno que faculta a su titular a usar, disfrutar, disponer y reivindicar el bien, otorgándole la titularidad legal absoluta inscrita en SUNARP. La Posesión es el poder de hecho que ejerces sobre el bien (uso y control físico), un derecho real reconocido por el Código Civil (Art. 896). Mientras que la propiedad es el "título" inscrito, la posesión es el "uso y control físico" del terreno.

10. ¿Puedo construir en el lote?
Sí, puedes construir en el lote, sujeto a las normativas locales y el contrato de posesión.

11. ¿La escritura me hace propietario?
No, la escritura pública de transferencia de posesión no le hace propietario en el sentido registral. Formaliza la transferencia de la posesión y le otorga un respaldo sobre ella. Para ser propietario y que su nombre aparezca en Registros Públicos, se requiere un proceso adicional de saneamiento.

12. ¿La empresa responde por el lote?
La empresa responde por el lote en el sentido de que garantiza la transferencia de la posesión del predio. Desarrolladora Santa María del Norte S.A.C. formaliza esta transferencia mediante un Contrato de Transferencia de Posesión, el cual se eleva a Escritura Pública a solicitud del cliente, otorgando el derecho de uso y disfrute del lote asignado.

13. ¿Qué planos entregarán a la firma del contrato?
Se te proporcionará plano de ubicación, memoria descriptiva y planos perimétricos.

14. ¿Cómo se respalda legalmente la posesión o qué documentos se entregan?
La empresa cuenta con documentos que respaldan su posesión desde 1998: Escrituras Públicas y Cartillas municipales (PR y HR). Al cliente se le entrega: Contrato de transferencia de posesión (documento fundamental) y Pagos de tributos municipales (PR y HR) que demuestran el cumplimiento de obligaciones fiscales.

15. ¿Cuál es el estado legal del proyecto y el proceso de adquisición?
Estado Legal: Condición de posesión respaldada por Escrituras Públicas desde 1998 y reconocimiento municipal indirecto (PR y HR). Proceso: 1. Firma del Contrato de Transferencia de Posesión. 2. Trámite Notarial (Escritura Pública). 3. Entrega física del lote para uso y disfrute.

16. ¿Qué documentos entrega la empresa al transferir la posesión?
1. Contrato de Transferencia de Posesión (elevado a Escritura Pública a solicitud). 2. Escrituras Públicas que respaldan la posesión de la empresa desde 1998. 3. Cartillas Municipales (PR y HR).

17. ¿Qué significa una transferencia de posesión?
Significa que se te otorga el uso y disfrute del predio. Se formaliza a través de un Contrato de Transferencia de Posesión elevado a Escritura Pública ante notario.

18. ¿Qué derechos tengo como poseedor?
Tiene el derecho de disponer y disfrutar del bien como si fuera suyo, ejerciendo un poder de hecho. Puede usar el lote, construir, cultivarlo o darle el uso que desee, siempre dentro de los límites legales y contractuales.

19. ¿Puedo perder mi lote?
Nuestra empresa mantiene una posesión sólida respaldada desde 1998. Al suscribir su contrato, usted adquiere por tracto sucesivo el derecho posesorio de la empresa; legalmente no sería posible que pierda su lote actuando de buena fe y cumpliendo sus obligaciones.

20. ¿DIREFOR, siendo el legítimo propietario, me puede quitar mi lote?
Aunque figura a nombre de DIREFOR en Registros Públicos, nuestra posesión es anterior a la Ley 29618 (imprescriptibilidad de predios del Estado). Esto significa que nuestra posesión es legítima y no somos invasores. Garantizamos la entrega de la posesión para su uso y disfrute.

21. Si pierdo un proceso de prescripción adquisitiva, ¿me pueden quitar mi lote?
No automáticamente. Perder la prescripción solo significa que no se acreditó la propiedad en ese momento, pero no extingue su derecho posesorio ni habilita un desalojo. Usted mantiene la posesión y el uso del lote mientras cumpla su contrato y no haya una resolución judicial firme de despojo.

22. ¿La empresa participa en el proceso de formalización o saneamiento?
No directamente. El saneamiento es un proceso personal del cliente. La empresa garantiza la posesión y entrega todo el respaldo documental (Escrituras desde 1998 y Cartillas PR/HR) para que el cliente inicie su trámite de manera independiente con su abogado.

23. ¿Existe riesgo de demanda de reivindicación o desalojo por parte de DIREFOR?
La seguridad se sustenta en una posesión efectiva desde 1998, anterior a la inscripción estatal. Una demanda de este tipo no prospera automáticamente contra una posesión antigua, pública y de buena fe. El respaldo de DS Casa Hierro Abogados y la Notaría Tambini reducen significativamente estos riesgos.

24. ¿La posesión me permite defenderme frente a terceros?
Sí. El Código Civil reconoce la posesión como un derecho real. Además, el Art. 898 permite la "suma de plazos posesorios", sumando su tiempo al de la empresa desde 1998 para fortalecer su defensa legal.

25. ¿Por qué la empresa no sanea primero el terreno?
Es una decisión estratégica para ofrecer una alternativa comercialmente viable basada en la transferencia de posesión legítima. La empresa es transparente al informar que no vende propiedad saneada, permitiendo que el adquirente decida si desea realizar el saneamiento por su cuenta posteriormente.

26. ¿Existe hoy algún juicio o problema legal activo sobre este terreno?
No existe ningún juicio, denuncia o problema legal activo. El registro a nombre de DIREFOR es por un cambio normativo (Ley 29618), no por un litigio o invasión.

27. ¿Qué respaldo real tengo si surge un problema legal mañana?
Su respaldo es el Contrato de Transferencia de Posesión y la cadena de posesión documentada de la empresa desde 1998 (Escrituras Públicas y reconocimiento municipal), lo que le otorga el derecho de uso y disfrute.

28. ¿Qué riesgos existen al adquirir por transferencia de posesión?
El riesgo principal es que no se adquiere la propiedad inscrita de forma automática. La titulación dependerá de un proceso de saneamiento personal que debe gestionar y asumir el cliente en el futuro.

29. ¿La empresa garantiza que no habrá problemas legales en el futuro?
Garantiza contractualmente la entrega de la posesión en la condición legal informada. No puede garantizar escenarios futuros externos, pero entrega una posesión debidamente respaldada para enfrentar contingencias.

30. ¿Qué obligaciones asume el adquirente?
Pagar el precio pactado, cumplir las condiciones de entrega, asumir trámites notariales de la Escritura Pública y cumplir el reglamento interno del proyecto.
""",
    },
    {
        "titulo": "Prados de Paraíso - Base de Conocimientos Oficial (Preguntas 31 a 58)",
        "marker": "Libro de Reclamaciones",  # detectar si ya es la versión oficial
        "contenido": """BASE DE CONOCIMIENTOS OFICIAL - PRADOS DE PARAÍSO (CONTINUACIÓN)

31. ¿Se paga algún impuesto por la transferencia?
El adquirente puede asumir el impuesto predial una vez entregada la posesión. Estos tributos se gestionan sobre el predio matriz mientras no haya individualización por lote.

32. ¿El contrato contempla cláusulas de saneamiento posesorio?
No. Está estructurado para garantizar la entrega de la posesión, no para ejecutar el saneamiento de la propiedad.

33. ¿La empresa ha evaluado iniciar el proceso de prescripción adquisitiva?
Es una decisión estratégica. Actualmente la empresa no ofrece la prescripción como parte del proyecto; su actividad es la transferencia de posesión. La obtención del título es un proceso que el adquirente debe asumir de forma personal.

34. ¿La transferencia de posesión podría considerarse simulación de compraventa?
No. Son actos distintos. En Prados de Paraíso hay transparencia total: el contrato especifica que se transfiere posesión (uso y disfrute) y no propiedad. No hay engaño, por lo que no existe simulación.

35. ¿Cómo se gestiona la formalización futura?
Mediante saneamiento físico-legal (como prescripción adquisitiva judicial). Es un trámite personal del adquirente tras recibir el lote. La empresa facilita toda la documentación histórica para este fin.

36. ¿Qué obligaciones mantiene la empresa luego de la transferencia?
Entregar la posesión en la condición informada, proporcionar la documentación posesoria de sustento y cumplir cualquier otra obligación pendiente en el contrato.

37. ¿La empresa mantiene la administración de áreas recreativas?
Asume la gestión inicial. Posteriormente, la administración puede pasar a una asociación de propietarios según el reglamento interno.

38. ¿Existen contingencias penales?
No. El modelo se basa en la transferencia de posesión, figura reconocida legalmente y respaldada por escrituras públicas y transparencia notarial.

39. ¿Qué respaldo real tiene el cliente si surge un conflicto?
1. Posesión histórica desde 1998. 2. Asesoría de DS Casahierro Abogados y Notaría Tambini. 3. Entrega de toda la documentación probatoria para defensa o saneamiento.

40. ¿Qué es DIREFOR y por qué figura como propietario?
Es una entidad estatal. Aparece como titular debido a la Ley 29618 (2010), que registró a nombre del Estado terrenos sin dueño inscrito. Esto no invalida la posesión legítima de la empresa iniciada en 1998.

41. ¿Es legal transferir la posesión de un terreno del Estado?
Sí. La ley peruana protege la posesión como situación jurídica distinta a la propiedad. Se transfiere el derecho de posesión histórica (anterior a la inscripción estatal), lo cual es totalmente lícito.

42. ¿Qué sucede si se revierte la posesión al Estado?
No hay procesos activos para ello. La inscripción de DIREFOR no implica pérdida automática de la posesión documentada que se ejerce desde 1998.

43. ¿La municipalidad reconoce oficialmente el proyecto?
Sí, de manera indirecta mediante la emisión de cartillas PR y HR a nombre de la empresa, lo que permite el pago de tributos y valida la actividad en el predio.

44. ¿Cómo impacta la ley que prohíbe la prescripción contra el Estado?
La Ley 29618 impide nuevas prescripciones desde 2010, pero no invalida posesiones históricas preexistentes. Como nuestra posesión data de 1998, mantiene su legitimidad para ser transferida a los clientes.

45. ¿La empresa acompaña judicialmente al cliente?
La representación legal en procesos judiciales corresponde al cliente y su abogado. La empresa proporciona toda la documentación probatoria necesaria para respaldar la defensa.

46. ¿La empresa indemnizará en caso de pérdida de posesión?
La empresa no tiene una política de indemnización por causas externas. Su compromiso es entregar la posesión respaldada por documentos históricos para que el cliente la ejerza y defienda.

47. ¿Se puede individualizar la posesión por cada lote?
Sí. El contrato delimita y asigna el derecho de uso y disfrute exclusivo sobre un lote específico, otorgando control físico total al adquirente sobre ese espacio.

48. ¿El adquirente podría ser demandado por el Estado?
Podría ser parte involucrada, pero su defensa es sólida al contar con el respaldo de la posesión histórica desde 1998 y escrituras públicas que garantizan su inversión.

49. ¿Qué pasa si el proyecto no logra consolidarse?
Usted seguirá manteniendo la posesión, uso y disfrute de su lote específico basado en la antigüedad de la posesión transferida.

50. ¿El contrato me protege frente a cualquier contingencia?
Regula la transferencia y pagos, asegurando la entrega física y documental. No cubre litigios externos futuros con terceros o el Estado fuera del control de la empresa.

51. ¿La empresa responde económicamente frente a la pérdida de posesión?
No asume responsabilidad económica por hechos externos ajenos a su incumplimiento contractual. El respaldo es documental y legal sobre la posesión entregada.

52. ¿Las cartillas PR y HR están a nombre de mi lote específico?
Se emiten a nombre de la empresa por el predio matriz. Sirven como respaldo de posesión general del proyecto mientras no haya individualización administrativa.

53. ¿Mi lote tendrá su propia cartilla municipal?
Inicialmente no, pero la empresa se compromete a realizar el trámite de Individualización Administrativa ante la Municipalidad para que cada lote cuente con su propia documentación.

54. ¿La empresa tiene Libro de Reclamaciones?
Sí. Físico en Calle Libertadores 155, Of. 302, San Isidro. Virtual en: https://pradosdeparaiso.com.pe/

55. ¿Qué pasa si no estoy conforme con la respuesta de la empresa?
En caso de que no estés conforme con la respuesta inicial, siempre existe la posibilidad de continuar el diálogo a través de los canales internos. La empresa prioriza la atención y resolución directa de los reclamos. Solo si, luego de agotar estas vías internas, el reclamo no resulta satisfactorio, el consumidor mantiene su derecho de recurrir a los organismos de protección al consumidor conforme a la normativa vigente.

56. ¿Cuáles son los plazos de atención de un reclamo?
Conforme al Reglamento de Libro de Reclamaciones y su modificatoria, el plazo máximo para atender un reclamo es de 15 días hábiles improrrogables.

57. ¿La empresa se responsabiliza por daños externos?
La empresa no asume responsabilidad por daños ocasionados por factores externos fuera de su control, tales como desastres naturales, actos de terceros o decisiones de autoridades. La responsabilidad se limita a cumplir las obligaciones expresamente asumidas en el contrato.

58. Si la empresa deja de pagar la deuda pendiente con el señor Manuel Ampuero, ¿Eso podría hacer que yo pierda mi lote o mi derecho de posesión?
No. Desde la suscripción de la Escritura Pública por la que el señor Manuel Ampuero transfirió la posesión a favor de Desarrolladora Santa María del Norte, la empresa adquirió válidamente la posesión efectiva del terreno. Esta condición no se ve afectada por las obligaciones internas entre las partes originales. Aun en el supuesto de que la empresa incumpliera algún pago, ello no genera la pérdida ni afectación de la posesión ya transferida formalmente mediante escritura pública. Por lo tanto, no existe riesgo alguno para el cliente.
""",
    },
]

def _seed_knowledge_base():
    """Sincroniza los documentos oficiales al startup. Actualiza o inserta según título."""
    try:
        import sqlite3 as _sqlite3
        with _sqlite3.connect(_db_path) as conn:
            cursor = conn.cursor()
            for doc in _KB_SEED_DOCS:
                cursor.execute("SELECT id, contenido FROM conocimiento_legal WHERE titulo = ?", (doc["titulo"],))
                row = cursor.fetchone()
                needs_update = row is None or doc["marker"] not in row[1]
                if needs_update:
                    if row:
                        cursor.execute("UPDATE conocimiento_legal SET contenido = ? WHERE id = ?",
                                       (doc["contenido"], row[0]))
                        logger.info(f"✅ KB actualizado: '{doc['titulo'][:50]}...'")
                    else:
                        cursor.execute("INSERT INTO conocimiento_legal (titulo, contenido) VALUES (?, ?)",
                                       (doc["titulo"], doc["contenido"]))
                        logger.info(f"✅ KB insertado: '{doc['titulo'][:50]}...'")
                else:
                    logger.info(f"✅ KB OK: '{doc['titulo'][:50]}...'")
            # Eliminar el doc viejo con título genérico si existe
            cursor.execute("DELETE FROM conocimiento_legal WHERE titulo = 'Condiciones Legales de Prados de Paraíso'")
            conn.commit()
    except Exception as e:
        logger.error(f"Error en _seed_knowledge_base: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — asegurar que el documento principal tenga el contenido correcto
    _seed_knowledge_base()
    logger.info("✅ Application started successfully")
    yield
    # Shutdown — properly close MongoDB async connection
    logger.info("🛑 Shutting down — closing MongoDB connection...")
    client.close()
    logger.info("✅ MongoDB connection closed")

app = FastAPI(lifespan=lifespan)

# ⚠️ CONFIGURACIÓN CRÍTICA DE CORS
origins = [
    "https://legbotdev.pradosdeparaiso.com.pe",       # Dominio de producción
    "https://frontendAsisLegal.onrender.com",          # Frontend en Render
    "https://frontendasislegal.onrender.com",          # Frontend en Render (lowercase)
    "https://verdant-paletas-4473ea.netlify.app",      # Frontend en Netlify
    "https://frontend-asis-legal.vercel.app",          # Frontend en Vercel
    "http://localhost:3000",                           # Desarrollo local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

api_router = APIRouter(prefix="/api")

# Información legal de Prados de Paraíso (usada como fallback en endpoints secundarios)
LEGAL_INFO = """
PRADOS DE PARAÍSO — Proyecto inmobiliario en Pachacamac, Lima, Perú.
Respaldado por Notaría Tambini y Casahierro Abogados.

1. CONDICIÓN LEGAL DEL TERRENO:
- 50% del terreno: Propiedad adquirida mediante compraventa de acciones y derechos, con escrituras públicas desde 1998.
- 50% restante: Posesión legítima y mediata de buena fe, ejercida continuamente desde 1998.
- El predio figura a nombre de DIREFOR (entidad estatal), pero la empresa posee legítimamente desde hace más de 25 años.

2. QUÉ RECIBE EL COMPRADOR:
Contrato de transferencia de POSESIÓN (no título de propiedad en primera instancia).
Para obtener el título inscrito en SUNARP el propietario gestiona el saneamiento legal al completar el pago total.

3. PREGUNTAS FRECUENTES:

Q: ¿Cuándo entregan el título de propiedad?
R: Al comprar se entrega contrato de transferencia de posesión. El título SUNARP se obtiene gestionando el saneamiento legal tras completar el pago. El equipo legal acompaña ese proceso.

Q: ¿Tienen partida registral en SUNARP?
R: No a nombre de la desarrolladora. El predio figura a nombre de DIREFOR. Esto no representa riesgo porque poseemos legítimamente desde 1998, respaldados por escrituras públicas notariales.

Q: ¿Es seguro comprar sin partida registral?
R: Sí. La posesión legítima de más de 25 años con escrituras públicas desde 1998 es un derecho real protegido por la ley peruana. El respaldo es Notaría Tambini y Casahierro Abogados.

Q: ¿Puedo construir en el terreno con posesión?
R: Sí. El poseedor legítimo tiene todos los derechos de uso, disfrute y construcción sobre el terreno.

Q: ¿Puedo revender el lote?
R: Sí, el contrato de posesión es transferible. Se recomienda completar el saneamiento primero para obtener mejor precio.

Q: ¿Tipos de posesión?
R: Legítima (mediata e inmediata) e Ilegítima (buena fe, mala fe, precaria). Prados de Paraíso: Posesión Legítima Mediata de Buena Fe — la categoría más sólida.

4. PROCESO DE COMPRA:
1. Separación del lote con pago inicial
2. Verificación de documentos legales
3. Firma de contrato de transferencia de posesión
4. Pago en cuotas según plan acordado
5. Gestión de saneamiento para título SUNARP al completar pago
6. Inscripción definitiva en Registros Públicos
"""

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    role: str = "seller"  # seller, client, admin
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    name: str
    role: str = "seller"

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    role: str  # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageCreate(BaseModel):
    conversation_id: str
    content: str

class Conversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0

class ConversationCreate(BaseModel):
    user_id: str
    user_name: str
    title: str = "Nueva Consulta"

class Document(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    filename: str
    content: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Helper function
def prepare_for_mongo(data: dict) -> dict:
    '''Convert datetime objects to ISO strings for MongoDB'''
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data

# Routes
@api_router.get("/")
async def root():
    return {"message": "Prados de Paraíso Legal Hub API"}

# User routes
@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_obj = User(**user.model_dump())
    doc = prepare_for_mongo(user_obj.model_dump())
    await db.users.insert_one(doc)
    return user_obj

@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find({}, {"_id": 0}).to_list(1000)
    for user in users:
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
    return users

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if isinstance(user.get('created_at'), str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    return user

# Conversation routes
@api_router.post("/conversations", response_model=Conversation)
async def create_conversation(conv: ConversationCreate):
    conv_obj = Conversation(**conv.model_dump())
    doc = prepare_for_mongo(conv_obj.model_dump())
    await db.conversations.insert_one(doc)
    return conv_obj

@api_router.get("/conversations/user/{user_id}", response_model=List[Conversation])
async def get_user_conversations(user_id: str):
    conversations = await db.conversations.find(
        {"user_id": user_id}, 
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)
    
    for conv in conversations:
        for field in ['created_at', 'updated_at']:
            if isinstance(conv.get(field), str):
                conv[field] = datetime.fromisoformat(conv[field])
    return conversations

@api_router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    conv = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    for field in ['created_at', 'updated_at']:
        if isinstance(conv.get(field), str):
            conv[field] = datetime.fromisoformat(conv[field])
    return conv

# Message routes
@api_router.post("/messages", response_model=Message)
async def create_message_endpoint(msg: MessageCreate):
    try:
        # Create user message
        user_msg = Message(
            conversation_id=msg.conversation_id,
            role="user",
            content=msg.content
        )
        doc = prepare_for_mongo(user_msg.model_dump())
        await db.messages.insert_one(doc)
        
        # Get conversation context
        messages = await db.messages.find(
            {"conversation_id": msg.conversation_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(50)
        
        # Generate AI response
        system_prompt = f'''Eres un asistente legal experto en Prados de Paraíso. 
Tu trabajo es responder preguntas sobre condiciones legales, propiedad, posesión y saneamiento.

Información legal disponible:
{LEGAL_INFO}

Responde de manera profesional, clara y precisa. Si no tienes información específica, 
indica que el usuario debe consultar con el equipo legal.'''
        
        chat = LlmChat(
            api_key=LLM_KEY,
            session_id=msg.conversation_id,
            system_message=system_prompt
        ).with_model(LLM_MODEL_PROVIDER, LLM_MODEL_NAME)
        
        user_message = UserMessage(text=msg.content)
        ai_response = await chat.send_message(user_message)
        
        # Create assistant message
        assistant_msg = Message(
            conversation_id=msg.conversation_id,
            role="assistant",
            content=ai_response
        )
        doc = prepare_for_mongo(assistant_msg.model_dump())
        await db.messages.insert_one(doc)
        
        # Update conversation
        await db.conversations.update_one(
            {"id": msg.conversation_id},
            {
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()},
                "$inc": {"message_count": 2}
            }
        )
        
        return assistant_msg
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/messages/{conversation_id}", response_model=List[Message])
async def get_messages(conversation_id: str):
    import uuid as _uuid
    try:
        _uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="conversation_id inválido")
    messages = await db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    for msg in messages:
        if isinstance(msg.get('timestamp'), str):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
    return messages

# Document routes
@api_router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    try:
        # Validate MIME type — only accept text/plain, text/markdown, application/pdf
        ALLOWED_MIME = {"text/plain", "text/markdown", "application/pdf", "text/csv"}
        ct = (file.content_type or "").split(";")[0].strip().lower()
        if ct and ct not in ALLOWED_MIME:
            raise HTTPException(status_code=415, detail=f"Tipo de archivo no permitido: {ct}")
        # Read with size limit — reject files larger than 5 MB
        MAX_UPLOAD_BYTES = 5 * 1024 * 1024
        content = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="El archivo supera el límite de 5 MB")
        content_str = content.decode('utf-8', errors='ignore')

        safe_filename = Path(file.filename).name if file.filename else "upload"
        doc = Document(
            user_id=user_id,
            filename=safe_filename,
            content=content_str[:10000]  # Limit size
        )
        doc_dict = prepare_for_mongo(doc.model_dump())
        await db.documents.insert_one(doc_dict)

        return {"success": True, "document_id": doc.id, "filename": safe_filename}
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/documents/user/{user_id}")
async def get_user_documents(user_id: str):
    docs = await db.documents.find(
        {"user_id": user_id},
        {"_id": 0, "content": 0}
    ).sort("uploaded_at", -1).to_list(100)
    
    for doc in docs:
        if isinstance(doc.get('uploaded_at'), str):
            doc['uploaded_at'] = datetime.fromisoformat(doc['uploaded_at'])
    return docs

# Analytics routes
@api_router.get("/analytics/overview")
async def get_analytics(x_admin_key: Optional[str] = None):
    _admin_key = os.environ.get("ADMIN_API_KEY", "")
    if _admin_key and x_admin_key != _admin_key:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    try:
        total_users = await db.users.count_documents({})
        total_conversations = await db.conversations.count_documents({})
        total_messages = await db.messages.count_documents({})
        total_documents = await db.documents.count_documents({})
        
        # Get recent activity
        recent_convs = await db.conversations.find(
            {},
            {"_id": 0}
        ).sort("updated_at", -1).limit(10).to_list(10)
        
        return {
            "total_users": total_users,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_documents": total_documents,
            "recent_activity": recent_convs
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Export conversation to PDF
@api_router.get("/conversations/{conversation_id}/export")
async def export_conversation(conversation_id: str):
    try:
        # Get conversation
        conv = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
        if not conv:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        # Get messages
        messages = await db.messages.find(
            {"conversation_id": conversation_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(1000)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph(f"<b>{conv.get('title', 'Conversación')}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Messages
        for msg in messages:
            role = "Usuario" if msg['role'] == 'user' else "Asistente"
            timestamp = msg.get('timestamp', '')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            msg_text = f"<b>{role}</b> - {timestamp.strftime('%Y-%m-%d %H:%M')}<br/>{msg['content']}"
            p = Paragraph(msg_text, styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 12))
        
        doc.build(story)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=conversacion_{conversation_id}.pdf"}
        )
    except Exception as e:
        logger.error(f"Error exporting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Search conversations
@api_router.get("/search")
async def search_conversations(q: str, user_id: Optional[str] = None):
    try:
        import re as _re
        # Escape regex special chars to prevent ReDoS
        safe_q = _re.escape(q[:200]) if q else ""
        if not safe_q:
            return {"conversations": [], "message_matches": 0}
        query = {"content": {"$regex": safe_q, "$options": "i"}}
        messages = await db.messages.find(query, {"_id": 0}).limit(50).to_list(50)
        
        # Get unique conversation IDs
        conv_ids = list(set(msg['conversation_id'] for msg in messages))
        
        # Get conversations
        conv_query = {"id": {"$in": conv_ids}}
        if user_id:
            conv_query["user_id"] = user_id
        
        conversations = await db.conversations.find(
            conv_query,
            {"_id": 0}
        ).to_list(50)
        
        return {
            "conversations": conversations,
            "message_matches": len(messages)
        }
    except Exception as e:
        logger.error(f"Error searching: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Text-to-Speech with ElevenLabs
@api_router.post("/tts")
async def text_to_speech(request: dict):
    '''Convert text to speech using ElevenLabs'''
    try:
        if not elevenlabs_client:
            raise HTTPException(status_code=503, detail="ElevenLabs not configured")
        
        text = request.get('text', '')
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Generate audio using ElevenLabs with streaming
        # Using Lina - Warm Latin American female voice (Colombian accent, works well for Peruvian Spanish)
        audio_stream = elevenlabs_client.text_to_speech.stream(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.6,
                similarity_boost=0.8,
                style=0.0,
                use_speaker_boost=True
            )
        )

        # Collect audio bytes from stream
        audio_bytes = b""
        for chunk in audio_stream:
            audio_bytes += chunk

        # Return base64 encoded audio
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        return {
            "audio": audio_base64,
            "format": "mp3"
        }
        
    except Exception as e:
        logger.error(f"Error in TTS: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Voice Chat Endpoint (Push-to-Talk)
@api_router.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):
    '''
    Complete voice chat flow:
    1. Transcribe audio using ElevenLabs STT
    2. Get AI response using LLM
    3. Convert response to speech using ElevenLabs TTS
    '''
    try:
        if not elevenlabs_client:
            raise HTTPException(status_code=503, detail="ElevenLabs not configured")
        
        if not LLM_KEY:
            raise HTTPException(status_code=503, detail="LLM not configured")
        
        # Step 1: Transcribe audio to text using ElevenLabs STT
        logger.info("📝 Transcribing audio...")
        audio_content = await audio.read()
        
        transcription_response = elevenlabs_client.speech_to_text.convert(
            file=io.BytesIO(audio_content),
            model_id="scribe_v1"
        )
        
        # Extract transcribed text
        transcribed_text = transcription_response.text if hasattr(transcription_response, 'text') else str(transcription_response)
        logger.info(f"✅ Transcribed: {transcribed_text}")
        
        if not transcribed_text or len(transcribed_text.strip()) == 0:
            raise HTTPException(status_code=400, detail="No se pudo transcribir el audio. Intenta hablar más claro.")
        
        # Step 2: Get AI response
        logger.info("🤖 Generating AI response...")
        system_prompt = f'''Eres un asistente legal experto en Prados de Paraíso. 
Tu trabajo es responder preguntas sobre condiciones legales, propiedad, posesión y saneamiento.

Información legal disponible:
{LEGAL_INFO}

Responde de manera profesional, clara, concisa y precisa. Mantén las respuestas breves (máximo 3-4 frases) 
ya que serán convertidas a voz. Si no tienes información específica, indica que el usuario debe consultar 
con el equipo legal.'''
        
        chat = LlmChat(
            api_key=LLM_KEY,
            session_id="voice_chat_" + str(uuid.uuid4()),
            system_message=system_prompt
        ).with_model(LLM_MODEL_PROVIDER, LLM_MODEL_NAME)
        
        user_message = UserMessage(text=transcribed_text)
        ai_response = await chat.send_message(user_message)
        logger.info(f"✅ AI Response: {ai_response[:100]}...")
        
        # Step 3: Convert AI response to speech
        logger.info("🔊 Converting response to speech...")
        audio_stream = elevenlabs_client.text_to_speech.stream(
            text=ai_response,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.6,
                similarity_boost=0.8,
                style=0.0,
                use_speaker_boost=True
            )
        )

        # Collect audio bytes from stream
        audio_bytes = b""
        for chunk in audio_stream:
            audio_bytes += chunk

        # Return base64 encoded audio
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        logger.info("✅ Voice chat completed successfully")
        
        return {
            "transcribed_text": transcribed_text,
            "ai_response": ai_response,
            "audio_url": f"data:audio/mpeg;base64,{audio_base64}",
            "format": "mp3"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in voice chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error procesando consulta de voz: {str(e)}")

# Text Chat Endpoint (alternative to voice)
@api_router.post("/text-chat")
async def text_chat(request: dict):
    '''
    Text-based chat flow (alternative to voice):
    1. Get user text input
    2. Get AI response using LLM
    3. Convert response to speech using ElevenLabs TTS (optional)
    '''
    try:
        if not LLM_KEY:
            raise HTTPException(status_code=503, detail="LLM not configured")
        
        text = request.get('text', '').strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        if len(text) > 2000:
            raise HTTPException(status_code=400, detail="El texto no puede superar 2000 caracteres")
        
        logger.info(f"💬 Text chat request: {text}")
        
        # Get AI response
        system_prompt = f'''Eres un asistente legal experto en Prados de Paraíso. 
Tu trabajo es responder preguntas sobre condiciones legales, propiedad, posesión y saneamiento.

Información legal disponible:
{LEGAL_INFO}

Responde de manera profesional, clara y precisa. Si no tienes información específica, 
indica que el usuario debe consultar con el equipo legal.'''
        
        chat = LlmChat(
            api_key=LLM_KEY,
            session_id="text_chat_" + str(uuid.uuid4()),
            system_message=system_prompt
        ).with_model(LLM_MODEL_PROVIDER, LLM_MODEL_NAME)
        
        user_message = UserMessage(text=text)
        ai_response = await chat.send_message(user_message)
        logger.info(f"✅ AI Response generated")
        
        # Optionally convert to speech if ElevenLabs is available
        audio_url = None
        if elevenlabs_client:
            try:
                logger.info(f"🔊 Converting response to speech (streaming mode)...")
                audio_stream = elevenlabs_client.text_to_speech.stream(
                    text=ai_response,
                    voice_id=ELEVENLABS_VOICE_ID,
                    model_id="eleven_multilingual_v2",
                    voice_settings=VoiceSettings(
                        stability=0.6,
                        similarity_boost=0.8,
                        style=0.0,
                        use_speaker_boost=True
                    )
                )
                
                audio_bytes = b""
                for chunk in audio_stream:
                    audio_bytes += chunk
                
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                audio_url = f"data:audio/mpeg;base64,{audio_base64}"
                logger.info("Audio generated")
            except Exception as e:
                logger.warning(f"Could not generate audio: {str(e)}")
        
        return {
            "user_text": text,
            "ai_response": ai_response,
            "audio_url": audio_url,
            "format": "mp3" if audio_url else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")


# HeyGen Streaming Avatar Endpoints
@api_router.post("/heygen/streaming-token")
async def create_heygen_streaming_token():
    """
    Generate a session token for HeyGen Streaming Avatar.
    This token is used by the frontend SDK to establish a WebRTC connection.
    """
    try:
        if not HEYGEN_API_KEY:
            raise HTTPException(status_code=503, detail="HeyGen API key not configured")
        
        import httpx
        
        logger.info("🎬 Creating HeyGen streaming session token...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.heygen.com/v1/streaming.create_token",
                headers={
                    "x-api-key": HEYGEN_API_KEY,
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"❌ HeyGen token creation failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"HeyGen API error: {response.text}"
                )
            
            data = response.json()
            token = data.get("data", {}).get("token")
            
            if not token:
                logger.error(f"❌ No token in response: {data}")
                raise HTTPException(status_code=500, detail="No token returned from HeyGen")
            
            logger.info("✅ HeyGen streaming token created successfully")
            
            return {
                "token": token,
                "avatar_id": HEYGEN_AVATAR_ID
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating HeyGen token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating streaming token: {str(e)}")


# Voice Agent Endpoint (using ElevenLabs Agent voice and knowledge)
@api_router.post("/voice-agent")
async def voice_agent(audio: UploadFile = File(...), agent_id: str = Form(...)):
    '''
    Send audio to get response using the ElevenLabs Agent configured voice.
    This endpoint:
    1. Transcribes user audio (STT)
    2. Gets agent configuration (voice, personality)
    3. Generates response using agent knowledge base context
    4. Converts to speech using agent voice (TTS)
    '''
    try:
        if not elevenlabs_client:
            raise HTTPException(status_code=503, detail="ElevenLabs not configured")
        
        if not LLM_KEY:
            raise HTTPException(status_code=503, detail="LLM not configured")
        
        logger.info(f"🎙️ Processing voice with agent: {agent_id}")
        
        # Step 1: Transcribe audio
        audio_content = await audio.read()
        transcription_response = elevenlabs_client.speech_to_text.convert(
            file=io.BytesIO(audio_content),
            model_id="scribe_v1"
        )
        
        transcribed_text = transcription_response.text if hasattr(transcription_response, 'text') else str(transcription_response)
        logger.info(f"✅ Transcribed: {transcribed_text}")
        
        if not transcribed_text or len(transcribed_text.strip()) == 0:
            raise HTTPException(status_code=400, detail="No se pudo transcribir el audio.")
        
        # Step 2: Get agent details to use the correct voice
        agent_voice_id = "saqk76H0L3GCnuHtLDw6"  # Karla - Peruvian female voice
        agent_name = "Doctor Prados de Paraiso"
        
        try:
            # Try to get agent details to confirm voice
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.elevenlabs.io/v1/convai/agents/{agent_id}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY},
                    timeout=5.0
                )
                if response.status_code == 200:
                    agent_data = response.json()
                    if 'conversation_config' in agent_data:
                        tts_config = agent_data.get('conversation_config', {}).get('tts', {})
                        if 'voice_id' in tts_config:
                            agent_voice_id = tts_config['voice_id']
                            logger.info(f"✅ Using agent voice: {agent_voice_id}")
                        agent_name = agent_data.get('name', agent_name)
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch agent details: {str(e)}, using default Dr. Prados voice")
        
        # Step 3: Generate AI response using the knowledge base context
        system_prompt = f'''Eres {agent_name}, un asistente legal experto especializado en Prados de Paraíso.
Tu trabajo es responder preguntas sobre condiciones legales, propiedad, posesión y saneamiento del proyecto.

Información legal disponible:
{LEGAL_INFO}

Responde de manera profesional, clara, concisa y amigable como lo haría el Dr. Prados.
Mantén las respuestas breves (máximo 3-4 frases) ya que serán convertidas a voz.'''
        
        chat = LlmChat(
            api_key=LLM_KEY,
            session_id=f"agent_{agent_id}_{uuid.uuid4()}",
            system_message=system_prompt
        ).with_model(LLM_MODEL_PROVIDER, LLM_MODEL_NAME)
        
        user_message = UserMessage(text=transcribed_text)
        ai_response = await chat.send_message(user_message)
        logger.info(f"✅ AI Response generated")
        
        # Step 4: Convert to speech using agent's voice (fallback to ELEVENLABS_VOICE_ID)
        audio_stream = elevenlabs_client.text_to_speech.stream(
            text=ai_response,
            voice_id=agent_voice_id or ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
        )
        
        audio_bytes = b""
        for chunk in audio_stream:
            audio_bytes += chunk
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        logger.info("✅ Voice agent response completed")
        
        return {
            "transcribed_text": transcribed_text,
            "agent_response": ai_response,
            "audio_url": f"data:audio/mpeg;base64,{audio_base64}",
            "format": "mp3",
            "voice_used": agent_voice_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in voice agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")


# WebSocket for real-time chat
@api_router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Create user message
            user_msg = Message(
                conversation_id=conversation_id,
                role="user",
                content=message_data['content']
            )
            doc = prepare_for_mongo(user_msg.model_dump())
            await db.messages.insert_one(doc)
            
            # Send user message confirmation
            await websocket.send_json(user_msg.model_dump(mode='json'))
            
            # Generate AI response
            system_prompt = f'''Eres un asistente legal experto en Prados de Paraíso.

Información legal:
{LEGAL_INFO}

Responde de manera profesional y clara.'''
            
            chat = LlmChat(
                api_key=LLM_KEY,
                session_id=conversation_id,
                system_message=system_prompt
            ).with_model(LLM_MODEL_PROVIDER, LLM_MODEL_NAME)
            
            user_message = UserMessage(text=message_data['content'])
            ai_response = await chat.send_message(user_message)
            
            # Create assistant message
            assistant_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=ai_response
            )
            doc = prepare_for_mongo(assistant_msg.model_dump())
            await db.messages.insert_one(doc)
            
            # Send assistant message
            await websocket.send_json(assistant_msg.model_dump(mode='json'))
            
            # Update conversation
            await db.conversations.update_one(
                {"id": conversation_id},
                {
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()},
                    "$inc": {"message_count": 2}
                }
            )
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

# ============================================================================
# LIVE AVATAR LITE MODE ENDPOINTS
# STT (ElevenLabs) → LLM (Gemini) → TTS PCM (ElevenLabs) → avatar lip-sync
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class SpeakRequest(BaseModel):
    session_id: str
    audio_base64: str          # audio grabado por el frontend (webm/opus)
    conversation_id: Optional[str] = None

class InterruptRequest(BaseModel):
    session_id: str

class TextSpeakRequest(BaseModel):
    session_id: str
    text: str
    conversation_id: Optional[str] = None

VALERIA_SYSTEM = '''Eres Valeria, asistente legal de Prados de Paraíso, proyecto inmobiliario en Pachacamac, Lima, Perú.

Tu función es responder las dudas legales de clientes potenciales que están considerando comprar un lote. Tu objetivo es generar confianza y resolver inquietudes sobre la condición legal del proyecto de manera clara y tranquilizadora, siempre con fundamento real.

REGLA ABSOLUTA DE CONOCIMIENTO: Basá SIEMPRE tus respuestas en la BASE DE CONOCIMIENTOS PRINCIPAL que se te proporciona. Esa es la fuente oficial y única del proyecto. NO uses conocimiento genérico sobre derecho inmobiliario si contradice o va más allá de lo que dice la base de conocimientos.

REGLA ABSOLUTA DE FORMATO: Responde SIEMPRE en exactamente 3 a 5 oraciones cortas. Ni una más. Tus respuestas se convierten a audio, así que deben ser breves y fluidas.

FORMATO OBLIGATORIO:
- Texto plano continuo, sin listas, sin guiones, sin asteriscos, sin numeraciones, sin títulos.
- Solo oraciones completas separadas por punto.
- Tono cálido, profesional y tranquilizador, como una llamada telefónica de confianza.
- Español peruano natural. Evitá tecnicismos innecesarios; si usás términos legales, explicalos en la misma oración.

DATOS CLAVE DEL PROYECTO (siempre válidos):
- El comprador recibe un contrato de transferencia de posesión (no título directo). El título SUNARP se gestiona al completar el pago.
- No hay partida registral a nombre de la desarrolladora (el predio está a nombre de DIREFOR, entidad estatal). Esto es legal y no representa riesgo.
- La posesión es legítima, mediata y de buena fe desde 1998, respaldada por escrituras públicas y Notaría Tambini.
- Si el cliente pregunta sobre precios o condiciones de pago, indicá que debe consultar con el equipo de ventas.

Si no encontrás información específica en la base de conocimientos, respondé con lo que sabés del proyecto en máximo 3 oraciones y ofrecé derivar al equipo legal o de ventas.
'''

def _truncate_to_sentences(text: str, max_sentences: int = 5) -> str:
    """Corta el texto a un máximo de N oraciones completas."""
    import re
    # Dividir por punto seguido de espacio o fin de línea
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filtrar oraciones vacías o muy cortas (artefactos)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    trimmed = " ".join(sentences[:max_sentences])
    # Asegurar que termina con punto
    if trimmed and trimmed[-1] not in ".!?":
        trimmed += "."
    return trimmed


def _extract_relevant_chunks(doc_content: str, query: str, max_chars: int = 3000) -> str:
    """Extrae los párrafos/preguntas más relevantes de un documento según la query."""
    import re
    # Dividir por bloques (preguntas numeradas o párrafos dobles)
    blocks = re.split(r'\n(?=\d+[\.\)]|\n)', doc_content)
    query_words = set(w.lower() for w in query.split() if len(w) >= 3)

    scored = []
    for block in blocks:
        if not block.strip():
            continue
        block_lower = block.lower()
        score = sum(1 for w in query_words if w in block_lower)
        scored.append((score, block.strip()))

    # Ordenar por relevancia, luego tomar los mejores hasta max_chars
    scored.sort(key=lambda x: x[0], reverse=True)
    result_parts = []
    total = 0
    for score, block in scored:
        if total + len(block) > max_chars:
            break
        result_parts.append(block)
        total += len(block)

    # Si no hay nada relevante, tomar los primeros 3000 chars del doc
    if not result_parts:
        return doc_content[:max_chars]

    return "\n\n".join(result_parts)


async def _build_valeria_response(user_text: str, conversation_id: str) -> str:
    """STT ya hecho. Búsqueda semántica + LLM → texto de respuesta."""
    import re

    all_docs = sqlite_kb.get_all_documents_full()
    relevant_docs = sqlite_kb.search(query=user_text, top_k=3)

    MAIN_DOC_PREFIX = "Prados de Paraíso - Base de Conocimientos Oficial"
    context_parts = []
    seen_ids = set()

    # 1. Documentos oficiales — extraer solo los chunks relevantes (máx 3000 chars c/u)
    main_docs = [d for d in all_docs if MAIN_DOC_PREFIX in d.get('titulo', '')]
    for doc in main_docs:
        seen_ids.add(doc['id'])
        chunk = _extract_relevant_chunks(doc['contenido'], user_text, max_chars=3000)
        clean = re.sub(r'\*+', '', chunk)
        context_parts.append(f"BASE DE CONOCIMIENTOS OFICIAL ({doc['titulo']}):\n{clean}")

    # 2. Docs relevantes adicionales (no oficiales), truncados a 1500 chars
    for doc in relevant_docs:
        if doc['id'] in seen_ids:
            continue
        seen_ids.add(doc['id'])
        clean = re.sub(r'\*+', '', doc['contenido'])[:1500]
        context_parts.append(f"Información adicional ({doc['titulo']}):\n{clean}")

    context = "\n\n".join(context_parts) if context_parts else "Usa tu conocimiento general sobre el proyecto."

    try:
        response = await litellm.acompletion(
            model=f"{LLM_MODEL_PROVIDER}/{LLM_MODEL_NAME}",
            api_key=LLM_KEY,
            max_tokens=220,
            messages=[
                {"role": "system", "content": VALERIA_SYSTEM + f"\nINFORMACIÓN DISPONIBLE:\n{context}"},
                {"role": "user", "content": user_text},
            ],
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "quota" in err_str or "rate" in err_str:
            logger.warning(f"LLM rate limit hit: {e}")
            raise HTTPException(
                status_code=503,
                detail="El asistente está temporalmente ocupado. Por favor intentá de nuevo en unos segundos."
            )
        raise
    # Garantizar máximo 5 oraciones aunque el LLM no respete la regla
    return _truncate_to_sentences(raw, max_sentences=5)


async def _tts_mp3(text: str) -> bytes:
    """Convierte texto a MP3 usando ElevenLabs (Karla, peruana). Para reproducción en browser."""
    if not elevenlabs_client:
        raise Exception("ElevenLabs not configured")

    async def _generate() -> bytes:
        audio_bytes = b""
        stream = elevenlabs_client.text_to_speech.stream(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(
                stability=0.55,
                similarity_boost=0.80,
                style=0.0,
                use_speaker_boost=True,
            ),
        )
        for chunk in stream:
            audio_bytes += chunk
        return audio_bytes

    return await asyncio.wait_for(_generate(), timeout=30.0)


async def _tts_pcm(text: str) -> bytes:
    """Convierte texto a PCM 16-bit 24kHz usando ElevenLabs (Karla, peruana)."""
    if not elevenlabs_client:
        raise Exception("ElevenLabs not configured")

    async def _generate() -> bytes:
        audio_bytes = b""
        stream = elevenlabs_client.text_to_speech.stream(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="pcm_24000",   # PCM 16-bit 24kHz — requerido por LiveAvatar LITE
            voice_settings=VoiceSettings(
                stability=0.55,
                similarity_boost=0.80,
                style=0.0,
                use_speaker_boost=True,
            ),
        )
        for chunk in stream:
            audio_bytes += chunk
        return audio_bytes

    return await asyncio.wait_for(_generate(), timeout=30.0)


@api_router.get("/liveavatar/config")
async def get_liveavatar_config():
    if not liveavatar_service:
        raise HTTPException(status_code=503, detail="LiveAvatar service not initialized")
    return liveavatar_service.get_avatar_config()


@api_router.post("/liveavatar/create-session")
async def create_liveavatar_session():
    """
    Crea sesión LITE en liveavatar.com.
    Retorna: session_id, livekit_url, livekit_token, ws_url
    El frontend conecta LiveKit para ver el video.
    El backend conecta el WebSocket para enviar audio.
    """
    try:
        if not liveavatar_service:
            raise HTTPException(status_code=503, detail="LiveAvatar service not initialized")

        session_data = await liveavatar_service.create_session()
        session_id   = session_data["session_id"]
        ws_url        = session_data.get("ws_url")

        if ws_url:
            # Conectar el WebSocket en background (el frontend no lo necesita)
            await liveavatar_service.connect_websocket(session_id, ws_url)
        else:
            logger.warning("No ws_url returned — LITE mode WS not available")

        return {"success": True, "session": session_data}

    except Exception as e:
        logger.error(f"Error creating LiveAvatar LITE session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/liveavatar/speak")
async def liveavatar_speak(request: SpeakRequest):
    """
    Flujo completo voice → avatar:
    1. Decodifica audio base64 del frontend
    2. STT: ElevenLabs Scribe transcribe
    3. LLM: Gemini genera respuesta con base de conocimientos
    4. TTS: ElevenLabs Karla PCM 24kHz
    5. Envía audio al avatar vía WebSocket → lip-sync

    Retorna: transcribed_text, ai_response (para mostrar en historial)
    """
    lock = _get_session_lock(request.session_id)
    # asyncio runs on a single thread — lock.locked() + acquire is effectively atomic
    # within one event loop iteration (no OS-level thread preemption between these lines)
    if lock.locked():
        raise HTTPException(status_code=429, detail="Ya hay una respuesta en proceso. Esperá que Valeria termine.")

    async with lock:
        try:
            if not liveavatar_service:
                raise HTTPException(status_code=503, detail="LiveAvatar service not initialized")
            if not elevenlabs_client:
                raise HTTPException(status_code=503, detail="ElevenLabs not configured")

            # Validate and decode audio base64 — reject oversized payloads (5 MB max)
            MAX_AUDIO_B64 = 5 * 1024 * 1024 * 4 // 3  # ~6.7 MB base64 → 5 MB binary
            if len(request.audio_base64) > MAX_AUDIO_B64:
                raise HTTPException(status_code=413, detail="Audio demasiado largo (máx 5 MB)")
            try:
                audio_bytes = base64.b64decode(request.audio_base64)
            except Exception:
                raise HTTPException(status_code=400, detail="Audio base64 inválido")

            logger.info(f"🎤 Received audio: {len(audio_bytes)} bytes for session {request.session_id[:8]}")

            # Step 1: STT
            # Pass filename so ElevenLabs can detect the format (webm/opus → ogg is compatible)
            audio_file = ("audio.webm", io.BytesIO(audio_bytes), "audio/webm")
            transcription = elevenlabs_client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v1",
            )
            raw_text = transcription.text if hasattr(transcription, "text") else str(transcription)
            user_text = raw_text.strip()[:2000]  # cap transcription length to avoid LLM token overflow
            logger.info(f"📝 Transcribed: {user_text}")

            if not user_text:
                raise HTTPException(status_code=400, detail="No se pudo transcribir el audio")

            # Step 2: LLM
            conv_id     = request.conversation_id or str(uuid.uuid4())
            ai_response = await _build_valeria_response(user_text, conv_id)
            logger.info(f"🤖 Response: {ai_response[:80]}...")

            # Step 3: TTS — generate MP3 (browser) and optionally PCM (lip-sync) concurrently
            ws_connected = liveavatar_service.is_connected(request.session_id)
            if ws_connected:
                try:
                    mp3_bytes, pcm_bytes = await asyncio.gather(
                        _tts_mp3(ai_response),
                        _tts_pcm(ai_response),
                    )
                except Exception as e:
                    logger.warning(f"Parallel TTS failed, falling back to MP3 only: {e}")
                    mp3_bytes = await _tts_mp3(ai_response)
                    pcm_bytes = None
            else:
                mp3_bytes = await _tts_mp3(ai_response)
                pcm_bytes = None
                logger.warning(f"No WS connection for session {request.session_id[:8]} — lip-sync unavailable")

            audio_b64 = base64.b64encode(mp3_bytes).decode("utf-8")
            audio_url = f"data:audio/mpeg;base64,{audio_b64}"
            logger.info(f"🔊 MP3 audio: {len(mp3_bytes)} bytes")

            # Step 4: Send PCM to avatar for lip-sync (best-effort)
            if ws_connected and pcm_bytes:
                try:
                    await liveavatar_service.speak(request.session_id, pcm_bytes)
                except Exception as e:
                    logger.warning(f"Avatar lip-sync failed (non-fatal): {e}")

            return {
                "success":          True,
                "transcribed_text": user_text,
                "ai_response":      ai_response,
                "audio_url":        audio_url,
                "conversation_id":  conv_id,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in /liveavatar/speak: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/liveavatar/speak-text")
async def liveavatar_speak_text(request: TextSpeakRequest):
    """
    Modo texto: usuario escribe → avatar habla.
    1. LLM genera respuesta
    2. TTS PCM → avatar lip-sync
    """
    lock = _get_session_lock(request.session_id)
    if lock.locked():
        raise HTTPException(status_code=429, detail="Ya hay una respuesta en proceso. Esperá que Valeria termine.")

    async with lock:
        try:
            if not liveavatar_service:
                raise HTTPException(status_code=503, detail="LiveAvatar service not initialized")

            user_text = request.text.strip()[:2000]  # cap input length
            if not user_text:
                raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
            conv_id     = request.conversation_id or str(uuid.uuid4())
            ai_response = await _build_valeria_response(user_text, conv_id)
            logger.info(f"🤖 Text response: {ai_response[:80]}...")

            # TTS — generate MP3 (browser) and optionally PCM (lip-sync) concurrently
            ws_connected = liveavatar_service.is_connected(request.session_id)
            if ws_connected:
                try:
                    mp3_bytes, pcm_bytes = await asyncio.gather(
                        _tts_mp3(ai_response),
                        _tts_pcm(ai_response),
                    )
                except Exception as e:
                    logger.warning(f"Parallel TTS failed, falling back to MP3 only: {e}")
                    mp3_bytes = await _tts_mp3(ai_response)
                    pcm_bytes = None
            else:
                mp3_bytes = await _tts_mp3(ai_response)
                pcm_bytes = None
                logger.warning(f"No WS for text-speak session {request.session_id[:8]}")

            audio_b64 = base64.b64encode(mp3_bytes).decode("utf-8")
            audio_url = f"data:audio/mpeg;base64,{audio_b64}"

            # Send PCM to avatar for lip-sync (best-effort)
            if ws_connected and pcm_bytes:
                try:
                    await liveavatar_service.speak(request.session_id, pcm_bytes)
                except Exception as e:
                    logger.warning(f"Avatar lip-sync failed (non-fatal): {e}")

            return {
                "success":         True,
                "ai_response":     ai_response,
                "audio_url":       audio_url,
                "conversation_id": conv_id,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in /liveavatar/speak-text: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/liveavatar/interrupt")
async def liveavatar_interrupt(request: InterruptRequest):
    """Detiene al avatar inmediatamente."""
    try:
        if not liveavatar_service:
            raise HTTPException(status_code=503, detail="LiveAvatar service not initialized")
        await liveavatar_service.interrupt(request.session_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"Error interrupting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/liveavatar/close-session/{session_id}")
async def close_liveavatar_session(session_id: str):
    """Cierra sesión y WebSocket."""
    try:
        if not liveavatar_service:
            raise HTTPException(status_code=503, detail="LiveAvatar service not initialized")
        success = await liveavatar_service.close_session(session_id)
        # Limpiar el lock de la sesión para evitar memory leak
        _session_locks.pop(session_id, None)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error closing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CHAT WITH SEMANTIC SEARCH (text only, no avatar)
# ============================================================================

@api_router.post("/chat")
async def chat_with_knowledge_base(request: ChatRequest):
    """Chat de texto puro (sin avatar). Retorna texto + audio MP3 opcional."""
    try:
        user_message = request.message.strip()
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        conv_id     = request.conversation_id or str(uuid.uuid4())
        ai_response = await _build_valeria_response(user_message, conv_id)
        logger.info(f"✅ Chat response: {ai_response[:100]}...")

        return {
            "message":         user_message,
            "response":        ai_response,
            "conversation_id": conv_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# ============================================================================
# END LIVE AVATAR ENDPOINTS
# ============================================================================

# Include all API routes
app.include_router(api_router)

# Startup/shutdown handled by lifespan context manager above