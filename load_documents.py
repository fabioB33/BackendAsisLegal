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
En Prados de Paraíso ofrecemos la transferencia de posesión de lotes. Esto significa que, al adquirir un lote con nosotros, obtienes el derecho de uso, disfrute y control efectivo del terreno.

Es importante que tengas claro que la condición legal actual del predio es de posesión, no de propiedad titulada inscrita en Registros Públicos a nombre de la empresa. Sin embargo, nuestra posesión es sólida y segura porque:

La empresa ejerce la posesión del terreno desde mil novecientos noventa y ocho, respaldada por escrituras públicas.

Contamos con el reconocimiento de la Municipalidad de Santa María a través de las cartillas municipales (Predio Rústico y Hoja Resumen).

Formalizamos tu adquisición mediante un Contrato de Transferencia de Posesión elevado a Escritura Pública ante notario.

Adicionalmente, contamos con la Resolución N.º 00202-2026-SOPCFPUR/MDSM, que aprueba el cambio de zonificación, reconociendo el área del proyecto como Zona Residencial de Densidad Media (RDM – R3). Este importante avance permite la ejecución de áreas recreativas, parques y espacios diversos, que forman parte del concepto integral de la comunidad sostenible de Villa Eco-Sostenible.

En resumen, te ofrecemos una oportunidad de inversión sólida, con respaldo legal, reconocimiento municipal y proyección urbana, dentro de una comunidad que ya cuenta con más de ochocientos clientes satisfechos y que continúa consolidándose como un proyecto sostenible y con visión de crecimiento.

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

15. ¿Cuál es el estado legal del proyecto y el proceso de adquisición de lote?
Estado Legal del Proyecto: La condición actual del proyecto es de posesión, no de propiedad titulada. Esta posesión está respaldada documentalmente por Escrituras Públicas que datan desde mil novecientos noventa y ocho y cuenta con un reconocimiento municipal indirecto a través de las cartillas de Predio Rústico (PR) y Hoja Resumen (HR), lo que nos permite cumplir con nuestras obligaciones tributarias.

Adicionalmente, contamos con la Resolución que aprueba el cambio de zonificación, reconociendo el área del proyecto como Zona Residencial de Densidad Media (RDM – R3). Este importante avance permite la ejecución de áreas recreativas, parques y espacios diversos, que forman parte del concepto integral de la comunidad sostenible de Villa Eco-Sostenible.

Proceso de Adquisición: Para adquirir un lote con nosotros, el proceso se basa en la transferencia de esta posesión y consta de tres pasos principales:

Firma del Contrato: Se firma un Contrato de Transferencia de Posesión.

Trámite Notarial: Para tu seguridad jurídica, este contrato se puede elevar a Escritura Pública ante notario, dándole fecha cierta y plena fuerza legal.

Entrega: Una vez completados los pagos y trámites, se te hace la entrega física del lote para que puedas ejercer tu derecho de uso y disfrute.

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

28. ¿Qué riesgos existen al adquirir el lote por transferencia de posesión?
Al adquirir un lote mediante transferencia de posesión, el riesgo principal que debes considerar es que no estás adquiriendo la propiedad inscrita en Registros Públicos, sino únicamente el derecho de uso y disfrute del terreno. Esto implica que la obtención del título de propiedad no es automática; dependerá de que tú, como adquiriente, inicies y asumas un proceso de saneamiento de manera personal en el futuro.

Además, es importante tener claro que la empresa no garantiza la titulación final, sino la entrega de una posesión documentada y formalizada mediante contrato. Sin embargo, para tu tranquilidad, esta posesión que te transferimos es sólida, ya que está respaldada por escrituras públicas desde mil novecientos noventa y ocho y cuenta con reconocimiento municipal.

29. ¿La empresa garantiza que no habrá problemas legales en el futuro?
Garantiza contractualmente la entrega de la posesión en la condición legal informada. No puede garantizar escenarios futuros externos, pero entrega una posesión debidamente respaldada para enfrentar contingencias.

30. ¿Qué obligaciones asume el adquirente?
Pagar el precio pactado, cumplir las condiciones de entrega, asumir trámites notariales de la Escritura Pública y cumplir el reglamento interno del proyecto.
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
