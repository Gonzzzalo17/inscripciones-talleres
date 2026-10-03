# Sesión 6 — Hallazgos y requisitos del proyecto

- Proyecto: P03 — Inscripciones a talleres y listas de espera
- Integrantes: Gonzalo Cárdenas, Santiago Arauz, Andrea Trujillo
- Fecha: Final de módulo
- Cliente o fuente consultada: docente (cliente), reunión 01
- Flujo seleccionado: inscripción / cancelación. Incluye la solicitud de plaza, la lista de espera, la cancelación y la asignación de plazas liberadas.

## 1. Hallazgos de la entrevista

| ID | Pregunta | Respuesta o hallazgo | Fuente | Estado |
|---|---|---|---|---|
| ENT-01 | ¿Qué pasa si el taller ya no tiene cupos o se cancela? | La idea es que se notifique a la persona, si se puede por WhatsApp. | Docente (cliente) | pendiente (falta definir el canal y qué pasa con las inscripciones si se cancela el taller) |
| ENT-02 | A la persona que está en la lista de espera, ¿se le notifica o se le agrega directamente? ¿Debe confirmar? | Se agrega automáticamente a la primera persona de la lista de espera, sin que tenga que confirmar. Se le manda una notificación, por ejemplo: «Felicidades, ya estás inscrito». | Docente (cliente) | confirmado |
| ENT-03 | Si una persona estaba inscrita en un taller y se sale, ¿recupera su lugar si vuelve? | No. Vuelve como si fuera una persona nueva: si hay cupo, toma el último lugar del taller; si el taller está lleno, va al último lugar de la lista de espera. | Docente (cliente) | confirmado |
| ENT-04 | ¿Se puede aumentar o disminuir el tamaño de un taller (por ejemplo, si se consigue un aula más grande)? | Sí. Si el taller pasa de 10 a 20 plazas, se acepta a los participantes que estaban en la lista de espera. Si el taller se hace más pequeño, los participantes que sobran pasan a la lista de espera. | Docente (cliente) | confirmado (falta definir quiénes pasan a la espera cuando se reduce) |
| ENT-05 | ¿Cómo se identifica a los trolls (por ejemplo, con CI o un código)? | Sin respuesta definida. | Docente (cliente) | pendiente |
| ENT-06 | Si hay 2 talleres distintos a la misma hora en aulas distintas, ¿me puedo inscribir a los 2? | No. Solo se puede estar inscrito en uno. | Docente (cliente) | confirmado |
| ENT-07 | ¿La lista de espera tiene un límite? ¿Es igual, menor o mayor que el tamaño del taller? | Es el 20 % del cupo máximo del taller. Ejemplo: taller de 20 → lista de espera de 4. Si la lista de espera está llena, se rechaza a la persona. | Docente (cliente) | confirmado (falta definir cómo se redondea, por ejemplo con cupo 12) |
| ENT-08 | ¿Hasta qué hora se puede inscribir alguien a un taller? | Hasta el último minuto antes de que empiece. Una vez iniciado el taller, se rechaza la inscripción. Esto es por ahora; a futuro se verá si se permite según la duración del taller. | Docente (cliente) | confirmado por ahora (la regla futura queda pendiente) |
| ENT-09 | ¿Hasta qué hora se puede cancelar una inscripción? | Hasta 3 horas antes del inicio. Ejemplo: si el taller empieza a las 12:00, se puede cancelar hasta las 9:00. | Docente (cliente) | confirmado |
| ENT-10 | Requisito del cliente (no fue pregunta): formato del identificador del taller | El ID debe estar relacionado con el nombre del taller. Ejemplos: Taller de danza `DAN-PAR-01`, Taller de fútbol `FUT-PAR-01`, Taller de violín `VIO-PAR-01`. | Docente (cliente) | confirmado (falta aclarar qué significa `PAR`) |
| ENT-11 | Requisito del cliente (no fue pregunta): historial de cancelaciones | Quiere mantener un historial de las cancelaciones de cada participante, para poder banear. | Docente (cliente) | pendiente (falta definir la regla de baneo) |

## 2. Alcance del flujo

