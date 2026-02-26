"""
Script para cargar documentos legales en SQLite
"""
from services.sqlite_knowledge import SQLiteKnowledgeBase

def load_legal_documents():
    """Carga los documentos legales en la base de datos"""
    
    print("🔄 Cargando documentos legales en SQLite...")
    
    # Inicializar SQLite
    sqlite_kb = SQLiteKnowledgeBase()
    
    # Documentos legales base
    documentos_base = [
        {
            "titulo": "Posesión Legítima en Perú",
            "contenido": """
La posesión legítima es una figura jurídica fundamental en el derecho peruano. Según el Código Civil peruano:

1. DEFINICIÓN:
La posesión es el ejercicio de hecho de uno o más poderes inherentes a la propiedad. 
El poseedor es reputado propietario, mientras no se pruebe lo contrario.

2. TIPOS DE POSESIÓN:
- Posesión inmediata: Es la que ejerce directamente el poseedor
- Posesión mediata: Es la que ejerce a través de otra persona
- Posesión legítima: Aquella que se ejerce con justo título y buena fe

3. ELEMENTOS:
- Corpus: El elemento material (tenencia física del bien)
- Animus: El elemento psicológico (intención de comportarse como propietario)

4. PROTECCIÓN LEGAL:
- El poseedor puede rechazar la violencia y repelerla con el empleo de la fuerza
- Puede ejercer las acciones posesorias (interdictos)
- Puede usucapir (adquirir por prescripción adquisitiva)

5. EN PRADOS DE PARAÍSO:
Los propietarios de terrenos en Prados de Paraíso ejercen posesión legítima cuando:
- Tienen título de propiedad
- Ejercen actos posesorios (construcción, cercado, uso)
- Pagan impuestos prediales
- No existe conflicto con terceros
            """
        },
        {
            "titulo": "Saneamiento Legal en Perú",
            "contenido": """
El saneamiento legal es el proceso mediante el cual se regulariza la situación jurídica de un inmueble:

1. QUÉ ES EL SANEAMIENTO:
Es el conjunto de procedimientos administrativos y/o judiciales destinados a:
- Formalizar la propiedad
- Inscribir el predio en Registros Públicos
- Obtener título de propiedad definitivo

2. PROCEDIMIENTOS:
A. Saneamiento Registral:
   - Rectificación de partidas registrales
   - Inscripción de actos no inscritos
   - Actualización catastral

B. Saneamiento Físico-Legal:
   - Levantamiento topográfico
   - Deslinde y amojonamiento
   - Georreferenciación

C. Prescripción Adquisitiva:
   - Ordinaria: 10 años con justo título y buena fe
   - Extraordinaria: 30 años sin necesidad de título

3. EN PRADOS DE PARAÍSO:
Los propietarios pueden sanear su propiedad mediante:
- Verificación de títulos
- Inscripción en SUNARP
- Regularización de linderos
- Obtención de certificado de zonificación
- Pago de impuestos al día

4. BENEFICIOS:
- Seguridad jurídica
- Acceso a crédito bancario
- Posibilidad de venta libre
- Protección contra invasiones
            """
        },
        {
            "titulo": "Derechos de Poderes Inherentes a la Propiedad",
            "contenido": """
Los poderes inherentes a la propiedad son derechos fundamentales del propietario:

1. DERECHO DE USO (IUS UTENDI):
- Usar el bien según su naturaleza
- Habitar en caso de vivienda
- Explotar económicamente el predio

2. DERECHO DE DISFRUTE (IUS FRUENDI):
- Obtener los frutos del bien
- Percibir las rentas
- Aprovechamiento económico

3. DERECHO DE DISPOSICIÓN (IUS ABUTENDI):
- Vender el bien
- Donarlo
- Gravarlo con hipoteca
- Destruirlo (dentro de los límites legales)

4. DERECHO DE REIVINDICACIÓN (IUS VINDICANDI):
- Recuperar el bien de quien lo posee sin derecho
- Acción reivindicatoria
- Protección registral

5. LIMITACIONES:
Estos derechos NO son absolutos, están limitados por:
- Normas de zonificación
- Protección del medio ambiente
- Derechos de vecinos (servidumbres)
- Bien común
- Seguridad pública

6. EN PRADOS DE PARAÍSO:
Los propietarios pueden:
- Construir respetando las normas urbanísticas
- Vender o traspasar sus terrenos
- Explotar económicamente (agricultura ecológica)
- Cercar y proteger su propiedad
- Heredar y disponer por testamento
            """
        },
        {
            "titulo": "Preguntas Frecuentes sobre Propiedad Legal",
            "contenido": """
PREGUNTAS FRECUENTES:

1. ¿Qué documentos necesito para acreditar mi propiedad?
R: Necesitas: Título de propiedad, partida registral de SUNARP, plano de ubicación, 
certificado de zonificación, y comprobante de pago de impuestos prediales.

2. ¿Cómo protejo mi propiedad contra invasiones?
R: Mediante: Cerco perimetral, vigilancia, inscripción en registros públicos, 
denuncia inmediata ante autoridades, y ejercicio continuo de actos posesorios.

3. ¿Puedo vender mi terreno antes de terminar el saneamiento?
R: Sí, pero es recomendable completar el saneamiento primero para:
- Obtener mejor precio
- Dar seguridad al comprador
- Facilitar el financiamiento
- Evitar futuros conflictos

4. ¿Qué es la prescripción adquisitiva y cómo me beneficia?
R: Es un modo de adquirir la propiedad por posesión continua. Beneficia porque:
- Permite formalizar propiedades informales
- Consolida la posesión de larga data
- Otorga título definitivo

5. ¿Qué impuestos debo pagar como propietario?
R: Principalmente:
- Impuesto Predial (anual)
- Arbitrios municipales
- Alcabala (al comprar)
- Impuesto a la Renta (si generas ingresos del predio)

6. ¿Puedo construir libremente en mi terreno?
R: No completamente. Debes:
- Respetar el plan de zonificación
- Obtener licencia de construcción
- Cumplir parámetros urbanísticos
- Respetar retiros y áreas libres
- No afectar el medio ambiente

7. ¿Qué hago si hay un conflicto de linderos?
R: Procedimiento:
1. Intentar acuerdo con el vecino
2. Levantamiento topográfico
3. Verificación de títulos
4. Conciliación extrajudicial
5. Proceso judicial de deslinde (última instancia)

8. ¿Cómo heredo un terreno en Prados de Paraíso?
R: Proceso:
1. Declaratoria de herederos o testamento
2. Partición de bienes
3. Inscripción en SUNARP
4. Actualización del impuesto predial
            """
        },
        {
            "titulo": "Condiciones Legales de Prados de Paraíso",
            "contenido": """
CONDICIONES LEGALES ESPECÍFICAS DE PRADOS DE PARAÍSO - PACHACAMAC, LIMA, PERÚ

1. QUÉ ES PRADOS DE PARAÍSO:
Prados de Paraíso es un proyecto inmobiliario de vivienda ecológica y sostenible ubicado en Pachacamac, Lima, Perú. Ofrece lotes para la construcción de viviendas, con un enfoque en la calidad y el desarrollo urbano. Está respaldado por Notaría Tambini y Casahierro Abogados.

2. CONDICIÓN LEGAL DEL TERRENO:
El proyecto tiene una condición legal mixta:
- 50% del terreno: Propiedad adquirida mediante compraventa de acciones y derechos, con escrituras públicas desde 1998.
- 50% restante: Terreno bajo condición de posesión legítima y mediata, ejercida de buena fe desde 1998.
El predio figura registralmente a nombre de DIREFOR (entidad estatal), pero la empresa posee legítimamente desde hace más de 25 años.

3. QUÉ RECIBE EL COMPRADOR:
El comprador recibe un contrato de transferencia de posesión (NO un título de propiedad en primera instancia). Para obtener el título de propiedad inscrito en Registros Públicos (SUNARP), el propietario debe gestionar el saneamiento legal una vez completado el pago total.

4. DIFERENCIA ENTRE PROPIEDAD Y POSESIÓN:
- Propiedad: Derecho que otorga titularidad legal inscribible en Registros Públicos (SUNARP). Requiere partida registral.
- Posesión legítima: Ejercicio de hecho de poderes inherentes a la propiedad. Reconocida y protegida por el Código Civil peruano.
La posesión de Prados de Paraíso es LEGÍTIMA, MEDIATA y de BUENA FE — la más sólida categoría posesoria.

5. PREGUNTAS FRECUENTES REALES:

Q: ¿Cuándo entregan el título de propiedad?
R: La condición legal actual es la POSESIÓN. Al comprar, se entrega contrato de transferencia de posesión. Para obtener el título de propiedad inscrito en SUNARP, el propietario debe gestionar el saneamiento legal tras completar el pago total. El equipo legal de Prados de Paraíso acompaña este proceso.

Q: ¿Tienen partida registral?
R: No existe partida registral a nombre de la desarrolladora. El predio figura a nombre de DIREFOR (entidad estatal). Esto NO representa riesgo legal ya que se posee legítimamente desde 1998, respaldado por escrituras públicas notariales.

Q: ¿Es seguro comprar sin partida registral?
R: Sí. La posesión legítima de más de 25 años, respaldada por escrituras públicas desde 1998, es un derecho real reconocido y protegido por la ley peruana. Además, el proyecto cuenta con el respaldo de Notaría Tambini y Casahierro Abogados.

Q: ¿Qué es la posesión legítima mediata?
R: Es la posesión ejercida a través de otra persona (el comprador) manteniendo el vínculo jurídico. Es legítima porque tiene justo título y buena fe. En la escala de tipos de posesión (Legítima vs Ilegítima; Mediata vs Inmediata; Buena fe vs Mala fe), Prados de Paraíso tiene la categoría más sólida: Posesión Legítima Mediata de Buena Fe.

Q: ¿Cuáles son los tipos de posesión?
R: Posesión Legítima (con justo título) e Ilegítima (sin título). Dentro de la ilegítima: de Buena Fe (quien cree tener derecho) y de Mala Fe (sabe que no tiene derecho). También existe la posesión Precaria (sin título ni vínculo). Prados de Paraíso: Posesión Legítima Mediata de Buena Fe.

Q: ¿Puedo construir con posesión?
R: Sí. El poseedor legítimo tiene todos los derechos de uso, disfrute y construcción sobre el terreno. Puede edificar, cercar, habitar y ejercer todos los actos propios del propietario.

Q: ¿Cuánto cuesta y cómo se paga?
R: Los precios y condiciones de pago se consultan con el equipo de ventas. Existen opciones de financiamiento directo y facilidades de pago.

6. PROCESO DE COMPRA:
1. Separación del lote con pago inicial
2. Verificación de documentos legales
3. Firma de contrato de transferencia de posesión
4. Pago en cuotas según plan acordado
5. Gestión de saneamiento para título SUNARP (al completar pago)
6. Inscripción definitiva en Registros Públicos

7. RESPALDO LEGAL:
- Notaría Tambini: Formalización de actos jurídicos
- Casahierro Abogados: Asesoría legal especializada
- Escrituras públicas desde 1998
- Más de 25 años de posesión continua y pacífica
            """
        }
    ]
    
    # Cargar documentos base
    print("\n📄 Cargando documentos base...")
    for doc in documentos_base:
        sqlite_kb.add_document(
            titulo=doc["titulo"],
            contenido=doc["contenido"],
            metadata={"source": "base_knowledge", "type": "legal_info"}
        )
        print(f"  ✓ {doc['titulo']}")
    
    print(f"\n✅ {len(documentos_base)} documentos cargados exitosamente")
    print(f"📊 Total documentos en base: {sqlite_kb.count_documents()}")
    
    # Prueba de búsqueda
    print("\n🔍 Prueba de búsqueda...")
    results = sqlite_kb.search("¿Qué es posesión legítima?", top_k=2)
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. {result['titulo']}")
        print(f"     Score: {result['score']:.4f}")
        print(f"     Contenido: {result['contenido'][:150]}...")

if __name__ == "__main__":
    load_legal_documents()
