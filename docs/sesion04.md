# Iteración de la Sesión 04

## Equipo y proyecto
* **Proyecto:** P03 — Inscripciones a talleres y listas de espera
* **Integrantes:** Andrea Trujillo Antezana, Gonzalo Andres Cárdenas Vargas, Santiago Arauz Peña

## Backlog ordenado
| Orden | ID | Capacidad | ¿A quién ayuda y para qué? | Duda pendiente |
|---|---|---|---|---|
| 1 | PB-01 | Crear taller con cupo máximo e inscribir participante por CI (con control de cupos, lista de espera y rechazo por duplicado) | Ayuda al Coordinador a ofertar talleres y al Participante a registrarse, garantizando el control y evitando registros repetidos. | ¿Se deben validar formatos de CI extranjeros o con letras? |
| 2 | PB-02 | Consultar disponibilidad de talleres y estado de ocupación  | Ayuda al Operador y Participante a visualizar los cupos disponibles antes de solicitar una inscripción. | Ninguna |
| 3 | PB-03 | Cancelar inscripción y reasignar plaza a la lista de espera  | Ayuda al Participante a liberar su cupo y al sistema a promover de forma transparente al siguiente en espera. | ¿La promoción desde lista de espera debe ser automática o requerir confirmación? |
| 4 | PB-04 | Modificar o corregir cupos de un taller conservando historial  | Ayuda al Coordinador a ajustar la capacidad del aula ante imprevistos sin perder el registro de cambios. | Ninguna |
| 5 | PB-05 | Generar reportes de confirmados, lista de espera y cancelaciones  | Ayuda al Instructor y al Coordinador a obtener el listado oficial de asistencia. | Ninguna |

* **Razón de la primera prioridad:** Se definió PB-01 como prioridad absoluta porque la creación del taller y la gestión inicial de inscripciones (controlando si hay vacantes, si pasa a lista de espera o si es un duplicado) constituyen la regla de negocio central del sistema. Sin esta capacidad mínima funcionando en código, no existen datos reales sobre los cuales consultar disponibilidad, procesar cancelaciones o generar reportes.

## Objetivo y alcance
Al finalizar, el Coordinador podrá crear un taller indicando su nombreTaller , categoriaTaller y cupo_maximo mediante la función crear_taller (generando su identificador único id_taller con formato UUID). Asimismo, se podrá registrar a un participante utilizando su ci_participante a través de la función registrar_inscripcion, otorgándole el estado "CONFIRMADO" si existe vacante disponible, el estado "EN_ESPERA" si el taller alcanza su cupo máximo, o lanzando una excepción ValueError si el cupo es menor o igual a cero o si el participante ya se encuentra registrado en el taller.

## Aclaraciones del cliente
| Pregunta | Respuesta del cliente | Efecto sobre el comportamiento esperado |
|---|---|---|
| ¿Creamos un nuevo repositorio o se usa el de la Sesión 03? | Debe ser un repositorio nuevo, el cual utilizarán de aquí en adelante hasta el final de la materia. | Se creó el repositorio oficial del proyecto semestral respetando la estructura base (`proyecto/`, `tests/`, `docs/`). |
| ¿Todos los usuarios pueden crear talleres o solo los coordinadores? | Queda a criterio del equipo para este primer paso, sirviendo como guía de diseño para la propuesta del software. | Se asumió el rol de Coordinador mediante la función `crear_taller` para definir ofertas con cupos limitados. |
| ¿Bajo qué criterio controlamos las identificaciones únicas (Carnet/Email) para evitar duplicados? | A criterio del equipo; están presentando la propuesta de software al cliente para ver si la aprueba. | Se decidió utilizar el Carnet de Identidad (`ci_participante`) como identificador único para validar que no existan inscripciones duplicadas. |
## Ejemplos de aceptación
| Caso | Estado inicial y entrada | Resultado esperado | Regla que lo justifica |
|---|---|---|---|
| **Uso normal** | Taller Robótica Avanzada creado con cupo máximo igual a 2 y lista de inscritos vacía. Se ejecuta la inscripción del participante con CI 1234567. | Se registra al participante con CI 1234567, asignándole el estado CONFIRMADO y el mensaje de confirmación exitosa. | Si existen vacantes disponibles y la cédula no está registrada, la plaza se otorga con estado confirmado. |
| **Rechazo o situación excepcional prevista** | Taller con cupo máximo igual a 2 y la CI 1234567 previamente registrada en la lista de inscritos. Se intenta inscribir nuevamente al participante con CI 1234567. | El sistema interrumpe la operación y lanza un error de tipo ValueError indicando que el participante con CI 1234567 ya está inscrito en este taller. | Se rechaza explícitamente la inscripción duplicada del mismo participante en el mismo taller lanzando una excepción. |
| **Límite** | Taller con cupo máximo igual a 2 y dos participantes confirmados con CI 1234567 y CI 8901234. Se ejecuta la inscripción del participante con CI 5554433. | Se registra al participante con CI 5554433, asignándole el estado EN ESPERA y el mensaje indicando que el cupo está lleno y fue enviado a lista de espera. | Cuando se alcanza la capacidad máxima del taller, la solicitud pasa automáticamente al estado de lista de espera. |
## Plan y seguimiento
| Tarea | Personas que colaboran | Estado | Evidencia o ubicación |
|---|---|---|---|
| Crear la clase Taller con sus atributos y la función crear_taller con control de cupos máximos | Andrea | Terminado | Archivo proyecto/reglas.py |
| Implementar la función registrar_inscripcion con validación de duplicados por Cédula de Identidad, estados CONFIRMADO y EN_ESPERA | Gonzalo | Terminado | Archivo proyecto/reglas.py |
| Escribir la suite de pruebas unitarias en pytest para verificar casos normales, límites y errores por duplicado | Santiago | Terminado | Archivo tests/test_reglas.py |
| Elaborar la documentación general y estructura inicial del archivo README.md | Todos los integrantes | Terminado | Archivo README.md |
| Consolidar y redactar el registro completo de la iteración, acuerdos, ejemplos de aceptación y retrospectiva en docs/sesion04.md | Todos los integrantes | En proceso | Archivo docs/sesion04.md|
| Consultar disponibilidad de talleres y estado de ocupación | Todo el equipo | Por hacer | Backlog (Próxima iteración) |
| Cancelar inscripción y reasignar plaza a la lista de espera | Todo el equipo | Por hacer | Backlog (Próxima iteración) |
| Modificar o corregir cupos de un taller conservando historial | Todo el equipo | Por hacer | Backlog (Próxima iteración) |
| Generar reportes de confirmados, lista de espera y cancelaciones | Todo el equipo | Por hacer | Backlog (Próxima iteración) |


