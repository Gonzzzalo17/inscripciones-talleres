# Iteración de la Sesión 04

## Equipo y proyecto
* **Proyecto:** P03 — Inscripciones a talleres y listas de espera
* **Integrantes:** Andrea Trujillo Antezana, Gonzalo Andres Cárdenas Vargas, Santiago Arauz Peña
* **Fecha de la iteración:** 26 al 28 de septiembre de 2026.  Este registro incluye la retroalimentación del cliente y el estado final del backlog.
## Backlog ordenado
| Orden | ID | Capacidad | ¿A quién ayuda y para qué? | Duda pendiente en la sesión 4 | Cómo se resolvió | Estado final |
|---|---|---|---|---|---|---|
| 1 | PB-01 | Crear taller con cupo máximo e inscribir participante (con control de cupos, lista de espera y rechazo por duplicado) | Ayuda al Coordinador a ofertar talleres y al Participante a inscribirse, garantizando el control y evitando registros repetidos. | ¿Se deben validar formatos de CI extranjeros o con letras? | Ya no se usa el CI: cada participante se identifica con su código universitario, que debe figurar en el padrón de estudiantes. | Terminado (CU-01, CU-04) |
| 2 | PB-02 | Consultar disponibilidad de talleres y estado de ocupación | Ayuda al Operador y al Participante a ver los cupos disponibles antes de solicitar una inscripción. | Ninguna | El cliente aclaró que las «consultas» del operador son búsquedas: qué talleres hay, si hay espacio, quiénes están inscritos y de qué es el taller. | Terminado (CU-03, CU-08, CU-13) |
| 3 | PB-03 | Cancelar inscripción y reasignar la plaza a la lista de espera | Ayuda al Participante a liberar su cupo y al sistema a promover al siguiente en espera. | ¿La promoción desde la lista de espera debe ser automática o requerir confirmación? | Automática y sin confirmación; la persona promovida ve el aviso en pantalla. | Terminado (CU-05) |
| 4 | PB-04 | Modificar o corregir cupos de un taller conservando historial | Ayuda al Coordinador a ajustar la capacidad del aula ante imprevistos sin perder el registro de cambios. | Ninguna | Solo se editan fechas y cupo, con un motivo elegido de una lista;el cupo va de 4 a 40 y no puede bajar de la cantidad de confirmados, para que nadie pierda su plaza. | Terminado (CU-06) |
| 5 | PB-05 | Mostrar listas de confirmados, lista de espera y cancelaciones | Ayuda al Coordinador y al Operador a conocer quién tiene plaza y por qué alguien sigue esperando. | Ninguna | El cliente quitó el rol Instructor: estas listas las consultan el operador y el coordinador de sus talleres. | Terminado (CU-08, CU-09, CU-12, CU-13) |

* **Razón de la primera prioridad:** Se definió PB-01 como prioridad absoluta porque la creación del taller y la gestión inicial de inscripciones (controlando si hay vacantes, si pasa a lista de espera o si es un duplicado) constituyen la regla de negocio central del sistema. Sin esta capacidad mínima funcionando en código, no existen datos reales sobre los cuales consultar disponibilidad, procesar cancelaciones o generar reportes.

## Objetivo y alcance
* **Objetivo de la iteración:** al finalizar, el Coordinador podrá crear un taller indicando su nombre, categoría y cupo máximo mediante la función `crear_taller`, que genera un identificador único con formato UUID. Además, se podrá inscribir a un participante por su CI mediante `registrar_inscripcion`, que le asigna el estado CONFIRMADO si hay vacante, EN_ESPERA si el taller llegó a su cupo máximo, o lanza `ValueError` si el cupo es menor o igual a cero o si el participante ya está inscrito en ese taller.
* **Límites:** solo Python, listas en memoria y pytest; sin base de datos, sin pantallas, sin cancelaciones ni reportes.
* **Resultado:** el objetivo se cumplió y se demostró sobre `main` (ver Verificación e integración).
* **Cómo evolucionó después:** el UUID se reemplazó por un código legible (`TAL-DAN-01`), el CI por el código universitario del padrón, y las listas en memoria por Django con base de datos. La primera versión se conserva en `version_inicial/reglas_sesion04.py`.

