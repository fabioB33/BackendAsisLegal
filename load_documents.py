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
            "titulo": "Prados de Paraíso - Base de Conocimientos Oficial (Preguntas 1 a 30)",
            "contenido": """BASE DE CONOCIMIENTOS OFICIAL - PRADOS DE PARAÍSO

1. ¿Qué es Prados del Paraíso?
Prados de Paraíso es una marca comercial de Desarrolladora Santa María del Norte SAC, dedicada a desarrollar proyectos inmobiliarios con un enfoque ecológico y sostenible. Busca innovar en el sector, combinando eficiencia ambiental, diseño funcional y calidad de vida. Responde a la demanda de estilos de vida responsables y un desarrollo inmobiliario consciente.

2. ¿Qué proyectos tiene Prados del Paraíso?
Prados de Paraíso actualmente cuenta con dos proyectos. Uno de ellos ya ha sido entregado con éxito y se llama "Prados de Paraíso – Casa Huerto Ecológico". El segundo proyecto, que se encuentra en desarrollo, es "Prados de Paraíso Villa Eco-Sostenible".
Ambos proyectos reflejan el compromiso de la marca con un enfoque ecológico y sostenible, ofreciendo oportunidades de inversión segura y con visión de futuro.

3. ¿Dónde se ubica el proyecto Villa Eco- Sostenible?
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
Sí, puedes construir en el lote, sujeto a las normativas locales y el contrato de posesión.

11. ¿La escritura me hace propietario?
No, la escritura pública de transferencia de posesión no le hace propietario en el sentido registral. Formaliza la transferencia de la posesión y le otorga un respaldo sobre ella. Para ser propietario y que su nombre aparezca en Registros Públicos, se requiere un proceso adicional de saneamiento.

12. ¿La empresa responde por el lote?
Sí, la empresa responde por el lote en el sentido de que garantiza la transferencia de la posesión del predio. Desarrolladora Santa María del Norte S.A.C. formaliza esta transferencia mediante un Contrato de Transferencia de Posesión, el cual puede elevarse a Escritura Pública a solicitud del cliente, otorgando el derecho de uso y disfrute del lote asignado.
Es importante aclarar que la empresa garantiza la entrega de la posesión en la condición legal informada (respaldada por documentos históricos), pero no responde por situaciones externas futuras, como desastres naturales o actos de terceros, ni ofrece indemnizaciones económicas por pérdida de posesión ajena a su incumplimiento contractual.

13. ¿Qué planos entregarán a la firma del contrato de transferencia de posesión?
Al momento de la firma del contrato de transferencia de posesión, se te proporcionarán tres documentos técnicos importantes: el plano de ubicación, la memoria descriptiva y los planos perimétricos.
Estos documentos son fundamentales porque delimitan físicamente el área sobre la cual ejercerás tu derecho de posesión, permitiéndote identificar con claridad la ubicación y las medidas exactas de tu lote.

14. ¿Cómo se respalda legalmente la posesión o qué documentos se entregan?
La empresa cuenta con documentos que respaldan su posesión desde 1998: Escrituras Públicas y Cartillas municipales (PR y HR). Al cliente se le entrega: Contrato de transferencia de posesión (documento fundamental) y Pagos de tributos municipales (PR y HR) que demuestran el cumplimiento de obligaciones fiscales.

15. ¿Cuál es el estado legal del proyecto y el proceso de adquisición de lote?
Estado Legal del Proyecto: La condición actual del proyecto es de posesión, no de propiedad titulada. Esta posesión está respaldada documentalmente por Escrituras Públicas que datan desde mil novecientos noventa y ocho y cuenta con un reconocimiento municipal indirecto a través de las cartillas de Predio Rústico (PR) y Hoja Resumen (HR), lo que nos permite cumplir con nuestras obligaciones tributarias.

Adicionalmente, contamos con la Resolución que aprueba el cambio de zonificación, reconociendo el área del proyecto como Zona Residencial de Densidad Media (RDM – R3). Este importante avance permite la ejecución de áreas recreativas, parques y espacios diversos, que forman parte del concepto integral de la comunidad sostenible de Villa Eco-Sostenible.

Proceso de Adquisición: Para adquirir un lote con nosotros, el proceso se basa en la transferencia de esta posesión y consta de tres pasos principales:

Firma del Contrato: Se firma un Contrato de Transferencia de Posesión.

Trámite Notarial: Para tu seguridad jurídica, este contrato se puede elevar a Escritura Pública ante notario, dándole fecha cierta y plena fuerza legal.

Entrega: Una vez completados los pagos y trámites, se te hace la entrega física del lote para que puedas ejercer tu derecho de uso y disfrute.

16. ¿Qué documentos entrega la empresa al transferir la posesión?
Para formalizar la transferencia y brindarte seguridad jurídica sobre tu lote en Prados de Paraíso, la empresa te entregará varios documentos importantes. Recibirás el Contrato de Transferencia de Posesión, que es el documento principal que te otorga el derecho de uso y disfrute del lote. Además, se te facilitarán las Escrituras Públicas que respaldan la posesión legítima del predio por parte de la empresa desde mil novecientos noventa y ocho, y las Cartillas Municipales (Predio Rústico y Hoja Resumen) que demuestran el cumplimiento de las obligaciones tributarias.

17. ¿Qué significa una transferencia de posesión?
Una transferencia de posesión significa que adquieres el uso, disfrute y control de un lote, lo que te permite ejercer un poder de hecho sobre el bien, como ocuparlo, cercarlo o construir en él. Este derecho está respaldado por un Contrato de Transferencia de Posesión que se eleva a Escritura Pública para mayor seguridad jurídica.
Es importante entender que esto es diferente de la propiedad, ya que la propiedad implica ser el dueño legal absoluto con tu nombre inscrito en los Registros Públicos. La posesión es un derecho real reconocido por el Código Civil, que te otorga el control físico del terreno.

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

23. ¿Existe el riesgo de que DIREFOR inicie una demanda de reivindicación o desalojo?
Entiendo perfectamente tu preocupación; es una consulta muy razonable al evaluar una inversión de este tipo. En el proyecto Prados de Paraíso, la seguridad jurídica se sustenta en que la empresa ejerce una posesión desde el año mil novecientos noventa y ocho.
Si bien la empresa no cuenta con una partida registral de propiedad a su nombre, sí ejerce y administra el terreno de manera efectiva y documentada. Esta posesión se encuentra respaldada por escrituras públicas que acreditan nuestra presencia desde mil novecientos noventa y ocho, además de documentación municipal (Predio Rústico y Hoja Resumen) que evidencia el cumplimiento de obligaciones tributarias y el reconocimiento de la posesión por parte de la Municipalidad de Santa María.
Adicionalmente, contamos con la Resolución que aprueba el cambio de zonificación, reconociendo el área del proyecto como Zona Residencial de Densidad Media (RDM – R3). Este importante avance permite la ejecución de áreas recreativas, parques y espacios diversos, que forman parte del concepto integral de la comunidad sostenible de Villa Eco-Sostenible. Además este reconocimiento municipal representa un respaldo institucional importante, ya que confirma la posesión del predio, brindando mayor formalidad y seguridad jurídica a los futuros adquirentes, respaldando la formalidad de El Proyecto y la protección de su inversión.
Es importante precisar que una eventual demanda de reivindicación o desalojo no prospera automáticamente cuando existe una posesión antigua, pública y ejercida de buena fe, como en este caso. La solidez de la posesión, el sustento documental y el acompañamiento legal existente reducen significativamente la probabilidad de acciones de este tipo.

24. ¿La posesión me permite defenderme frente a terceros?
Sí. El Código Civil reconoce la posesión como un derecho real. Además, el Art. 898 permite la "suma de plazos posesorios", sumando su tiempo al de la empresa desde 1998 para fortalecer su defensa legal.

25. ¿Por qué la empresa no sanea primero el terreno?
Es una decisión estratégica para ofrecer una alternativa comercialmente viable basada en la transferencia de posesión legítima. La empresa es transparente al informar que no vende propiedad saneada, permitiendo que el adquirente decida si desea realizar el saneamiento por su cuenta posteriormente.

26. ¿Existe hoy algún juicio, denuncia o problema legal activo sobre este terreno?
Basándome en la información legal disponible sobre el proyecto Prados de Paraíso, puedo confirmarte que no existe ningún juicio, denuncia o problema legal activo sobre el terreno. Aunque la partida registral figura a nombre de DIREFOR, una entidad del Estado, esto no implica que haya un conflicto, ya que nuestra posesión está respaldada por escrituras públicas desde mil novecientos noventa y ocho. El proyecto se desarrolla en un marco de transparencia, sin litigios que pongan en riesgo tu adquisición de la posesión.

27. Si yo compro hoy el lote y mañana hay un problema legal con el terreno, ¿qué respaldo real tengo como adquiriente?
Lo primero que debes saber es que la condición legal del predio que adquieres es la posesión, no la propiedad. Esto significa que nuestra empresa te garantiza la entrega de la posesión del lote, lo que te otorga el derecho de uso y disfrute del mismo. Esta transferencia se formaliza mediante un Contrato de Transferencia de Posesión.
Tu respaldo como adquirente se basa en este Contrato de Transferencia de Posesión, que te otorga el derecho de uso y disfrute. Además, la posesión de nuestra empresa está documentada y respaldada por escrituras públicas que datan desde mil novecientos noventa y ocho, y la Municipalidad de Santa María reconoce nuestra posesión de manera indirecta a través de la emisión de cartillas municipales.

28. ¿Qué riesgos existen al adquirir el lote por transferencia de posesión?
Al adquirir un lote mediante transferencia de posesión, el riesgo principal que debes considerar es que no estás adquiriendo la propiedad inscrita en Registros Públicos, sino únicamente el derecho de uso y disfrute del terreno. Esto implica que la obtención del título de propiedad no es automática; dependerá de que tú, como adquiriente, inicies y asumas un proceso de saneamiento de manera personal en el futuro.

Además, es importante tener claro que la empresa no garantiza la titulación final, sino la entrega de una posesión documentada y formalizada mediante contrato. Sin embargo, para tu tranquilidad, esta posesión que te transferimos es sólida, ya que está respaldada por escrituras públicas desde mil novecientos noventa y ocho y cuenta con reconocimiento municipal.

29. ¿La empresa garantiza que no habrá problemas legales en el futuro?
Garantiza contractualmente la entrega de la posesión en la condición legal informada. No puede garantizar escenarios futuros externos, pero entrega una posesión debidamente respaldada para enfrentar contingencias.

30. ¿Qué obligaciones asume el adquirente?
Al adquirir un lote en Prados del Paraíso mediante transferencia de posesión, asumes varias obligaciones importantes que están detalladas en el contrato. Principalmente, te comprometes a pagar el precio pactado por la transferencia, ya sea al contado o siguiendo el cronograma de pagos establecido.
Además, debes cumplir con las condiciones para que se te entregue la posesión, lo cual incluye la cancelación total del valor del lote. También serás responsable de asumir los trámites notariales y administrativos que origine la Escritura Pública del Contrato de Transferencia, así como cumplir con el reglamento interno del proyecto y las normas sobre el uso del lote.
"""
        },
        {
            "titulo": "Prados de Paraíso - Base de Conocimientos Oficial (Preguntas 31 a 58)",
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
Una vez realizada la transferencia de la posesión del lote, las obligaciones de la empresa se limitan estrictamente a lo establecido en el contrato. Principalmente, la empresa se compromete a:
Entregar la posesión del lote en la condición legal que se te informó previamente.
Proporcionarte toda la documentación posesoria que sustenta la transferencia realizada.
Cumplir con cualquier obligación contractual que pudiera haber quedado pendiente, si correspondiera.

37. ¿La empresa mantiene la administración sobre áreas recreativas?
La empresa asume la gestión inicial necesaria para la organización del proyecto. Sin embargo, la administración y el mantenimiento de las áreas recreativas pueden ser asumidos posteriormente por una asociación. Esto se realizará conforme a lo previsto en el reglamento interno y a medida que se consolide el proyecto.

38. ¿Existen contingencias penales asociadas al modelo de negocio?
De acuerdo con la naturaleza del proyecto y lo establecido contractualmente, no existen contingencias penales inherentes al modelo de negocio de Prados de Paraíso.
Esto se debe a que:
Figura Legal Reconocida: El proyecto se basa en la transferencia de posesión, una figura reconocida por el ordenamiento jurídico peruano.
Respaldo Documental: Nuestra posesión está respaldada por documentación formal y Escrituras Públicas que datan desde 1998.
Transparencia: Todo el proceso se realiza de manera transparente, con asesoría legal y notarial, diferenciando claramente la posesión de la propiedad.

39. ¿Qué respaldo real tiene el cliente si surge un conflicto?
1. Posesión histórica desde 1998. 2. Asesoría de DS Casahierro Abogados y Notaría Tambini. 3. Entrega de toda la documentación probatoria para defensa o saneamiento.

40. ¿Qué es DIREFOR y por qué figura como propietario?
Es una entidad estatal. Aparece como titular debido a la Ley 29618 (2010), que registró a nombre del Estado terrenos sin dueño inscrito. Esto no invalida la posesión legítima de la empresa iniciada en 1998.

41. ¿Es legal transferir la posesión de un terreno del Estado?
Sí, la legislación peruana reconoce la posesión como una situación jurídica protegida, que es distinta y diferente al derecho de propiedad. En Prados de Paraíso, lo que se transfiere es la posesión del terreno, no la propiedad. Nuestra empresa ejerce una posesión anterior a la inscripción estatal, debidamente documentada, y transfiere esa situación posesoria mediante un Contrato de Transferencia de Posesión.

42. ¿Qué sucede si se revierte la posesión al Estado?
No hay procesos activos para ello. La inscripción de DIREFOR no implica pérdida automática de la posesión documentada que se ejerce desde 1998.

43. ¿La municipalidad reconoce oficialmente el proyecto?
Sí, de manera indirecta mediante la emisión de cartillas PR y HR a nombre de la empresa, lo que permite el pago de tributos y valida la actividad en el predio.

44. ¿Cómo impacta la ley que prohíbe la prescripción adquisitiva de inmuebles contra el Estado?
La Ley número veintinueve mil seiscientos dieciocho, promulgada en dos mil diez, prohíbe que los bienes inmuebles de dominio privado estatal sean adquiridos por particulares mediante prescripción adquisitiva. Esto significa que ya no se puede reclamar la propiedad de terrenos estatales solo por haberlos poseído durante mucho tiempo a partir de esa fecha.
Sin embargo, en el caso de Prados de Paraíso, la empresa cuenta con veintisiete años de posesión, la cual se inició antes de que esta ley entrara en vigor. Por lo tanto, la legitimidad de la posesión transferida a los clientes se mantiene, ya que la ley no invalida la posesión histórica que ya existía. En resumen, la ley protege al Estado de nuevas reclamaciones, pero no afecta las posesiones preexistentes.

45. ¿La empresa acompaña judicialmente al cliente si hay alguna contingencia legal?
Entiendo tu pregunta. En caso de que enfrentes una contingencia legal o decidas iniciar un proceso de formalización de tu lote, la gestión y representación legal corresponde al cliente. La empresa te proporcionará toda la documentación probatoria disponible para respaldar tu caso y facilitar tu defensa, pero la representación ante un juez debe ser realizada por tu propio abogado.

46. ¿La empresa indemnizará en caso de pérdida de posesión?
La empresa no asume responsabilidad económica ni ofrece una indemnización específica por la pérdida de la posesión si esta es causada por hechos externos o ajenos al incumplimiento del comprador.
Lo que la empresa garantiza es la entrega de una posesión documentada y formalizada mediante contrato, respaldada por la documentación histórica que posee desde mil novecientos noventa y ocho. Es decir, su compromiso es entregarte el lote con el respaldo legal de su posesión, pero no cubre contingencias futuras fuera de su control.

47. ¿Se puede individualizar la posesión por cada lote?
¡Claro que sí! Cuando firmas el Contrato de Transferencia de Posesión, este documento delimita y asigna el derecho de uso y disfrute exclusivo sobre un lote determinado dentro del proyecto. Esto significa que tú tienes el control físico y el derecho a usar y disfrutar ese espacio concreto, cercarlo o construir en él.

48. ¿El adquirente podría ser demandado directamente ante un posible proceso judicial iniciado por el Estado?
Sí, como adquirente de la posesión, usted sería la parte directamente involucrada en cualquier proceso judicial que el Estado pudiera iniciar. Sin embargo, es importante destacar que la posesión que recibe está respaldada por documentación histórica y escrituras públicas desde mil novecientos noventa y ocho. Esto le brinda una garantía sobre la posesión de su lote, permitiéndole usar y disfrutar su inversión con tranquilidad y confianza.

49. ¿Qué pasa si el proyecto no logra consolidarse?
Usted seguirá manteniendo la posesión, uso y disfrute de su lote específico basado en la antigüedad de la posesión transferida.

50. ¿El contrato me protege frente a cualquier contingencia legal?
El contrato está diseñado principalmente para regular la transferencia de la posesión y las obligaciones de pago, asegurando que usted reciba la posesión de su lote con el respaldo de documentos históricos. Si bien le brinda seguridad sobre la posesión física y la documentación que acredita su derecho de ocupación, no cubre situaciones externas. Esto incluye litigios con terceros o con el Estado que puedan surgir en el futuro.

51. ¿La empresa responde económicamente frente a la pérdida de la posesión del proyecto?
La empresa no asume responsabilidad económica por la pérdida de la posesión si esta es causada por hechos externos o ajenos al incumplimiento del comprador. Es decir, la empresa respalda la posesión que te transfiere, pero no te indemnizará económicamente por causas que no sean su incumplimiento contractual.

52. ¿Las cartillas PR y HR están a nombre de mi lote específico?
No, las cartillas PR (Predio Rústico) y HR (Hoja Resumen) no estarán a nombre de su lote específico de forma individual. Estos tributos municipales se gestionan sobre el predio matriz, es decir, sobre la propiedad principal del proyecto.
Esto ocurre mientras no exista una individualización administrativa por cada lote. La empresa le entregará estos documentos que demuestran el cumplimiento de las obligaciones tributarias del predio general.

53. ¿Mi lote tendrá su propia cartilla municipal?
Inicialmente no, pero la empresa se compromete a realizar el trámite de Individualización Administrativa ante la Municipalidad para que cada lote cuente con su propia documentación.

54. ¿La empresa tiene Libro de Reclamaciones?
Sí, la empresa cuenta con un Libro de Reclamaciones.
Lo tenemos disponible en dos formatos para tu comodidad: Físico: En nuestras oficinas ubicadas en Calle Libertadores ciento cincuenta y cinco, Oficina trescientos dos, distrito de San Isidro. Virtual: Accesible a través de nuestra página web: web: https://pradosdeparaiso.com.pe/.

55. ¿Qué pasa si no estoy conforme con la respuesta de la empresa?
Entiendo que quieras saber qué opciones tienes si una respuesta no cumple tus expectativas.
Si no estás conforme con la respuesta inicial que te brindamos, siempre puedes continuar el diálogo a través de nuestros canales internos para solicitar una revisión adicional, una reunión de aclaración o la intervención de un área especializada. Nuestra prioridad es resolver los reclamos de manera directa, pero si tras agotar estas vías internas el resultado no es satisfactorio, mantienes tu derecho de acudir a los organismos de protección al consumidor según la normativa vigente.

56. ¿Cuáles son los plazos de atención de un reclamo?
Es una pregunta muy importante para tener claridad sobre los tiempos.
De acuerdo con el Reglamento del Libro de Reclamaciones y su modificatoria, el plazo máximo que tenemos como proveedores para atender un reclamo y brindarte una respuesta es de quince días hábiles improrrogables.

57. ¿La empresa se responsabiliza por daños externos?
La empresa no asume responsabilidad por daños ocasionados por factores externos fuera de su control, tales como desastres naturales, actos de terceros o decisiones de autoridades. La responsabilidad se limita a cumplir las obligaciones expresamente asumidas en el contrato.

58. Si la empresa deja de pagar la deuda pendiente con el señor Manuel Ampuero, ¿Eso podría hacer que yo pierda mi lote o mi derecho de posesión?
No. Desde la suscripción de la Escritura Pública por la que el señor Manuel Ampuero transfirió la posesión a favor de Desarrolladora Santa María del Norte, la empresa adquirió válidamente la posesión efectiva del terreno. Esta condición no se ve afectada por las obligaciones internas entre las partes originales. Aun en el supuesto de que la empresa incumpliera algún pago, ello no genera la pérdida ni afectación de la posesión ya transferida formalmente mediante escritura pública. Por lo tanto, no existe riesgo alguno para el cliente.

59. ¿Puedo obtener título de propiedad si pago el precio total del lote?
Entiendo tu interés en obtener un título de propiedad al realizar el pago total del lote. En el caso de Prados de Paraíso, el proyecto se desarrolla bajo la modalidad de transferencia de posesión, por lo que no se otorga título de propiedad inscrito en Registros Públicos como parte de la compra del lote. Recibirás un contrato de transferencia de posesión que acredita tu derecho de posesión sobre el lote.
La condición actual del proyecto es de posesión, no de propiedad titulada. Esta posesión está respaldada documentalmente por Escrituras Públicas que datan desde mil novecientos noventa y ocho y cuenta con un reconocimiento municipal indirecto a través de las cartillas de Predio Rústico (PR) y Hoja Resumen (HR), lo que nos permite cumplir con nuestras obligaciones tributarias.
Si deseas mayor información sobre esta modalidad o sobre el proyecto, estaré encantada de ayudarte.
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
