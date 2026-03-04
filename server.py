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
LLM_MODEL_NAME = "gpt-4o-mini" if OPENAI_API_KEY else "gemini-2.0-flash"
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

# Cache for knowledge base documents (static content — loaded once at startup)
_kb_docs_cache: list | None = None

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
        "titulo": "Prados de Paraíso - Base de Conocimientos Oficial (Versión Integrada)",
        "marker": "posesionarios",  # texto único de la pregunta 58 — fuerza update si no está
        "contenido": """BASE DE CONOCIMIENTOS DEL BOT (VERSIÓN INTEGRADA Y FINAL)

1. ¿Qué es Prados del Paraíso?
Prados de Paraíso es una marca comercial de Desarrolladora Santa María del Norte SAC, dedicada a desarrollar proyectos inmobiliarios con un enfoque ecológico y sostenible. Busca innovar en el sector, combinando eficiencia ambiental, diseño funcional y calidad de vida. Responde a la demanda de estilos de vida responsables y un desarrollo inmobiliario consciente.

2. ¿Qué proyectos tiene Prados del Paraíso?
Prados de Paraíso actualmente cuenta con dos proyectos. Uno de ellos ya ha sido entregado con éxito y se llama "Prados de Paraíso – Casa Huerto Ecológico". El segundo proyecto, que se encuentra en desarrollo, es "Prados de Paraíso Villa Eco-Sostenible".
Ambos proyectos reflejan el compromiso de la marca con un enfoque ecológico y sostenible, ofreciendo oportunidades de inversión segura y con visión de futuro.

3. ¿Dónde se ubica el proyecto Villa Eco-Sostenible?
El proyecto "Prados de Paraíso Villa Eco-Sostenible" se encuentra ubicado a la altura del kilómetro 137.25 de la Carretera Panamericana Norte. Pertenece al distrito de Santa María, en la provincia de Huaura, departamento de Lima.
Es una ubicación estratégica que busca combinar la accesibilidad con el entorno natural que caracteriza a nuestros desarrollos.

4. ¿Quién desarrolla el proyecto?
El proyecto es promovido por Desarrolladora Santa María del Norte S.A.C., una empresa con experiencia en el mercado inmobiliario.
Además, para garantizar la transparencia y seguridad jurídica en todos los procesos, contamos con el respaldo y asesoramiento legal de DS CASAHIERRO ABOGADOS y tenemos un convenio con la NOTARIA TAMBINI.

5. ¿La empresa es formal?
Sí, la empresa es formal y cuenta con el respaldo de la marca Prados de Paraíso, que tiene una trayectoria sólida en el desarrollo de proyectos inmobiliarios. Además, se encuentra inscrita en la Partida Electrónica número 15437655 del Registro de Personas Jurídicas de Lima.
Esto asegura que opera bajo todas las regulaciones legales pertinentes.

6. ¿Desde cuándo existe el proyecto?
El proyecto "Villa Eco-Sostenible" inició en octubre del dos mil veintitrés.
Sin embargo, es importante destacar que, aunque el desarrollo del proyecto es reciente, nuestra empresa mantiene la posesión del terreno desde el año mil novecientos noventa y ocho, lo cual nos brinda un respaldo histórico sólido en la zona.

7. ¿Qué es exactamente lo que ofrecen?
En Prados de Paraíso ofrecemos la transferencia de posesión de lotes. Esto significa que, al adquirir un lote con nosotros, obtienes el derecho de uso, disfrute y control efectivo del terreno.
Es importante que tengas claro que la condición legal actual del predio es de posesión, no de propiedad titulada inscrita en Registros Públicos a nombre de la empresa. Sin embargo, nuestra posesión es sólida y segura porque:
La empresa ejerce la posesión del terreno desde mil novecientos noventa y ocho, respaldada por escrituras públicas.
Contamos con el reconocimiento de la Municipalidad de Santa María a través de las cartillas municipales (Predio Rústico y Hoja Resumen).
Formalizamos tu adquisición mediante un Contrato de Transferencia de Posesión elevado a Escritura Pública ante notario.
Adicionalmente, contamos con la Resolución N.º 00202-2026-SOPCFPUR/MDSM, que aprueba el cambio de zonificación, reconociendo el área del proyecto como Zona Residencial de Densidad Media (RDM – R3). Este importante avance permite la ejecución de áreas recreativas, parques y espacios diversos, que forman parte del concepto integral de la comunidad sostenible de Villa Eco-Sostenible.
En resumen, te ofrecemos una oportunidad de inversión sólida, con respaldo legal, reconocimiento municipal y proyección urbana, dentro de una comunidad que ya cuenta con más de ochocientos clientes satisfechos y que continúa consolidándose como un proyecto sostenible y con visión de crecimiento.

8. ¿Es lo mismo transferencia de posesión que comprar un terreno?
No, no es exactamente lo mismo, aunque en la práctica ambos te permiten usar el terreno. La diferencia clave es que "comprar la propiedad" significa que te conviertes en el dueño legal absoluto y tu nombre aparece inscrito en los Registros Públicos (SUNARP).
En cambio, la "transferencia de posesión", que es lo que ofrecemos en Prados de Paraíso, significa que adquieres el uso, disfrute y control del lote. Tienes un respaldo mediante el Contrato de Transferencia de Posesión y una Escritura Pública, lo que te da un derecho real sobre el bien, pero no la titularidad registral de la propiedad.

9. ¿Qué diferencia hay entre posesión y propiedad?
La propiedad es el derecho legal absoluto sobre un bien, que te otorga la titularidad y se inscribe formalmente en los Registros Públicos. Como propietario, tienes el derecho de usar, disfrutar, disponer y reivindicar el bien.
Por otro lado, la posesión es el poder de hecho que ejerces sobre un bien, lo que significa que lo usas y disfrutas físicamente, independientemente de si eres el titular registral. Este derecho está reconocido por el Código Civil y se puede transferir mediante un Contrato de Transferencia de Posesión. En resumen, la propiedad es el título legal, mientras que la posesión es el uso y control físico del terreno.

10. ¿Puedo construir en el lote?
Sí, puedes construir en el lote que adquieras en Prados de Paraíso, siempre y cuando respetes las normativas locales y el Reglamento de Diseño y Construcción. Al adquirir el lote, tendrás el derecho de uso y disfrute exclusivo sobre él. Así que, si tienes un proyecto en mente, ¡adelante con ello!

11. ¿La escritura me hace propietario?
No, una escritura pública de transferencia de posesión no te convierte en propietario en el sentido registral. Es una distinción importante: la escritura pública en el contexto de Prados de Paraíso formaliza la transferencia de la posesión, dándote un respaldo legal sobre el uso y disfrute del terreno.
La propiedad es un derecho distinto que otorga la titularidad del bien y es lo que se inscribe en los Registros Públicos (SUNARP). Para que tu nombre aparezca como propietario en SUNARP, se requiere un proceso adicional de saneamiento.

12. ¿La empresa responde por el lote?
Sí, la empresa responde por el lote en el sentido de que garantiza la transferencia de la posesión del predio. Desarrolladora Santa María del Norte S.A.C. formaliza esta transferencia mediante un Contrato de Transferencia de Posesión, el cual puede elevarse a Escritura Pública a solicitud del cliente, otorgando el derecho de uso y disfrute del lote asignado.
Es importante aclarar que la empresa garantiza la entrega de la posesión en la condición legal informada (respaldada por documentos históricos), pero no responde por situaciones externas futuras, como desastres naturales o actos de terceros, ni ofrece indemnizaciones económicas por pérdida de posesión ajena a su incumplimiento contractual.

13. ¿Qué planos entregarán a la firma del contrato de transferencia de posesión?
Al momento de la firma del contrato de transferencia de posesión, se te proporcionarán tres documentos técnicos importantes: el plano de ubicación, la memoria descriptiva y los planos perimétricos.
Estos documentos son fundamentales porque delimitan físicamente el área sobre la cual ejercerás tu derecho de posesión, permitiéndote identificar con claridad la ubicación y las medidas exactas de tu lote.

14. ¿Cómo se respalda legalmente la posesión o qué documentos se entregan a los clientes?
La posesión en Prados de Paraíso está respaldada legalmente por varios documentos sólidos. La empresa ejerce una posesión de buena fe desde mil novecientos noventa y ocho, acreditada por escrituras públicas que dan fe de las transferencias de posesión a lo largo del tiempo. Además, la Municipalidad de Santa María reconoce esta posesión de manera indirecta a través de la emisión de cartillas municipales, como el Predio Rústico (PR) y la Hoja Resumen (HR), que demuestran el cumplimiento de las obligaciones tributarias.
Cuando adquieres un lote, te entregamos el Contrato de Transferencia de Posesión, que es el documento fundamental que formaliza tu derecho de uso y disfrute. Este contrato puede elevarse a Escritura Pública ante notario para mayor seguridad. También te facilitamos las escrituras públicas que respaldan la posesión de la empresa desde mil novecientos noventa y ocho y las cartillas municipales (PR y HR) que demuestran el cumplimiento de las obligaciones tributarias del predio.

15. ¿Cuál es el estado legal del proyecto y el proceso de adquisición de lote?
Estado Legal del Proyecto: La condición actual del proyecto es de posesión, no de propiedad titulada. Esta posesión está respaldada documentalmente por Escrituras Públicas que datan desde mil novecientos noventa y ocho y cuenta con un reconocimiento municipal indirecto a través de las cartillas de Predio Rústico (PR) y Hoja Resumen (HR), lo que nos permite cumplir con nuestras obligaciones tributarias.
Adicionalmente, contamos con la Resolución que aprueba el cambio de zonificación, reconociendo el área del proyecto como Zona Residencial de Densidad Media (RDM – R3). Este importante avance permite la ejecución de áreas recreativas, parques y espacios diversos, que forman parte del concepto integral de la comunidad sostenible de Villa Eco-Sostenible.
Proceso de Adquisición: Para adquirir un lote con nosotros, el proceso se basa en la transferencia de esta posesión y consta de tres pasos principales. Primero, se firma un Contrato de Transferencia de Posesión. Segundo, para tu seguridad jurídica, este contrato se puede elevar a Escritura Pública ante notario, dándole fecha cierta y plena fuerza legal. Tercero, una vez completados los pagos y trámites, se te hace la entrega física del lote para que puedas ejercer tu derecho de uso y disfrute.

16. ¿Qué documentos entrega la empresa al transferir la posesión?
Para formalizar la transferencia y brindarte seguridad jurídica sobre tu lote en Prados de Paraíso, la empresa te entregará varios documentos importantes. Recibirás el Contrato de Transferencia de Posesión, que es el documento principal que te otorga el derecho de uso y disfrute del lote. Además, se te facilitarán las Escrituras Públicas que respaldan la posesión legítima del predio por parte de la empresa desde mil novecientos noventa y ocho, y las Cartillas Municipales (Predio Rústico y Hoja Resumen) que demuestran el cumplimiento de las obligaciones tributarias.

17. ¿Qué significa una transferencia de posesión?
La transferencia de posesión significa que se te otorga el derecho de uso y disfrute del lote. Este proceso se formaliza a través de un Contrato de Transferencia de Posesión, que luego se eleva a Escritura Pública ante un notario. En el caso de Prados de Paraíso, esta transferencia te permite disfrutar del lote y ejercer control sobre él, respaldado por la confianza y la seguridad del contrato.

18. ¿Qué derechos tengo como poseedor?
Como poseedor en Prados de Paraíso, usted tiene el derecho de usar y disfrutar físicamente del lote, lo que incluye ocuparlo, cercarlo y construir en él, siempre sujeto a las normativas locales y al contrato de posesión. Este derecho está respaldado por un Contrato de Transferencia de Posesión, que puede elevarse a Escritura Pública para mayor seguridad jurídica.
La posesión le otorga el control físico y el poder jurídico sobre el bien, permitiéndole disponer de él como si fuera suyo. Además, el Contrato de Transferencia de Posesión delimita y asigna el derecho de uso y disfrute exclusivo sobre su lote específico. Es importante recordar que, aunque la posesión es un derecho real protegido, es distinta de la propiedad inscrita en Registros Públicos.

19. ¿Puedo perder mi lote?
Entiendo perfectamente tu preocupación, es una pregunta muy importante y quiero darte tranquilidad al respecto.
Nuestra empresa mantiene una posesión sólida, respaldada por documentos legales como escrituras públicas que datan desde 1998, además de ejercer una posesión efectiva y de buena fe reconocida por la Municipalidad a través del pago de tributos. Al suscribir tu contrato de transferencia de posesión, adquieres por tracto sucesivo el derecho posesorio que la empresa tiene desde hace décadas, por lo que legalmente no sería posible que pierdas tu lote.
Además, incluso si un proceso de saneamiento (como una prescripción adquisitiva) no resultara favorable en un primer momento, eso no implica automáticamente la pérdida de la posesión, ya que tú mantienes el derecho de uso y disfrute mientras cumplas con tus obligaciones contractuales.

20. ¿Direfor, siendo el legítimo propietario, me puede quitar mi lote?
Entiendo tu preocupación, es una pregunta muy válida. Mira, es cierto que el predio figura a nombre de DIREFOR en los Registros Públicos, pero nuestra empresa, Desarrolladora Santa María del Norte S.A.C., mantiene la posesión del predio desde el año 1998.
Esto es clave porque nuestra posesión es anterior a la Ley 29618 (que habla sobre la imprescriptibilidad de los predios del Estado). Aunque no tenemos un título de propiedad registrado, ejercemos la posesión con el respaldo de escrituras públicas y cartillas municipales, por lo que la presencia de DIREFOR como titular registral no implica que seamos invasores ni representa un riesgo inmediato para tu posesión.
Nosotros te garantizamos la entrega de la posesión mediante un Contrato de Transferencia de Posesión, lo que te otorga el uso y disfrute del lote.

21. Si llevo un proceso de saneamiento vía prescripción adquisitiva de dominio, y pierdo el proceso, ¿me pueden quitar mi lote o mi posesión?
Si llevas un proceso de saneamiento vía prescripción adquisitiva de dominio y este no resulta favorable, esto significa que en ese momento y por esa vía, no se logró acreditar tu derecho de propiedad sobre el lote. Sin embargo, la improcedencia o el rechazo de este proceso no implica automáticamente que vayas a perder tu posesión.
Tú adquiriste la posesión del lote mediante un Contrato de Transferencia de Posesión, lo cual te otorga el derecho de uso y disfrute. Este derecho se mantiene mientras tu posesión no sea cuestionada o despojada por una resolución judicial firme.
El proceso de prescripción adquisitiva no tiene como objetivo desalojar al poseedor, sino evaluar si se cumplen los requisitos para adquirir la propiedad. Por lo tanto, perder dicho proceso no habilita por sí solo a un tercero a quitarte el lote, ni extingue tu derecho posesorio.
En resumen, aunque la prescripción adquisitiva no prospere, tú mantienes tu posesión, siempre y cuando continúes ejerciéndola conforme a la ley y cumplas con las obligaciones contractuales que asumiste.

22. ¿La empresa participa en el proceso de formalización o saneamiento?
Gracias por tu consulta, es muy importante aclararlo. La empresa no realiza directamente el trámite de formalización o saneamiento del título de propiedad, ya que este es un proceso personal que corresponde a cada cliente una vez que el proyecto ha sido entregado y el lote cancelado.
Lo que sí hacemos es garantizar la entrega de la posesión del lote mediante un Contrato de Transferencia de Posesión y brindarte todo el respaldo documentario necesario para que tú puedas iniciar ese trámite. Te entregaremos copias de las escrituras públicas que acreditan la posesión desde 1998 y la documentación municipal (Predio Rústico y Hoja Resumen) para que, con la ayuda de tu abogado, evalúes la mejor vía de formalización.

23. ¿Existe el riesgo de que DIREFOR inicie una demanda de reivindicación o desalojo?
Entiendo perfectamente tu preocupación; es una consulta muy razonable al evaluar una inversión de este tipo. En el proyecto Prados de Paraíso, la seguridad jurídica se sustenta en que la empresa ejerce una posesión desde el año mil novecientos noventa y ocho.
Si bien la empresa no cuenta con una partida registral de propiedad a su nombre, sí ejerce y administra el terreno de manera efectiva y documentada. Esta posesión se encuentra respaldada por escrituras públicas que acreditan nuestra presencia desde mil novecientos noventa y ocho, además de documentación municipal (Predio Rústico y Hoja Resumen) que evidencia el cumplimiento de obligaciones tributarias y el reconocimiento de la posesión por parte de la Municipalidad de Santa María.
Adicionalmente, contamos con la Resolución que aprueba el cambio de zonificación, reconociendo el área del proyecto como Zona Residencial de Densidad Media (RDM – R3). Este importante avance permite la ejecución de áreas recreativas, parques y espacios diversos, que forman parte del concepto integral de la comunidad sostenible de Villa Eco-Sostenible. Además este reconocimiento municipal representa un respaldo institucional importante, ya que confirma la posesión del predio, brindando mayor formalidad y seguridad jurídica a los futuros adquirentes, respaldando la formalidad de El Proyecto y la protección de su inversión.
Es importante precisar que una eventual demanda de reivindicación o desalojo no prospera automáticamente cuando existe una posesión antigua, pública y ejercida de buena fe, como en este caso. La solidez de la posesión, el sustento documental y el acompañamiento legal existente reducen significativamente la probabilidad de acciones de este tipo.

24. ¿La posesión que ustedes transfieren me permite defenderme legalmente frente a terceros o solo frente a la empresa?
La posesión que transferimos en Prados de Paraíso te permite defenderte legalmente no solo frente a nuestra empresa, sino también frente a terceros. Esto se debe a que el Código Civil Peruano reconoce la posesión como un derecho real, lo que te otorga la facultad de usar y disfrutar del bien como si fuera tuyo.
Al adquirir la posesión mediante un Contrato de Transferencia de Posesión, que se eleva a Escritura Pública, obtienes un respaldo legal sólido. Además, un punto importante es la "suma de plazos posesorios", regulada en el artículo 898 del Código Civil, que te permite sumar tu tiempo de posesión al tiempo que nuestra empresa ha poseído el terreno desde 1998. Esto fortalece aún más tu posición legal.

25. ¿Por qué la empresa no sanea primero el terreno y después lo vende?
Es una excelente pregunta y es importante entender la estrategia detrás de Prados de Paraíso.
La razón principal es que la condición legal actual del predio es la posesión, no la propiedad. Esto significa que la empresa ejerce el uso y disfrute del inmueble, una situación que está formalizada y respaldada por documentación, incluyendo escrituras públicas que acreditan la continuidad posesoria desde 1998, y documentación municipal de Santa María que reconoce esta posesión.
La gerencia de la empresa ha tomado la decisión estratégica de estructurar el proyecto bajo un modelo de transferencia de posesión. Esto se hace para ofrecer una alternativa clara, transparente y comercialmente viable a los interesados, sin prometer ni ofrecer procesos de titulación o saneamiento registral por parte de la empresa. Es fundamental saber que la posesión puede ser transferida legalmente.
Por lo tanto, la empresa garantiza la entrega de la posesión mediante un Contrato de Transferencia de Posesión, que se formaliza una vez que el adquirente ha pagado el valor total del lote. A partir de ese momento, como nuevo poseedor, puedes evaluar de manera independiente si deseas iniciar un procedimiento de saneamiento o formalización de la titularidad, asumiendo los costos y trámites que esto implique. Para facilitar cualquier evaluación futura, la empresa pone a tu disposición toda la documentación existente, como las escrituras públicas y las constancias municipales relacionadas con la posesión.

26. ¿Existe hoy algún juicio, denuncia o problema legal activo sobre este terreno?
Basándome en la información legal disponible sobre el proyecto Prados de Paraíso, puedo confirmarte que no existe ningún juicio, denuncia o problema legal activo sobre el terreno. Aunque la partida registral figura a nombre de DIREFOR, una entidad del Estado, esto no implica que haya un conflicto, ya que nuestra posesión está respaldada por escrituras públicas desde mil novecientos noventa y ocho. El proyecto se desarrolla en un marco de transparencia, sin litigios que pongan en riesgo tu adquisición de la posesión.

27. Si yo compro hoy el lote y mañana hay un problema legal con el terreno, ¿qué respaldo real tengo como adquiriente?
Lo primero que debes saber es que la condición legal del predio que adquieres es la posesión, no la propiedad. Esto significa que nuestra empresa te garantiza la entrega de la posesión del lote, lo que te otorga el derecho de uso y disfrute del mismo. Esta transferencia se formaliza mediante un Contrato de Transferencia de Posesión.
Tu respaldo como adquirente se basa en este Contrato de Transferencia de Posesión, que te otorga el derecho de uso y disfrute. Además, la posesión de nuestra empresa está documentada y respaldada por escrituras públicas que datan desde mil novecientos noventa y ocho, y la Municipalidad de Santa María reconoce nuestra posesión de manera indirecta a través de la emisión de cartillas municipales.

28. ¿Qué riesgos existen al adquirir el lote por transferencia de posesión?
Al adquirir un lote mediante transferencia de posesión, el riesgo principal que debes considerar es que no estás adquiriendo la propiedad inscrita en Registros Públicos, sino únicamente el derecho de uso y disfrute del terreno. Esto implica que la obtención del título de propiedad no es automática; dependerá de que tú, como adquirente, inicies y asumas un proceso de saneamiento de manera personal en el futuro.
Además, es importante tener claro que la empresa no garantiza la titulación final, sino la entrega de una posesión documentada y formalizada mediante contrato. Sin embargo, para tu tranquilidad, esta posesión que te transferimos es sólida, ya que está respaldada por escrituras públicas desde mil novecientos noventa y ocho y cuenta con reconocimiento municipal.

29. ¿La empresa garantiza que no habrá problemas legales en el futuro?
La empresa no puede garantizar escenarios futuros que estén fuera de su control. Lo que sí garantiza, de manera expresa y contractual, es la entrega de la posesión del lote en la condición legal que se te ha informado.
Actualmente, la empresa ejerce una posesión que está debidamente respaldada por escrituras públicas que acreditan su ejercicio posesorio, así como por documentación municipal. Esta posesión sólida es la que se te transfiere mediante el Contrato de Transferencia de Posesión.

30. ¿Qué obligaciones asume el adquirente?
Al adquirir un lote en Prados del Paraíso mediante transferencia de posesión, asumes varias obligaciones importantes que están detalladas en el contrato. Principalmente, te comprometes a pagar el precio pactado por la transferencia, ya sea al contado o siguiendo el cronograma de pagos establecido.
Además, debes cumplir con las condiciones para que se te entregue la posesión, lo cual incluye la cancelación total del valor del lote. También serás responsable de asumir los trámites notariales y administrativos que origine la Escritura Pública del Contrato de Transferencia, así como cumplir con el reglamento interno del proyecto y las normas sobre el uso del lote.

31. ¿Se paga algún impuesto o tributo por la transferencia de posesión?
Sí. Con la entrega del lote, el cliente asumirá el pago de los tributos municipales que correspondan, de conformidad con la normativa municipal vigente.
A partir de ese momento, el cliente deberá gestionar ante la municipalidad el alta como nuevo contribuyente y la baja del anterior, a fin de que figure formalmente como responsable de las obligaciones tributarias del lote adquirido.
Previamente, la empresa se encargará de realizar la individualización administrativa de las cartillas municipales de cada lote (HR y PR), lo que permitirá que cada predio cuente con su propia identificación tributaria independiente.
Mientras no se efectúe dicha individualización, los tributos se administran sobre el predio matriz del proyecto.

32. ¿El contrato contempla cláusulas de saneamiento posesorio?
El contrato de Transferencia de Posesión está diseñado para regular y garantizar la entrega de la posesión del lote, no para llevar a cabo un saneamiento de la propiedad. Esto significa que se enfoca en asegurar su derecho de uso y disfrute sobre el bien.

33. ¿La empresa ha evaluado iniciar el proceso prescripción adquisitiva del proyecto?
Es una excelente pregunta. La empresa ha evaluado la posibilidad de iniciar un proceso de prescripción adquisitiva para el proyecto. Sin embargo, la decisión de hacerlo es estratégica y considera diversos factores legales, técnicos y comerciales.
Actualmente, la empresa no ofrece el inicio de un proceso de prescripción adquisitiva como parte del proyecto. Su actividad principal se centra en la transferencia de posesión, no en la comercialización de propiedad ya saneada. Esto significa que la obtención del título de propiedad es un proceso que el adquirente, si lo desea, deberá iniciar y asumir de manera personal.

34. ¿La transferencia de posesión podría considerarse simulación de compraventa?
Esa es una excelente pregunta que toca un punto legal muy importante. Permíteme aclararte la diferencia para que tengas total tranquilidad.
La transferencia de posesión y la compraventa de propiedad son actos jurídicos distintos y no deben confundirse. La Transferencia de Posesión (lo que hacemos en Prados de Paraíso) implica ceder el derecho de ejercer el poder de hecho sobre un bien (usarlo y disfrutarlo). Esto es un acto transparente, respaldado por asesoramiento legal y formalizado mediante un contrato que puede elevarse a Escritura Pública. La Compraventa de Propiedad implica transferir el derecho de ser el dueño legal absoluto, lo cual se inscribe en los Registros Públicos.
Una simulación ocurre cuando las partes fingen celebrar un acto para engañar a terceros o evadir la ley. En nuestro caso, no hay simulación porque el contrato es claro y específico: se transfiere la posesión, no la propiedad saneada. Nosotros somos muy transparentes al informar que lo que adquieres es el derecho de uso y disfrute, respaldado por nuestra cadena de posesión documentada desde 1998, y no un título de propiedad inscrito en SUNARP en este momento.

35. ¿Cómo se gestiona la eventual formalización futura de la posesión?
La formalización futura de la posesión se gestiona a través de un proceso de saneamiento físico-legal. Este proceso permite al poseedor evaluar la posibilidad de acceder al derecho de propiedad y, si es el caso, inscribirlo en Registros Públicos.
Es importante saber que este saneamiento no forma parte del servicio que ofrece la empresa, sino que debe ser asumido de manera personal por el adquirente una vez que haya recibido la posesión del lote y cumplido con las condiciones contractuales. Existen vías legales como la prescripción adquisitiva de dominio, que se tramita judicialmente, o vías administrativas, según la normativa. La empresa te brindará el respaldo documental necesario para iniciar este proceso.

36. ¿Qué obligaciones mantiene la empresa luego de la transferencia?
Una vez realizada la transferencia de la posesión del lote, las obligaciones de la empresa se limitan estrictamente a lo establecido en el contrato. Principalmente, la empresa se compromete a entregar la posesión del lote en la condición legal que se te informó previamente, proporcionarte toda la documentación posesoria que sustenta la transferencia realizada, y cumplir con cualquier obligación contractual que pudiera haber quedado pendiente, si correspondiera.

37. ¿La empresa mantiene la administración sobre áreas recreativas?
La empresa asume la gestión inicial necesaria para la organización del proyecto. Sin embargo, la administración y el mantenimiento de las áreas recreativas pueden ser asumidos posteriormente por una asociación. Esto se realizará conforme a lo previsto en el reglamento interno y a medida que se consolide el proyecto.

38. ¿Existen contingencias penales asociadas al modelo de negocio?
De acuerdo con la naturaleza del proyecto y lo establecido contractualmente, no existen contingencias penales inherentes al modelo de negocio de Prados de Paraíso.
Esto se debe a que el proyecto se basa en la transferencia de posesión, una figura reconocida por el ordenamiento jurídico peruano. Nuestra posesión está respaldada por documentación formal y Escrituras Públicas que datan desde 1998. Todo el proceso se realiza de manera transparente, con asesoría legal y notarial, diferenciando claramente la posesión de la propiedad.

39. ¿Qué respaldo real tiene el cliente si surge un conflicto?
Entiendo perfectamente tu inquietud, es fundamental sentir seguridad al realizar una inversión.
Si llegara a surgir algún conflicto, tu respaldo real se fundamenta en tres pilares principales que brindan solidez a tu adquisición. Primero, la Seguridad Jurídica Histórica: la empresa cuenta con una posesión respaldada por escrituras públicas que datan desde 1998, además de documentación formal que acredita nuestra trayectoria en el terreno. Segundo, el Asesoramiento Legal Especializado: contamos con el respaldo y la asesoría del estudio DS CASAHIERRO ABOGADOS, así como un convenio con la NOTARIA TAMBINI. Tercero, el Compromiso de Documentación: la empresa se compromete a entregarte toda la documentación necesaria para que, si así lo deseas, puedas iniciar tu propio proceso de saneamiento físico-legal.

40. ¿Qué es DIREFOR y por qué figura como propietario?
DIREFOR es la Dirección de Formalización de la Propiedad Rural, una entidad del Estado. Figura como titular registral del predio matriz debido a un cambio normativo con la Ley número veintinueve mil seiscientos dieciocho, que entró en vigencia en el año dos mil diez.
Esta ley estableció que los terrenos sin propiedad inscrita pasaran a nombre del Estado. Sin embargo, es importante destacar que esta inscripción no invalida la posesión que nuestra empresa ejerce sobre el predio desde mil novecientos noventa y ocho, la cual está debidamente documentada.

41. ¿Es legal transferir la posesión de un terreno del Estado?
Sí, la legislación peruana reconoce la posesión como una situación jurídica protegida, que es distinta y diferente al derecho de propiedad. En Prados de Paraíso, lo que se transfiere es la posesión del terreno, no la propiedad. Nuestra empresa ejerce una posesión anterior a la inscripción estatal, debidamente documentada, y transfiere esa situación posesoria mediante un Contrato de Transferencia de Posesión.

42. ¿Qué sucede si se revierte la posesión a favor del Estado?
Actualmente, no existe ningún procedimiento administrativo o judicial que busque revertir la posesión del predio a favor del Estado. Aunque DIREFOR figura como titular registral del predio matriz por mandato de la Ley número veintinueve mil seiscientos dieciocho, esto no implica automáticamente la pérdida de la posesión existente. Nuestra empresa ejerce esta posesión desde mil novecientos noventa y ocho, y está debidamente documentada, lo que le brinda un respaldo sólido.

43. ¿La municipalidad reconoce oficialmente el proyecto?
La Municipalidad de Santa María reconoce nuestra posesión de manera indirecta a través de la emisión de cartillas municipales, específicamente el PR (Predio Rústico) y la HR (Hoja Resumen). Adicionalmente, contamos con la Resolución N.º 00202-2026-SOPCFPUR/MDSM, que aprueba el cambio de zonificación, reconociendo el área del proyecto como Zona Residencial de Densidad Media (RDM – R3), lo cual confirma la posesión del predio, brindando mayor formalidad y seguridad jurídica a los adquirentes, respaldando la formalidad del Proyecto y la protección de su inversión.

44. ¿Cómo impacta la ley que prohíbe la prescripción adquisitiva de inmuebles contra el Estado?
La Ley número veintinueve mil seiscientos dieciocho, promulgada en dos mil diez, prohíbe que los bienes inmuebles de dominio privado estatal sean adquiridos por particulares mediante prescripción adquisitiva. Esto significa que ya no se puede reclamar la propiedad de terrenos estatales solo por haberlos poseído durante mucho tiempo a partir de esa fecha.
Sin embargo, en el caso de Prados de Paraíso, la empresa cuenta con veintisiete años de posesión, la cual se inició antes de que esta ley entrara en vigor. Por lo tanto, la legitimidad de la posesión transferida a los clientes se mantiene, ya que la ley no invalida la posesión histórica que ya existía. En resumen, la ley protege al Estado de nuevas reclamaciones, pero no afecta las posesiones preexistentes.

45. ¿La empresa acompaña judicialmente al cliente si hay alguna contingencia legal?
Entiendo tu pregunta. En caso de que enfrentes una contingencia legal o decidas iniciar un proceso de formalización de tu lote, la gestión y representación legal corresponde al cliente. La empresa te proporcionará toda la documentación probatoria disponible para respaldar tu caso y facilitar tu defensa, pero la representación ante un juez debe ser realizada por tu propio abogado.

46. ¿La empresa indemnizará en caso de pérdida de posesión?
La empresa no asume responsabilidad económica ni ofrece una indemnización específica por la pérdida de la posesión si esta es causada por hechos externos o ajenos al incumplimiento del comprador.
Lo que la empresa garantiza es la entrega de una posesión documentada y formalizada mediante contrato, respaldada por la documentación histórica que posee desde mil novecientos noventa y ocho. Es decir, su compromiso es entregarte el lote con el respaldo legal de su posesión, pero no cubre contingencias futuras fuera de su control.

47. ¿Se puede individualizar la posesión por cada lote?
Sí. Cuando firmas el Contrato de Transferencia de Posesión, este documento delimita y asigna el derecho de uso y disfrute exclusivo sobre un lote determinado dentro del proyecto. Esto significa que tú tienes el control físico y el derecho a usar y disfrutar ese espacio concreto, cercarlo o construir en él.

48. ¿El adquirente podría ser demandado directamente ante un posible proceso judicial iniciado por el Estado?
Sí, como adquirente de la posesión, usted sería la parte directamente involucrada en cualquier proceso judicial que el Estado pudiera iniciar. Sin embargo, es importante destacar que la posesión que recibe está respaldada por documentación histórica y escrituras públicas desde mil novecientos noventa y ocho. Esto le brinda una garantía sobre la posesión de su lote, permitiéndole usar y disfrutar su inversión con tranquilidad y confianza.

49. ¿Qué pasa si el proyecto no logra consolidarse?
Entendemos que esta es una preocupación importante para cualquier inversión. La garantía principal de Prados de Paraíso es la antigüedad de la posesión que se transfiere a nuestros clientes, respaldada por escrituras públicas desde 1998.
Adicionalmente, contamos con la Resolución que aprueba el cambio de zonificación, reconociendo el área del proyecto como Zona Residencial de Densidad Media (RDM – R3). Este importante avance permite la ejecución de áreas recreativas, parques y espacios diversos, que forman parte del concepto integral de la comunidad sostenible de Villa Eco-Sostenible.
Si el proyecto no se consolida completamente, por ejemplo, en cuanto a infraestructura o desarrollo planificado, usted seguirá manteniendo la posesión de su lote, con pleno ejercicio de uso y disfrute sobre ese espacio.

50. ¿El contrato me protege frente a cualquier contingencia legal?
El contrato está diseñado principalmente para regular la transferencia de la posesión y las obligaciones de pago, asegurando que usted reciba la posesión de su lote con el respaldo de documentos históricos. Si bien le brinda seguridad sobre la posesión física y la documentación que acredita su derecho de ocupación, no cubre situaciones externas. Esto incluye litigios con terceros o con el Estado que puedan surgir en el futuro.

51. ¿La empresa responde económicamente frente a la pérdida de la posesión del proyecto?
La empresa no asume responsabilidad económica por la pérdida de la posesión si esta es causada por hechos externos o ajenos al incumplimiento del comprador. Es decir, la empresa respalda la posesión que te transfiere, pero no te indemnizará económicamente por causas que no sean su incumplimiento contractual.

52. ¿Las cartillas PR y HR están a nombre de mi lote específico?
No, las cartillas PR (Predio Rústico) y HR (Hoja Resumen) no estarán a nombre de su lote específico de forma individual. Estos tributos municipales se gestionan sobre el predio matriz, es decir, sobre la propiedad principal del proyecto.
Esto ocurre mientras no exista una individualización administrativa por cada lote. La empresa le entregará estos documentos que demuestran el cumplimiento de las obligaciones tributarias del predio general.

53. ¿Mi lote tendrá su propia cartilla municipal?
Actualmente las cartillas municipales PR y HR se emiten a nombre de la empresa para el predio en su totalidad.
La empresa se compromete a realizar el procedimiento de Individualización Administrativa ante la Municipalidad Distrital para tu lote. Esto te permitirá tener una mejor formalización de tu propiedad. Así que puedes estar tranquilo, ya que estamos trabajando para asegurar que cada adquirente tenga la documentación necesaria en el futuro.

54. ¿La empresa tiene Libro de Reclamaciones?
Sí, la empresa cuenta con un Libro de Reclamaciones.
Lo tenemos disponible en dos formatos para tu comodidad: Físico en nuestras oficinas ubicadas en Calle Libertadores ciento cincuenta y cinco, Oficina trescientos dos, distrito de San Isidro. Virtual accesible a través de nuestra página web: https://pradosdeparaiso.com.pe/

55. ¿Qué pasa si no estoy conforme con la respuesta de la empresa?
Si no estás conforme con la respuesta inicial que te brindamos, siempre puedes continuar el diálogo a través de nuestros canales internos para solicitar una revisión adicional, una reunión de aclaración o la intervención de un área especializada. Nuestra prioridad es resolver los reclamos de manera directa, pero si tras agotar estas vías internas el resultado no es satisfactorio, mantienes tu derecho de acudir a los organismos de protección al consumidor según la normativa vigente.

56. ¿Cuáles son los plazos de atención de un reclamo?
De acuerdo con el Reglamento del Libro de Reclamaciones y su modificatoria, el plazo máximo que tenemos como proveedores para atender un reclamo y brindarte una respuesta es de quince días hábiles improrrogables.

57. ¿La empresa se responsabiliza por daños externos?
En realidad, la empresa no asume responsabilidad por daños ocasionados por factores externos que estén fuera de su control. Esto incluye situaciones como desastres naturales, actos de terceros, decisiones de autoridades o cualquier otro evento fortuito o de fuerza mayor.
Nuestra responsabilidad se limita estrictamente a cumplir con las obligaciones que hemos asumido en el contrato, que son principalmente la entrega de la posesión del lote y la documentación correspondiente.

58. Si la empresa Desarrolladora Santa Maria del Norte S.A.C deja de pagar la deuda pendiente con el señor Manuel Ampuero por la transferencia de posesión, ¿Eso podría hacer que yo pierda mi lote o mi derecho de posesión?
Desde la suscripción de la Escritura Pública por la que el señor Manuel Ampuero transfirió la posesión a favor de Desarrolladora Santa María del Norte (en adelante, la "empresa"), adquirió válidamente la posesión efectiva del terreno.
En consecuencia, desde esa fecha la empresa ostenta la calidad de poseedora, con plena facultad para transferir dicha posesión a terceros. Esta condición posesoria no se ve afectada por las obligaciones internas o relaciones económicas que puedan existir entre las partes que intervinieron en la transferencia original.
Así, aun en el supuesto de que la empresa incumpliera algún pago u obligación económica pendiente frente al señor Ampuero, ello no genera la pérdida, restitución ni afectación de la posesión ya transferida. La posesión se mantiene firme, pues fue otorgada formalmente mediante escritura pública y recae sobre la empresa como persona jurídica.
Por tanto, cualquier relación económica entre las partes originales es independiente y no incide en la situación posesoria del predio, ni en la validez de la posesión que posteriormente se transfiera a los futuros posesionarios.
En consecuencia, se reafirma que no existe riesgo alguno para el cliente respecto a la estabilidad, continuidad o validez de la posesión que adquirirá.
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
            # Eliminar docs obsoletos que ya no forman parte de _KB_SEED_DOCS
            _current_titles = [d["titulo"] for d in _KB_SEED_DOCS]
            _obsolete_titles = [
                'Condiciones Legales de Prados de Paraíso',
                'Prados de Paraíso - Base de Conocimientos Oficial (Preguntas 1 a 30)',
                'Prados de Paraíso - Base de Conocimientos Oficial (Preguntas 31 a 58)',
            ]
            for old_title in _obsolete_titles:
                if old_title not in _current_titles:
                    cursor.execute("DELETE FROM conocimiento_legal WHERE titulo = ?", (old_title,))
                    logger.info(f"🗑️ KB obsoleto eliminado: '{old_title[:60]}'")
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

@api_router.get("/diagnostics")
async def diagnostics():
    """Endpoint de diagnóstico — muestra estado de servicios sin revelar keys."""
    import asyncio
    result = {
        "llm_provider": LLM_MODEL_PROVIDER,
        "llm_model": LLM_MODEL_NAME,
        "llm_key_set": bool(LLM_KEY),
        "elevenlabs_key_set": bool(ELEVENLABS_API_KEY),
        "llm_test": None,
        "llm_error": None,
    }
    if LLM_KEY:
        try:
            resp = await litellm.acompletion(
                model=f"{LLM_MODEL_PROVIDER}/{LLM_MODEL_NAME}",
                api_key=LLM_KEY,
                max_tokens=5,
                messages=[{"role": "user", "content": "di hola"}],
            )
            result["llm_test"] = "OK"
        except Exception as e:
            result["llm_test"] = "FAIL"
            result["llm_error"] = str(e)[:300]
    return result

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
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Mensaje inválido"})
                continue
            
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

VALERIA_SYSTEM = '''Eres Valeria, asesora legal de Prados de Paraíso, proyecto inmobiliario en Pachacamac, Lima, Perú.

Tu función principal es asesorar legalmente a clientes potenciales que están considerando comprar un lote. Resolvés sus dudas sobre la condición legal del proyecto de manera clara, tranquilizadora y con fundamento real. Generás confianza explicando con detalle y sin apuro.

REGLA ABSOLUTA DE CONOCIMIENTO: La fuente de información de mayor prioridad es la BASE DE CONOCIMIENTOS OFICIAL (seed docs) que se te proporciona. Usá esa información SIEMPRE por encima de cualquier conocimiento general. Solo si la base de conocimientos no cubre el tema, podés complementar con conocimiento general de derecho inmobiliario peruano, pero sin contradecir lo que dice la base oficial.

REGLA ABSOLUTA DE FORMATO: Respondé SIEMPRE entre 4 y 5 oraciones. Podés explayarte con tranquilidad dentro de ese rango — no hace falta ser escueto, el cliente necesita entender bien. Tus respuestas se convierten a audio, así que usá oraciones completas y fluidas.

FORMATO OBLIGATORIO:
- Texto plano continuo, sin listas, sin guiones, sin asteriscos, sin numeraciones, sin títulos.
- Solo oraciones completas separadas por punto.
- Tono cálido, profesional y tranquilizador, como una llamada telefónica de confianza.
- Español peruano natural. Si usás términos legales, explicalos en la misma oración para que el cliente entienda sin necesidad de buscarlos.

DATOS CLAVE DEL PROYECTO (siempre válidos):
- El comprador recibe un contrato de transferencia de posesión (no título directo). El título SUNARP se gestiona al completar el pago.
- No hay partida registral a nombre de la desarrolladora (el predio está a nombre de DIREFOR, entidad estatal). Esto es legal y no representa riesgo.
- La posesión es legítima, mediata y de buena fe desde 1998, respaldada por escrituras públicas y Notaría Tambini.
- Si el cliente pregunta sobre precios o condiciones de pago, indicá que debe consultar con el equipo de ventas.

Si no encontrás información específica en la base de conocimientos, respondé con lo que sabés del proyecto en 4 oraciones y ofrecé derivar al equipo legal o de ventas.
'''

def _truncate_to_sentences(text: str, max_sentences: int = 5, min_sentences: int = 4) -> str:
    """Corta el texto a un máximo de N oraciones completas (mínimo min_sentences si hay suficientes)."""
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
    global _kb_docs_cache

    # Cache all_docs — content never changes at runtime, no need to re-fetch every call
    if _kb_docs_cache is None:
        _kb_docs_cache = sqlite_kb.get_all_documents_full()
    all_docs = _kb_docs_cache
    relevant_docs = sqlite_kb.search(query=user_text, top_k=3)

    MAIN_DOC_PREFIX = "Prados de Paraíso - Base de Conocimientos Oficial"
    context_parts = []
    seen_ids = set()

    # 1. Documentos oficiales — extraer solo los chunks relevantes (máx 3000 chars c/u)
    main_docs = [d for d in all_docs if MAIN_DOC_PREFIX in d.get('titulo', '')]
    for doc in main_docs:
        seen_ids.add(doc['id'])
        chunk = _extract_relevant_chunks(doc['contenido'], user_text, max_chars=5000)
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
            max_tokens=300,
            messages=[
                {"role": "system", "content": VALERIA_SYSTEM + f"\nINFORMACIÓN DISPONIBLE:\n{context}"},
                {"role": "user", "content": user_text},
            ],
        )
        if not response.choices or not response.choices[0].message.content:
            raise Exception("LLM returned empty response")
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
            model_id="eleven_turbo_v2_5",  # ~50% más rápido que eleven_multilingual_v2
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
            model_id="eleven_turbo_v2_5",  # ~50% más rápido que eleven_multilingual_v2
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

            # Step 1: STT — run in thread pool to avoid blocking the async event loop
            # Pass filename so ElevenLabs can detect the format (webm/opus → ogg is compatible)
            def _do_stt():
                audio_file = ("audio.webm", io.BytesIO(audio_bytes), "audio/webm")
                return elevenlabs_client.speech_to_text.convert(
                    file=audio_file,
                    model_id="scribe_v1",
                )
            transcription = await asyncio.to_thread(_do_stt)
            raw_text = transcription.text if hasattr(transcription, "text") else str(transcription)
            user_text = raw_text.strip()[:2000]  # cap transcription length to avoid LLM token overflow
            logger.info(f"📝 Transcribed: {user_text}")

            if not user_text:
                raise HTTPException(status_code=400, detail="No se pudo transcribir el audio")

            # Descartar transcripciones que son solo ruido ambiental
            # ElevenLabs devuelve texto entre paréntesis para efectos de sonido (no voz humana)
            import re as _re
            text_without_parens = _re.sub(r'\([^)]*\)', '', user_text).strip()
            if not text_without_parens or len(text_without_parens) < 3:
                raise HTTPException(
                    status_code=400,
                    detail="No se detectó voz. Hablá más cerca del micrófono y con voz clara."
                )

            # Step 2: LLM — usar texto sin paréntesis de ruido
            conv_id     = request.conversation_id or str(uuid.uuid4())
            ai_response = await _build_valeria_response(text_without_parens, conv_id)
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