- Incluye:
  - Solicitar plaza en un taller: queda confirmada si hay cupo; si no, queda en lista de espera; si la espera también está llena, se rechaza.
  - Rechazar la solicitud si el taller ya empezó o si choca de horario con otro taller en el que la persona ya está inscrita.
  - Cancelar una inscripción hasta 3 horas antes del inicio.
  - Pasar automáticamente a la primera persona de la espera cuando se libera una plaza, y generar el mensaje «Felicidades, ya estás inscrito».
  - Ajustar inscritos y lista de espera cuando cambia el cupo del taller.
  - Identificar a los talleres con el formato acordado (`DAN-PAR-01`).
  - Registrar las cancelaciones de cada participante.
- No incluye (por ahora):
  - Envío real de notificaciones por WhatsApp (pendiente: ENT-01).
  - Detección de trolls y baneos (pendiente: ENT-05 y ENT-11).
  - Inscripción después del inicio del taller (regla futura, ENT-08).
  - Crear o eliminar talleres, pagos y reportes.
  - Registro e inicio de sesión (se asume que el participante ya está identificado).

## 3. Requisitos

### TAL-RF-01 — Solicitud con plaza disponible

- Tipo: funcional
- Origen: ENT-08 y encargo inicial
- Prioridad y razón: alta. Es el caso principal del flujo.
- Estado: aprobado por el cliente
- Requisito: si un taller todavía no empezó y tiene plazas libres, y la persona no tiene una inscripción activa en ese taller, el sistema debe registrar la inscripción como **confirmada** y aumentar en 1 las plazas ocupadas. Si el taller ya empezó, debe rechazar la solicitud.
- Criterio de aceptación:
  - Situación inicial: taller `DAN-PAR-01` de 10:00 a 12:00, cupo 10, 5 plazas ocupadas. P-01 no está inscrito.
  - Acción: P-01 solicita plaza a las 9:59.
  - Resultado esperado: P-01 queda confirmado y el taller tiene 6 plazas ocupadas. Si P-02 solicita a las 10:01, se rechaza con el mensaje «El taller ya empezó» y las plazas ocupadas no cambian.

### TAL-RF-02 — Lista de espera con límite del 20 %

- Tipo: funcional
- Origen: ENT-07. Pregunta propia del equipo.
- Prioridad y razón: alta. Es la regla principal de la lista de espera.
- Estado: aprobado por el cliente (falta definir el redondeo)
- Requisito: si el taller está lleno, el sistema debe poner a la persona al final de la lista de espera y mostrarle su posición. La lista de espera puede tener como máximo el 20 % del cupo del taller. Si la lista de espera también está llena, el sistema debe rechazar la solicitud.
- Criterio de aceptación:
  - Situación inicial: taller `FUT-PAR-01` con cupo 20 y 20 plazas ocupadas; lista de espera con 3 personas (máximo 4).
  - Acción: P-10 solicita plaza; después P-11 solicita plaza.
  - Resultado esperado: P-10 queda en espera en la posición 4. P-11 es rechazado con el mensaje «El taller y la lista de espera están llenos». La espera queda con 4 personas y las plazas ocupadas siguen en 20.

### TAL-RF-03 — Asignación automática de una plaza liberada

- Tipo: funcional
- Origen: ENT-02. Pregunta propia del equipo.
- Prioridad y razón: alta. Sin esta regla la lista de espera no sirve.
- Estado: aprobado por el cliente
- Requisito: cuando se libera una plaza en un taller con personas en espera, el sistema debe confirmar automáticamente a la primera persona de la lista, sin que tenga que aceptar, y generar el mensaje «Felicidades, ya estás inscrito». Las demás personas avanzan una posición.
- Criterio de aceptación:
  - Situación inicial: taller `VIO-PAR-01` con cupo 2; A y B confirmados; C y D en espera, en ese orden.
  - Acción: A cancela su inscripción dentro del plazo permitido.
  - Resultado esperado: C queda confirmado y recibe el mensaje «Felicidades, ya estás inscrito»; D pasa a la posición 1; el taller sigue con 2 plazas ocupadas; la cancelación de A queda registrada.

### TAL-RF-04 — Volver a inscribirse después de cancelar