## Aclaraciones del cliente
| Pregunta | Respuesta del cliente | Efecto sobre el comportamiento esperado |
|---|---|---|
| ¿Creamos un nuevo repositorio o se usa el de la Sesión 03? | Debe ser un repositorio nuevo, que se usará hasta el final de la materia. | Se creó el repositorio oficial del proyecto respetando la estructura base (`proyecto/`, `tests/`, `docs/`). |
| ¿Todos los usuarios pueden crear talleres o solo los coordinadores? | Queda a criterio del equipo para este primer paso, como propuesta de diseño. | Se asumió el rol de Coordinador en `crear_taller`. Más adelante el cliente definió que el coordinador solicita sus talleres y el operador los aprueba o crea directamente. |
| ¿Bajo qué criterio controlamos las identificaciones únicas (carnet o correo) para evitar duplicados? | A criterio del equipo; están presentando la propuesta al cliente para que la apruebe. | Se usó el CI (`ci_participante`) para rechazar inscripciones duplicadas. Más adelante se cambió por el código universitario del padrón. |

Las preguntas hechas al cliente después de esta sesión están en la sección **Retroalimentación** y con más detalle, en [sesion-06-requisitos.md](sesion-06-requisitos.md).

## Ejemplos de aceptación
| Caso | Estado inicial y entrada | Resultado esperado | Regla que lo justifica |
|---|---|---|---|
| **Uso normal** | Taller Robótica Avanzada creado con cupo máximo igual a 2 y lista de inscritos vacía. Se ejecuta la inscripción del participante con CI 1234567. | Se registra al participante con CI 1234567 con estado CONFIRMADO y el mensaje de confirmación exitosa. | Si hay vacantes y la cédula no está registrada, la plaza se otorga con estado confirmado. |
| **Rechazo o situación excepcional prevista** | Taller con cupo máximo igual a 2 y la CI 1234567 ya registrada. Se intenta inscribir de nuevo al participante con CI 1234567. | El sistema interrumpe la operación y lanza `ValueError` indicando que el participante con CI 1234567 ya está inscrito en este taller. | Se rechaza la inscripción duplicada del mismo participante en el mismo taller. |
| **Límite** | Taller con cupo máximo igual a 2 y dos confirmados (CI 1234567 y CI 8901234). Se inscribe al participante con CI 5554433. | Se registra al participante con CI 5554433 con estado EN_ESPERA y el mensaje de que el cupo está lleno. | Al llegar al cupo máximo, la solicitud pasa a la lista de espera. |

Estos tres ejemplos siguen vigentes en el sistema actual con los datos nuevos: confirmado con plaza libre, rechazo por inscripción duplicada y paso a la lista de espera con el taller lleno (CU-04). El cupo de 2 ya no es válido porque el cliente fijó un mínimo de 4.

## Plan y seguimiento
| Tarea | Personas que colaboran | Estado | Evidencia o ubicación |
|---|---|---|---|
| Crear la clase Taller con sus atributos y la función `crear_taller` con control de cupos máximos | Andrea | Terminado | `proyecto/reglas.py` (hoy `version_inicial/reglas_sesion04.py`) |
| Implementar `registrar_inscripcion` con validación de duplicados por CI y estados CONFIRMADO y EN_ESPERA | Gonzalo | Terminado | `proyecto/reglas.py` (hoy `version_inicial/reglas_sesion04.py`) |
| Escribir las pruebas en pytest para los casos normal, límite y duplicado | Santiago | Terminado | `tests/test_reglas.py` (hoy `tests/version_inicial/test_reglas_sesion04.py`) |
| Elaborar la documentación general y la estructura inicial del `README.md` | Todos los integrantes | Terminado | `README.md` |
| Consolidar el registro de la iteración, acuerdos, ejemplos y retrospectiva | Todos los integrantes | Terminado | `docs/sesion04.md` |
| PB-02 Consultar disponibilidad de talleres y estado de ocupación | Todo el equipo | Terminado en iteraciones siguientes | `inscripciones/views.py` (lista de talleres y ocupación), `inscripciones/servicios/operador.py` (`calcular_ocupacion`) |
| PB-03 Cancelar inscripción y reasignar la plaza a la lista de espera | Todo el equipo | Terminado en iteraciones siguientes | `inscripciones/servicios/operador.py` (`cancelar_inscripcion`, `promover_siguiente_en_espera`), `tests/test_cancelar.py` |
| PB-04 Modificar o corregir cupos de un taller conservando historial | Todo el equipo | Terminado en iteraciones siguientes | `inscripciones/servicios/coordinador.py` (`editar_taller`), modelo `TallerHistorial`, `tests/test_edicion_taller.py` |
| PB-05 Listas de confirmados, espera y cancelaciones | Todo el equipo | Terminado en iteraciones siguientes | Búsqueda de inscripciones, historial de cancelaciones y ocupación; `tests/test_buscar.py`, `tests/test_baneo.py` |