- Tipo: funcional
- Origen: ENT-03. Pregunta propia del equipo.
- Prioridad y razón: media. Evita que alguien cancele y "guarde" su lugar.
- Estado: aprobado por el cliente
- Requisito: si una persona canceló su inscripción y vuelve a solicitar plaza en el mismo taller, el sistema debe tratarla como una solicitud nueva: no recupera su lugar anterior. Si hay cupo, queda confirmada; si no, va al final de la lista de espera.
- Criterio de aceptación:
  - Situación inicial: taller `DAN-PAR-01` con cupo 2. A canceló; C fue promovido de la espera; ahora B y C están confirmados y D está en espera, en la posición 1.
  - Acción: A vuelve a solicitar plaza.
  - Resultado esperado: A queda en espera en la posición 2, detrás de D. B y C siguen confirmados.

### TAL-RF-05 — Choque de horario entre talleres

- Tipo: funcional
- Origen: ENT-06. Pregunta propia del equipo.
- Prioridad y razón: media. Una persona no puede estar en dos aulas al mismo tiempo.
- Estado: aprobado por el cliente
- Requisito: si una persona ya está inscrita en un taller y solicita plaza en otro taller a la misma hora, el sistema debe rechazar la solicitud y conservar la inscripción que ya tenía.
- Criterio de aceptación:
  - Situación inicial: P-01 confirmado en `DAN-PAR-01` (10:00–12:00). El taller `FUT-PAR-01` (10:00–12:00) tiene plazas libres.
  - Acción: P-01 solicita plaza en `FUT-PAR-01`.
  - Resultado esperado: el sistema rechaza con el mensaje «Ya estás inscrito en otro taller a esa hora». P-01 sigue inscrito solo en `DAN-PAR-01` y las plazas de `FUT-PAR-01` no cambian.

### TAL-RF-06 — Plazo para cancelar

- Tipo: funcional
- Origen: ENT-09. Pregunta propia del equipo.
- Prioridad y razón: media. Da tiempo a que la persona en espera pueda organizarse para asistir.
- Estado: aprobado por el cliente
- Requisito: el sistema debe permitir cancelar una inscripción solo hasta 3 horas antes del inicio del taller. Después de ese momento debe rechazar la cancelación y conservar la inscripción.
- Criterio de aceptación:
  - Situación inicial: P-01 confirmado en `VIO-PAR-01`, que empieza a las 12:00.
  - Acción: P-01 intenta cancelar a las 8:30; en otro caso, intenta cancelar a las 9:30.
  - Resultado esperado: a las 8:30 la cancelación se acepta y se aplica TAL-RF-03. A las 9:30 se rechaza con el mensaje «Ya no se puede cancelar: el plazo vence 3 horas antes del inicio» y P-01 sigue confirmado.

### TAL-RF-07 — Cambio de cupo del taller

- Tipo: funcional
- Origen: ENT-04. Pregunta propia del equipo.
- Prioridad y razón: baja. No es parte del flujo diario del participante, pero el cliente lo pidió.
- Estado: aprobado por el cliente para el aumento; pendiente de aclaración para la reducción
- Requisito: si el cupo de un taller aumenta, el sistema debe confirmar a las personas de la lista de espera en orden hasta llenar las nuevas plazas. Si el cupo disminuye, los participantes que sobran deben pasar a la lista de espera (falta definir cuáles).
- Criterio de aceptación:
  - Situación inicial: taller `FUT-PAR-01` con cupo 10, 10 confirmados y 2 en espera.
  - Acción: el cupo cambia a 20.
  - Resultado esperado: las 2 personas en espera quedan confirmadas, en orden; el taller tiene 12 plazas ocupadas y la lista de espera queda vacía.

### TAL-RC-01 — Solicitudes simultáneas por la última plaza

- Tipo: calidad (fiabilidad / consistencia de datos)
- Origen: propuesta del equipo, relacionada con TAL-RF-01 y TAL-RF-02
- Prioridad y razón: alta. Si dos personas piden la última plaza al mismo tiempo, el taller podría quedar con sobrecupo.
- Estado: propuesto
- Requisito: si dos o más solicitudes llegan al mismo tiempo cuando queda una sola plaza, el sistema debe confirmar solo una y aplicar TAL-RF-02 a las demás. Las plazas ocupadas nunca deben superar el cupo.
- Criterio de aceptación:
  - Situación inicial: taller `DAN-PAR-01` con cupo 10 y 9 plazas ocupadas.
  - Acción: P-10 y P-11 solicitan plaza al mismo tiempo (se simula en una prueba).
  - Resultado esperado: uno queda confirmado y el otro en espera, en la posición 1. El taller tiene 10 plazas ocupadas, no 11.

### TAL-RT-01 — Lenguaje del proyecto

- Tipo: restricción
- Origen: encargo del curso
- Prioridad y razón: alta. Es obligatorio según el encargo.
- Estado: aprobado (encargo del curso)
- Requisito: la lógica principal del flujo de inscripción debe estar desarrollada en Python.
- Criterio de comprobación posterior: al revisar y ejecutar el incremento, las reglas de TAL-RF-01 a TAL-RF-07 están implementadas en Python. Todavía no se comprobó.

### TAL-RT-02 — Formato del identificador del taller

- Tipo: restricción
- Origen: ENT-10 (pedido directo del cliente)
- Prioridad y razón: media. El cliente lo pidió explícitamente y afecta cómo se guardan los talleres.
- Estado: aprobado por el cliente (falta aclarar el significado de `PAR`)
- Requisito: cada taller debe tener un identificador formado por tres letras del nombre del taller, el código `PAR` y un número de dos dígitos, separados por guiones (`DAN-PAR-01`). No puede haber dos talleres con el mismo identificador.
- Criterio de comprobación posterior: al registrar el Taller de danza, su ID es `DAN-PAR-01`; si se intenta registrar otro taller con `DAN-PAR-01`, se rechaza.

## 4. Escenarios del flujo

| Caso | Requisito relacionado | Datos y acción | Resultado esperado |
|---|---|---|---|
| Normal | TAL-RF-01 | `DAN-PAR-01` cupo 10, 5 ocupadas; P-01 solicita antes del inicio | P-01 confirmado; 6 plazas ocupadas |
| Límite | TAL-RF-02 | `FUT-PAR-01` lleno (20/20) y espera con 4 de 4; P-11 solicita | Rechazo: «El taller y la lista de espera están llenos»; nada cambia |
| Rechazo | TAL-RF-05 | P-01 inscrito en `DAN-PAR-01` (10:00–12:00) solicita `FUT-PAR-01` a la misma hora | Rechazo: «Ya estás inscrito en otro taller a esa hora»; P-01 conserva su inscripción |

Estos escenarios están especificados; ninguno fue ejecutado todavía.

## 5. Preguntas y decisiones pendientes

| Pregunta | A quién consultar | Impacto mientras no se resuelva |
|---|---|---|
| ¿Las notificaciones se envían de verdad por WhatsApp o basta con mostrar el mensaje en el sistema? | Docente (cliente) | TAL-RF-03 solo genera el mensaje; el envío queda fuera del alcance |
| Si se cancela un taller completo, ¿qué pasa con los inscritos y los que están en espera? | Docente (cliente) | No hay requisito para ese caso |
| Cuando el cupo se reduce, ¿qué participantes pasan a la espera (los últimos inscritos)? ¿Y si la espera supera el 20 %? | Docente (cliente) | TAL-RF-07 solo cubre el aumento |
| ¿Cómo se redondea el 20 % (por ejemplo, cupo 12 → 2,4)? | Docente (cliente) | Afecta el límite de TAL-RF-02 |
| ¿Cómo se identifica a un troll (CI, código)? ¿Cuántas cancelaciones llevan a un baneo? | Docente (cliente) | El historial de cancelaciones se guarda, pero no se aplica ningún baneo |
| ¿Qué significa `PAR` en el identificador? ¿Siempre es igual? | Docente (cliente) | TAL-RT-02 puede cambiar |
| ¿Se permitirá inscribirse después del inicio según la duración del taller? | Docente (cliente) | Por ahora TAL-RF-01 rechaza toda solicitud después del inicio |

## 6. Siguiente paso

- Tarea: implementar en `proyecto/reglas.py` la función de solicitar plaza (confirmar, poner en espera con límite del 20 % o rechazar) y sus pruebas en `tests/`.
- Requisito relacionado: TAL-RF-01 y TAL-RF-02
- Responsable inicial: Santiago