**Ajuste en el punto de inspección:** PB-02 y las siguientes quedaron para la próxima iteración, para cerrar primero PB-01 con sus pruebas integradas en `main`.

## Verificación e integración
* **Pruebas ejecutadas:** `python -m pytest -q` con 7 pruebas en `tests/test_reglas.py`:
  * inscripción con cupo;
  * última plaza disponible;
  * envío a espera con el taller lleno;
  * rechazo de CI duplicado;
  * rechazo de cupo cero;
  * rechazo de cupo negativo;
  * identificador único automático.
* **Resultado:** las 7 pruebas pasaron en `main` después de integrar.
* **PR:** [#1](https://github.com/Gonzzzalo17/inscripciones-talleres/pull/1) integrado el 28/09/2026. Commit demostrado: `f16696c`.
* **Dónde están hoy:** cuando el proyecto pasó a Django, esas pruebas se conservaron sin cambios en `tests/version_inicial/test_reglas_sesion04.py` como registro de esta iteración.

## Retroalimentación
Peticiones y respuestas del cliente recibidas después de la demostración (revisión de la sesión 4, entrevista de la sesión 6, consultas por mensaje y reunión sobre roles y categorías), y cómo cambió el backlog.

| Petición o respuesta del cliente | Cambio en el backlog | Dónde quedó |
|---|---|---|
| La promoción desde la espera es automática, sin que la persona confirme, con un aviso «ya estás inscrito». | PB-03 se precisó como promoción automática del primero en espera. | TAL-RF-03, CU-05 |
| Quien cancela y vuelve no recupera su lugar: entra como persona nueva (confirmado si hay cupo o al final de la espera). | Se agregó la regla de reinscripción a PB-01. | TAL-RF-04, CU-04 |
| Si el taller crece, la espera pasa a confirmada en orden; si se achica, los que sobran pasan a la espera. | PB-04 incluye el aumento de cupo con promoción. El 22/10 el cliente precisó la reducción: el cupo no puede quedar por debajo de los confirmados. | TAL-RF-07, CU-06 |
| No se puede estar en dos talleres a la misma hora. | Se agregó el choque de horario a PB-01. | TAL-RF-05, CU-04 |
| La lista de espera es el 20 % del cupo; si está llena, se rechaza la solicitud. | Se agregó el límite de la espera a PB-01. | TAL-RF-02, CU-04 |
| Se puede inscribir hasta el último minuto antes del inicio; después se rechaza. | Se agregó la validación de taller ya empezado a PB-01. | TAL-RF-01, CU-04 |
| Se puede cancelar hasta 3 horas antes del inicio. | Se agregó el plazo de cancelación a PB-03. | TAL-RF-06, CU-05 |
| El identificador del taller debe estar relacionado con su nombre en lugar de un UUID; luego indicó que debe ir según la categoría. | Se reemplazó el UUID por un código legible (`TAL-DAN-01`) que sale de la actividad del nombre; la categoría se guarda aparte y se usa para buscar. | TAL-RT-02, CU-01 |
| Quiere un historial de cancelaciones para poder banear. Regla: más de 3 cancelaciones en 72 horas bloquean 24 horas. | Nuevo elemento: **PB-06 Bloqueo por cancelaciones**. | TAL-RF-08, CU-11 |
| Mientras está bloqueado no puede inscribirse, pierde todo lo anterior y sale de las listas de espera. | Se completó PB-06. | TAL-RF-08, CU-11 |
| El administrador (operador) puede quitar el bloqueo cuando quiera; si vuelve a pasar, el bloqueo sigue siendo de 24 horas. | Se agregó levantar el bloqueo a PB-06. | TAL-RF-08, CU-12 |
| Las «consultas» del operador son búsquedas: qué talleres hay, si hay espacio, quiénes están inscritos y de qué es el taller. | PB-02 y PB-05 se precisaron como búsquedas del operador. | TAL-RF-14, CU-13 |
| Los avisos (paso de espera a confirmado, taller cancelado) basta con mostrarlos en pantalla. | Nuevo elemento: **PB-07 Avisos en pantalla**. El envío por WhatsApp quedó fuera de alcance. | TAL-RF-13, CU-10 |
| Si se cancela un taller completo, el aviso también va en pantalla. | Nuevo elemento: **PB-08 Cancelar un taller completo**. | TAL-RF-11, CU-07 |
| El cupo va de 4 a 40 personas. | Se agregó el rango a PB-01 y PB-04. | TAL-RT-03 |
| Roles: el coordinador crea, edita y solicita sus talleres y ve todo lo de sus talleres; el operador crea, edita todos, acepta o rechaza, inscribe y ve bloqueos y talleres; el participante se registra, inicia sesión, se inscribe, ve sus inscripciones y puede ser bloqueado. No hay rol Instructor. | Nuevos elementos: **PB-09 Roles, cuenta e inicio de sesión** y **PB-10 Aprobar o rechazar talleres**. PB-05 deja de ser para el instructor. | TAL-RF-09, CU-02, CU-15 |
| El taller debe tener categoría parametrizada (deporte, canto, baile) y búsqueda por categoría en la pantalla. | Nuevo elemento: **PB-11 Categorías y búsqueda por categoría**. | TAL-RF-12, CU-03, CU-14 |
| Al editar solo se cambian fechas (si no empezó) y cupo; nombre y categoría no. El motivo se elige de una lista con las 4 razones más comunes. | PB-04 se precisó con motivos parametrizados e historial. | TAL-RF-10, CU-06, CU-14 |
| Las pruebas deben repartirse en 80 % unitarias, 15 % de integración y 5 % de punta a punta. | Se agregaron pruebas de pantallas y de punta a punta con navegador. | TAL-RC-03 |
| Un bot de avisos sería ideal, pero no alcanza el tiempo; es mejor cumplir lo pedido. | No se agregó al backlog. | Fuera de alcance |

### Backlog final
| Orden | ID | Capacidad | Estado |
|---|---|---|---|
| 1 | PB-01 | Crear taller e inscribir participante (cupo, espera del 20 %, duplicados, choque de horario, taller no empezado, reinscripción) | Terminado |
| 2 | PB-09 | Roles, cuenta con código universitario e inicio de sesión | Terminado |
| 3 | PB-10 | Aprobar o rechazar talleres y ediciones del coordinador | Terminado |
| 4 | PB-03 | Cancelar inscripción con promoción automática y plazo de 3 horas | Terminado |
| 5 | PB-06 | Bloqueo por cancelaciones y levantar el bloqueo | Terminado |
| 6 | PB-04 | Editar fechas y cupo con motivo parametrizado e historial | Terminado |
| 7 | PB-02 | Consultar talleres, disponibilidad y ocupación | Terminado |
| 8 | PB-05 | Listas de confirmados, espera y cancelaciones (búsqueda del operador) | Terminado |
| 9 | PB-07 | Avisos en pantalla | Terminado |
| 10 | PB-08 | Cancelar un taller completo | Terminado |
| 11 | PB-11 | Categorías y búsqueda por categoría | Terminado |

## Retrospectiva
1. **Mantener:** escribir la prueba de cada regla junto con la función. Evidencia: los casos normal, límite y rechazo de la tabla de ejemplos quedaron cubiertos por las 7 pruebas y la suite pasó en `main`.
2. **Experimentar:** abrir un pull request por cada tarea y que otro integrante lo revise antes de integrarlo; cada integrante actualiza el documento de la sesión en el mismo PR de su tarea. Se comprueba si al cierre de la siguiente sesión el documento queda terminado y todas las tareas tienen un PR revisado. **Resultado:** se adoptó; desde entonces cada cambio entra a `main` por pull request revisado por otro integrante.

## Planificación y adaptación
* **¿Qué decisión necesitaba planificación antes de programar?** Qué identifica a un participante (se eligió el CI) y qué devuelve la inscripción (estado CONFIRMADO, EN_ESPERA o error). Sin acordar esa interfaz, las pruebas y la implementación no coincidían.
* **¿Qué decisión pudimos mejorar gracias a una prueba o a la revisión del cliente?** El identificador del taller: el UUID funcionaba en las pruebas, pero el cliente pidió después un código relacionado con el taller. También la promoción desde la espera, que quedó automática, y la identificación del participante, que pasó del CI al código universitario del padrón.
* **¿En qué contexto conviene fijar más detalles por anticipado?** En las reglas que cambian datos de muchas personas a la vez, como la lista de espera, las cancelaciones y el bloqueo, porque un error deja cupos incorrectos. El costo de fijarlas antes, si el cliente todavía las está definiendo, es rehacer pruebas y código, como pasó con la regla del bloqueo, que primero fue provisional. Por eso las fijamos con ejemplos pequeños y las ajustamos en cada revisión.