# Sesión 6 — Hallazgos y requisitos del proyecto

- **Proyecto:** P03 — Inscripciones a talleres y listas de espera
- **Integrantes:** Gonzalo Cárdenas, Santiago Arauz, Andrea Trujillo
- **Cliente:** docente de la materia
- **Flujo seleccionado:** inscripción y cancelación (solicitud de plaza, lista de espera, cancelación y asignación de plazas liberadas)
- **Contenido:** hallazgos de la entrevista de la sesión 6 (requisitos iniciales), respuestas posteriores del cliente (requisitos agregados) y cumplimiento del encargo.

**Cómo leer este documento.** Cada hallazgo y cada requisito indica si es **inicial** (entrevista de la sesión 6) o **agregado después** (pedido del cliente en una consulta posterior). Cuando una respuesta posterior cambió un requisito inicial, se conserva el requisito con su ID y se indica qué cambió y cuándo.

## 1. Hallazgos de la entrevista

### 1.1 Entrevista inicial (reunión 01, sesión 6)

| ID | Pregunta | Respuesta en la entrevista inicial | Respuesta posterior o estado final |
|---|---|---|---|
| ENT-01 | ¿Qué pasa si el taller ya no tiene cupos o se cancela? | Se avisa a la persona; si se puede, por WhatsApp. | **Cambió el 22/10:** basta con mostrar el aviso en pantalla, también si se cancela un taller (ENT-13 y ENT-14). Confirmado. |
| ENT-02 | A la persona en lista de espera, ¿se le notifica o se la agrega directamente? ¿Debe confirmar? | Se agrega automáticamente a la primera de la lista, sin confirmar, y se le avisa «Felicidades, ya estás inscrito». | Confirmado. |
| ENT-03 | Si alguien cancela y vuelve, ¿recupera su lugar? | No. Vuelve como persona nueva: si hay cupo queda confirmada; si no, va al final de la espera. | Confirmado. |
| ENT-04 | ¿Se puede aumentar o disminuir el tamaño de un taller? | Sí. Si sube de 10 a 20 plazas, entran los de la espera. Si baja, los que sobran pasan a la espera. | Confirmado. El aumento confirma a la espera en orden; la reducción no puede dejar el cupo por debajo de los confirmados (ENT-17). |
| ENT-05 | ¿Cómo se identifica a los trolls? | Sin respuesta en la entrevista. | **Resuelto después:** cada persona se identifica por su código universitario del padrón y se aplica el bloqueo por cancelaciones (ENT-11, ENT-15, ENT-16). |
| ENT-06 | Si hay 2 talleres a la misma hora en aulas distintas, ¿me puedo inscribir a los 2? | No, solo a uno. | Confirmado. |
| ENT-07 | ¿La lista de espera tiene un límite? | El 20 % del cupo (taller de 20 → espera de 4). Si está llena, se rechaza. | Confirmado, con redondeo hacia arriba: cupo 12 → espera de 3; cupo 4 → espera de 1. |
| ENT-08 | ¿Hasta qué hora se puede inscribir alguien? | Hasta el último minuto antes del inicio; después se rechaza. | Confirmado: desde la hora de inicio no se acepta ninguna solicitud. |
| ENT-09 | ¿Hasta qué hora se puede cancelar? | Hasta 3 horas antes del inicio (taller a las 12:00 → hasta las 9:00). | Confirmado. |
| ENT-10 | Pedido del cliente: formato del identificador del taller | Relacionado con el nombre: `DAN-PAR-01`, `FUT-PAR-01`, `VIO-PAR-01`. | **Cambió en la reunión 02:** el código lleva el prefijo `TAL`, tres letras de la actividad y un número de dos dígitos (`TAL-DAN-01`). Confirmado. |
| ENT-11 | Pedido del cliente: historial de cancelaciones | Guardar las cancelaciones de cada participante para poder banear; la regla se definiría después. | **Definido el 22/10:** más de 3 cancelaciones en 72 horas bloquean 24 horas (ENT-15 y ENT-16). Confirmado. |

### 1.2 Consultas posteriores

| ID | Fecha | Pregunta | Respuesta del cliente | Estado |
|---|---|---|---|---|
| ENT-12 | 8/10 | El encargo dice que el operador «hace consultas»: ¿es atender dudas o algo más? | Consultas = búsquedas (query): qué talleres hay disponibles, si hay espacios, quiénes están inscritos y de qué es el taller. | Confirmado |
| ENT-13 | 22/10 | Cuando alguien pasa de la espera a confirmado, ¿basta con mostrar el aviso en pantalla o se envía de verdad? | Basta con mostrarlo en pantalla. | Confirmado |
| ENT-14 | 22/10 | ¿Y si se cancela un taller? | El aviso también va en pantalla. | Confirmado |
| ENT-15 | 22/10 | Mientras está bloqueado, ¿qué no puede hacer? ¿Conserva sus inscripciones? ¿Y si estaba en espera? | Bloqueado «es como si no existiera»: no puede inscribirse a talleres nuevos, pierde todo lo anterior y, si estaba en espera, se lo saca de todas las listas. | Confirmado |
| ENT-16 | 22/10 | ¿Alguien puede quitar el bloqueo antes de las 24 horas? Si vuelve a pasar, ¿el castigo aumenta? | El administrador (operador) puede quitarlo cuando quiera. Si vuelve a pasar, el bloqueo sigue siendo de 24 horas. | Confirmado |
| ENT-17 | 22/10 | Si se reduce el cupo y sobran confirmados, ¿quiénes pasan a la espera, en qué posición y qué pasa si la espera supera el 20 %? | El cupo no se puede reducir por debajo de la cantidad de confirmados: nadie pierde su plaza. | Confirmado |

### 1.3 Reunión 02 con el cliente (roles y categorías)

| ID | Tema | Respuesta del cliente | Estado |
|---|---|---|---|
| ENT-18 | Cupo del taller | Mínimo 4 y máximo 40 personas. | Confirmado |
| ENT-19 | Roles | **Coordinador:** crea, edita y solicita sus talleres, y ve todo lo relacionado con ellos. **Operador:** crea talleres, edita todos, acepta o rechaza los que pide el coordinador, inscribe, ve los bloqueos y los talleres, y mantiene lo que ya hacía. **Participante:** se registra, inicia sesión, se inscribe, ve sus inscripciones y puede ser bloqueado. No se incluye el rol Instructor. | Confirmado |
| ENT-20 | Categoría y búsqueda | Cada taller tiene una categoría parametrizada (por ejemplo deporte, canto, baile) y en la pantalla se puede buscar por categoría. | Confirmado |
| ENT-21 | Edición de un taller | Solo se modifican las fechas (si el taller no empezó) y el cupo; el nombre y la categoría no. El motivo se elige de una lista parametrizada con las 4 razones más comunes. | Confirmado |
| ENT-22 | Pruebas | Reparto por tipo: 80 % unitarias, 15 % de integración y 5 % de punta a punta. | Confirmado |
| ENT-23 | Bot de avisos | Sería ideal, pero no alcanza el tiempo; es mejor cumplir con lo pedido. | Fuera de alcance |

## 2. Alcance del flujo

### 2.1 Alcance inicial (sesión 6)

- Incluía:
  - Solicitar plaza: confirmada si hay cupo, en espera si está lleno, rechazada si la espera también está llena.
  - Rechazar si el taller ya empezó o si choca de horario con otro taller de la persona.
  - Cancelar hasta 3 horas antes del inicio y pasar automáticamente al primero de la espera.
  - Ajustar la espera cuando sube el cupo.
  - Identificar los talleres con el formato acordado y registrar las cancelaciones de cada participante.
- No incluía: envío de notificaciones, baneo, inscripción después del inicio, crear o eliminar talleres, reportes, registro e inicio de sesión.

### 2.2 Alcance ampliado (pedidos posteriores del cliente)

- Se agregó:
  - Bloqueo por cancelaciones y levantar el bloqueo (ENT-11, ENT-15, ENT-16).
  - Avisos en pantalla para cada cambio que afecta a una persona (ENT-13, ENT-14).
  - Roles con cuenta e inicio de sesión, y aprobación de talleres por el operador (ENT-19).
  - Categorías parametrizadas y búsqueda por categoría (ENT-20).
  - Edición de fechas y cupo con motivo parametrizado e historial (ENT-21).
  - Cancelar un taller completo (ENT-14).
  - Búsquedas del operador (ENT-12).
  - Cupo de 4 a 40 (ENT-18) y reparto de pruebas (ENT-22).
- Sigue fuera de alcance:
  - Envío real de mensajes por WhatsApp, correo o bot (ENT-13, ENT-14, ENT-23).
  - Inscripción después de la hora de inicio del taller (ENT-08).

## 3. Requisitos

Cada requisito indica su **origen** (inicial o agregado después), su estado y la prueba automática que lo comprueba. Todas las pruebas pasan en `main` con `python -m pytest -q`.

### 3.0 Resumen

| ID | Requisito | Origen | Fuente | Estado |
|---|---|---|---|---|
| TAL-RF-01 | Solicitud con plaza disponible | Inicial | ENT-08 | Aprobado |
| TAL-RF-02 | Lista de espera con límite del 20 % | Inicial | ENT-07 | Aprobado |
| TAL-RF-03 | Asignación automática de una plaza liberada | Inicial | ENT-02 (ajustado por ENT-13) | Aprobado |
| TAL-RF-04 | Volver a inscribirse después de cancelar | Inicial | ENT-03 | Aprobado |
| TAL-RF-05 | Choque de horario entre talleres | Inicial | ENT-06 | Aprobado |
| TAL-RF-06 | Plazo para cancelar | Inicial | ENT-09 | Aprobado |
| TAL-RF-07 | Cambio de cupo del taller | Inicial | ENT-04 (precisado por ENT-17 y ENT-18) | Aprobado |
| TAL-RC-01 | Solicitudes simultáneas por la última plaza | Inicial | Encargo | Aprobado |
| TAL-RT-01 | Lenguaje del proyecto | Inicial | Encargo | Aprobado |
| TAL-RT-02 | Formato del identificador del taller | Inicial | ENT-10 (cambiado en la reunión 02) | Aprobado |
| TAL-RF-08 | Bloqueo por exceso de cancelaciones | Agregado después | ENT-11, ENT-15, ENT-16 (22/10) | Aprobado |
| TAL-RF-09 | Roles, inicio de sesión y aprobación de talleres | Agregado después | ENT-19 (reunión 02) | Aprobado |
| TAL-RF-10 | Edición del taller con motivo e historial | Agregado después | ENT-21 (reunión 02) | Aprobado |
| TAL-RF-11 | Cancelación de un taller completo | Agregado después | ENT-14 (22/10) | Aprobado |
| TAL-RF-12 | Categorías y búsqueda por categoría | Agregado después | ENT-20 (reunión 02) | Aprobado |
| TAL-RF-13 | Avisos en pantalla | Agregado después | ENT-13, ENT-14 (22/10) | Aprobado |
| TAL-RF-14 | Consultas del operador | Agregado después | ENT-12 (8/10) | Aprobado |
| TAL-RC-02 | Mensaje claro ante un rechazo | Agregado después | Condiciones del curso | Aprobado |
| TAL-RC-03 | Pirámide de pruebas | Agregado después | ENT-22 (reunión 02) | Aprobado |
| TAL-RT-03 | Cupo permitido | Agregado después | ENT-18 (reunión 02) | Aprobado |
| TAL-RT-04 | Base de datos | Agregado después | Encargo (persistencia de datos) | Aprobado |

### 3.1 Requisitos iniciales (sesión 6)

#### TAL-RF-01 — Solicitud con plaza disponible

- **Tipo:** funcional · **Origen:** inicial (TAL-03 del encargo, ENT-08) · **Prioridad:** alta, es el caso principal del flujo · **Estado:** aprobado por el cliente
- **Requisito:** si un taller todavía no empezó y tiene plazas libres, y la persona no tiene una inscripción activa en él, el sistema registra la inscripción como **confirmada** y las plazas ocupadas suben en 1. Si el taller ya empezó, rechaza la solicitud.
- **Cambio posterior:** desde la reunión 02 el taller además debe estar **aprobado** por el operador (TAL-RF-09).
- **Criterio de aceptación:**
  - Situación inicial: taller `TAL-DAN-01` de 10:00 a 12:00, cupo 10, 5 plazas ocupadas. P-01 no está inscrito.
  - Acción: P-01 solicita plaza a las 9:59; P-02 solicita a las 10:01.
  - Resultado esperado: P-01 queda confirmado y hay 6 plazas ocupadas. P-02 es rechazado con «El taller ya empezó.» y las ocupadas no cambian.
- **Comprobado por:** `tests/test_operador.py` (`test_confirmado_con_plaza_libre`, `test_e1_taller_ya_iniciado_no_escribe_nada`).

#### TAL-RF-02 — Lista de espera con límite del 20 %

- **Tipo:** funcional · **Origen:** inicial (TAL-06, ENT-07) · **Prioridad:** alta, es la regla principal de la espera · **Estado:** aprobado por el cliente
- **Requisito:** si el taller está lleno, la persona queda al final de la espera y ve su posición. La espera admite como máximo el 20 % del cupo, redondeado hacia arriba (cupo 12 → 3; cupo 4 → 1). Si también está llena, se rechaza la solicitud.
- **Criterio de aceptación:**
  - Situación inicial: taller `TAL-FUT-01` con cupo 20 y 20 ocupadas; espera con 3 personas (máximo 4).
  - Acción: P-10 solicita plaza; después P-11 solicita plaza.
  - Resultado esperado: P-10 queda en espera en la posición 4. P-11 es rechazado con «El taller y la lista de espera están llenos.». La espera queda con 4 personas y las ocupadas siguen en 20.
- **Comprobado por:** `tests/test_operador.py` (`test_e4_espera_en_ultima_posicion`, `test_e5_taller_y_espera_llenos_rechaza_sin_cambios`, `test_capacidad_lista_espera_redondea_hacia_arriba`).

#### TAL-RF-03 — Asignación automática de una plaza liberada

- **Tipo:** funcional · **Origen:** inicial (TAL-05, TAL-06, ENT-02) · **Prioridad:** alta, sin esta regla la espera no sirve · **Estado:** aprobado por el cliente
- **Requisito:** cuando se libera una plaza y hay personas en espera, el sistema confirma automáticamente a la primera, sin que tenga que aceptar, y le muestra «Felicidades, se liberó una plaza y ya estás inscrito en el taller …». Las demás avanzan una posición, sin huecos.
- **Cambio posterior:** el 22/10 el cliente confirmó que el aviso solo se muestra en pantalla (ENT-13).
- **Criterio de aceptación:**
  - Situación inicial: taller `TAL-VIO-01` con cupo 4; A, B, E y F confirmados; C y D en espera, en ese orden.
  - Acción: A cancela dentro del plazo.
  - Resultado esperado: C queda confirmado y recibe el aviso; D pasa a la posición 1; siguen 4 ocupadas; la cancelación de A queda en el historial.
- **Comprobado por:** `tests/test_operador.py` (`test_cancelar_promueve_al_primero_en_espera`, `test_cancela_alguien_en_espera_y_las_posiciones_se_reordenan`), `tests/test_notificaciones.py`.

#### TAL-RF-04 — Volver a inscribirse después de cancelar

- **Tipo:** funcional · **Origen:** inicial (ENT-03) · **Prioridad:** media, evita que alguien cancele y «guarde» su lugar · **Estado:** aprobado por el cliente
- **Requisito:** si una persona canceló y vuelve a pedir plaza en el mismo taller, se trata como solicitud nueva y no recupera su lugar: confirmada si hay cupo, al final de la espera si no. No se crea un segundo registro para la misma persona y taller.
- **Criterio de aceptación:**
  - Situación inicial: taller de cupo 4 lleno. A canceló, C pasó de la espera a confirmado y D está en espera en la posición 1.
  - Acción: A vuelve a solicitar plaza.
  - Resultado esperado: A queda en espera en la posición 2, detrás de D. Los confirmados no cambian.
- **Comprobado por:** `tests/test_reinscripcion.py`.

#### TAL-RF-05 — Choque de horario entre talleres

- **Tipo:** funcional · **Origen:** inicial (TAL-04, ENT-06) · **Prioridad:** media, una persona no puede estar en dos aulas a la vez · **Estado:** aprobado por el cliente
- **Requisito:** si una persona está confirmada o en espera en un taller y pide plaza en otro que se cruza de horario, el sistema rechaza la solicitud y conserva lo que ya tenía.
- **Criterio de aceptación:**
  - Situación inicial: P-01 confirmado en `TAL-DAN-01` (10:00–12:00); `TAL-FUT-01` (10:00–12:00) tiene plazas libres.
  - Acción: P-01 solicita plaza en `TAL-FUT-01`.
  - Resultado esperado: rechazo con «El participante ya tiene otro taller en este horario.». P-01 sigue solo en `TAL-DAN-01` y las plazas de `TAL-FUT-01` no cambian. Lo mismo ocurre si P-01 estaba en espera en `TAL-DAN-01`.
- **Comprobado por:** `tests/test_operador.py` (`test_e3_choque_de_horario_conserva_la_inscripcion_previa`, `test_no_se_inscribe_a_la_misma_hora_si_ya_esta_en_espera_de_otro_taller`).

#### TAL-RF-06 — Plazo para cancelar

- **Tipo:** funcional · **Origen:** inicial (TAL-05, ENT-09) · **Prioridad:** media, da tiempo a que la persona en espera se organice · **Estado:** aprobado por el cliente
- **Requisito:** solo se puede cancelar hasta 3 horas antes del inicio. Después se rechaza y la inscripción se conserva. Una cancelación repetida no cambia nada.
- **Criterio de aceptación:**
  - Situación inicial: P-01 confirmado en `TAL-VIO-01`, que empieza a las 12:00.
  - Acción: P-01 intenta cancelar a las 8:30; en otro caso, a las 9:30.
  - Resultado esperado: a las 8:30 se acepta y se aplica TAL-RF-03. A las 9:30 se rechaza con «Ya pasó el tiempo límite para cancelar.» y P-01 sigue confirmado. Si cancela dos veces, la segunda responde «No existe inscripción activa para cancelar.».
- **Comprobado por:** `tests/test_operador.py` (`test_cancelar_fuera_de_plazo_conserva_la_inscripcion`), `tests/test_cancelar.py`.

#### TAL-RF-07 — Cambio de cupo del taller

- **Tipo:** funcional · **Origen:** inicial (TAL-07, ENT-04) · **Prioridad:** media, lo pidió el cliente para cuando cambia el aula · **Estado:** aprobado por el cliente
- **Requisito:** si el cupo aumenta, el sistema confirma a la espera en orden hasta llenar las nuevas plazas. Si el cupo disminuye, solo puede bajar hasta la cantidad de confirmados, para que nadie pierda su plaza.
- **Cambios posteriores:** en la sesión 6 se había dicho que, al reducir el cupo, los que sobran pasan a la espera. El 22/10 el cliente lo precisó: el cupo no puede quedar por debajo de los confirmados (ENT-17). En la reunión 02 fijó que el cupo siempre está entre 4 y 40 (ENT-18).
- **Criterio de aceptación:**
  - Situación inicial: taller `TAL-FUT-01` con cupo 10, 10 confirmados y 2 en espera.
  - Acción: el cupo cambia a 20; en otro caso, a 8.
  - Resultado esperado: con 20, las 2 personas en espera quedan confirmadas en orden, hay 12 ocupadas y la espera queda vacía. Con 8 se rechaza con «No se puede bajar el cupo a 8: ya hay 10 participantes confirmados.» y nada cambia.
- **Comprobado por:** `tests/test_coordinador.py` (`test_editar_subiendo_el_cupo_confirma_a_la_espera_en_orden`, `test_subir_el_cupo_nunca_confirma_mas_que_el_nuevo_cupo`, `test_bajar_el_cupo_solo_hasta_los_confirmados_sin_mover_a_nadie`).

#### TAL-RC-01 — Solicitudes simultáneas por la última plaza

- **Tipo:** calidad (consistencia de datos) · **Origen:** inicial (situación del encargo: «dos personas intentan ocupar la última plaza») · **Prioridad:** alta, sin esto el taller podría quedar con sobrecupo · **Estado:** propuesto en la sesión 6; hoy implementado y comprobado
- **Requisito:** si dos o más solicitudes llegan a la vez cuando queda una sola plaza, solo una queda confirmada y las demás siguen TAL-RF-02. Las ocupadas nunca superan el cupo y la espera nunca supera el 20 %.
- **Criterio de aceptación:**
  - Situación inicial: taller con cupo 4 y 3 ocupadas.
  - Acción: P-10 y P-11 solicitan a la vez.
  - Resultado esperado: uno queda confirmado y el otro en espera, en la posición 1. Hay 4 ocupadas, no 5.
- **Comprobado por:** `tests/test_simultaneas.py`.

#### TAL-RT-01 — Lenguaje del proyecto

- **Tipo:** restricción · **Origen:** inicial (encargo del curso) · **Prioridad:** alta, es obligatorio · **Estado:** aprobado
- **Requisito:** la lógica principal está desarrollada en Python, separada de la interfaz y del acceso a datos.
- **Criterio de comprobación:** las reglas de TAL-RF-01 a TAL-RF-14 están en `inscripciones/servicios/` (Python con Django) y las vistas solo llaman a esos servicios. Comprobado.

#### TAL-RT-02 — Formato del identificador del taller

- **Tipo:** restricción · **Origen:** inicial (ENT-10) · **Prioridad:** media, el cliente lo pidió explícitamente · **Estado:** aprobado por el cliente
- **Requisito inicial:** tres letras del nombre, el código `PAR` y un número de dos dígitos (`DAN-PAR-01`), sin repetidos.
- **Cambio posterior:** en la reunión 02 el formato cambió a `TAL-<3 letras de la actividad>-<número de 2 dígitos>`, donde la actividad es la primera palabra del nombre que no sea «taller», «de», «la», etc. La categoría del taller se guarda aparte y se usa para buscar (TAL-RF-12).
- **Criterio de comprobación:** «Taller de Danza» recibe `TAL-DAN-01` y el siguiente de danza `TAL-DAN-02`; nunca se repite un código. Comprobado en `tests/test_coordinador.py`.

### 3.2 Requisitos agregados después de la sesión 6

#### TAL-RF-08 — Bloqueo por exceso de cancelaciones

- **Tipo:** funcional · **Origen:** agregado después. En la sesión 6 el historial de cancelaciones estaba pedido (ENT-11), y la regla del bloqueo se definió el 22/10 (ENT-15, ENT-16) · **Prioridad:** alta · **Estado:** aprobado por el cliente
- **Requisito:** si una persona tiene más de 3 cancelaciones en 72 horas, queda bloqueada 24 horas: no puede inscribirse, pierde sus inscripciones confirmadas y sale de las listas de espera de los talleres que no empezaron, y sus plazas pasan al siguiente en espera. Si vuelve a pasar, el bloqueo es otra vez de 24 horas. El operador puede levantar un bloqueo activo cuando quiera: el historial de cancelaciones se conserva completo, se registra qué operador lo levantó y cuándo, y las cancelaciones anteriores a ese momento ya no cuentan para un nuevo bloqueo. Las inscripciones perdidas no vuelven. Cancelar un taller completo no cuenta como cancelación de la persona.
- **Criterio de aceptación:**
  - Situación inicial: P-01 confirmado en `TAL-DAN-01` y en espera en `TAL-FUT-01`; ya canceló 3 veces en las últimas 72 horas.
  - Acción: P-01 cancela una cuarta inscripción y luego pide plaza en otro taller.
  - Resultado esperado: P-01 recibe el aviso de bloqueo, queda cancelado en `TAL-DAN-01` (su plaza pasa al primero en espera) y sale de la espera de `TAL-FUT-01`. La nueva solicitud se rechaza con «Bloqueado hasta el dd/mm HH:MM…». Con 3 cancelaciones en 72 horas, o con 4 separadas por más de 72 horas, no se bloquea.
- **Comprobado por:** `tests/test_baneo.py`, `tests/test_operador.py` (`test_operador_puede_levantar_bloqueo_y_conservar_historial_antiguo`, `test_al_bloquearlo_no_toca_inscripciones_de_talleres_que_ya_empezaron`).

#### TAL-RF-09 — Roles, inicio de sesión y aprobación de talleres

- **Tipo:** funcional · **Origen:** agregado después (ENT-19, reunión 02; TAL-01 del encargo) · **Prioridad:** alta, el encargo pide diferenciar acciones del operador y consultas de otros usuarios · **Estado:** aprobado por el cliente
- **Requisito:** cada persona entra con su código y contraseña y solo ve y usa lo de su rol. Solo un estudiante del padrón puede crear una cuenta de participante. El taller que pide un coordinador queda pendiente hasta que el operador lo aprueba; el que crea el operador queda aprobado. Un taller pendiente o rechazado no recibe inscripciones. El coordinador solo ve y maneja sus talleres.
- **Criterio de aceptación:**
  - Situación inicial: el coordinador C-01 crea `TAL-DAN-01`.
  - Acción: P-01 intenta inscribirse; el operador aprueba el taller; P-01 vuelve a intentarlo. Además, P-01 escribe a mano la dirección de crear taller.
  - Resultado esperado: el primer intento se rechaza con «El taller todavía no fue aprobado por el operador.». Después de aprobarlo, P-01 queda confirmado y C-01 recibe el aviso. La pantalla de crear taller le responde 403 a P-01.
- **Comprobado por:** `tests/test_operador.py`, `tests/test_decidir_taller.py`, `tests/test_sesion.py`, `tests/test_registro.py`, `tests/test_coordinador_solo_lo_suyo.py`, `tests/e2e/test_recorridos.py`.

#### TAL-RF-10 — Edición del taller con motivo e historial

- **Tipo:** funcional · **Origen:** agregado después (ENT-21, reunión 02; TAL-07 del encargo) · **Prioridad:** alta, el encargo pide conservar motivo e historial · **Estado:** aprobado por el cliente
- **Requisito:** solo se editan las fechas y el cupo de un taller que no empezó ni está cancelado; el nombre y la categoría no cambian. El motivo se elige de la lista parametrizada. Se guardan los datos anteriores con el motivo y la fecha. El coordinador solo edita sus talleres y su edición vuelve a quedar pendiente de aprobación. Si el operador rechaza la edición de un taller que ya tiene inscritos, el taller vuelve a sus datos anteriores y nadie pierde su plaza.
- **Criterio de aceptación:**
  - Situación inicial: `TAL-DAN-01` aprobado para el 10/11 de 10:00 a 12:00, con P-01 confirmado.
  - Acción: su coordinador lo pasa al 12/11 eligiendo el motivo «Cambio de fecha u horario porque el ambiente no está disponible», y el operador rechaza el cambio.
  - Resultado esperado: el historial guarda la fecha anterior y el motivo. Tras el rechazo, el taller vuelve al 10/11, sigue aprobado, P-01 sigue confirmado y tanto él como el coordinador reciben el aviso.
- **Comprobado por:** `tests/test_edicion_taller.py`, `tests/test_coordinador.py`, `tests/test_editar_taller_pantalla.py`, `tests/test_operador.py` (`test_rechazar_la_edicion_de_un_taller_con_inscritos_vuelve_a_sus_datos_y_avisa`).

#### TAL-RF-11 — Cancelación de un taller completo

- **Tipo:** funcional · **Origen:** agregado después. Era una pregunta abierta del encargo y de la sesión 6; el cliente la respondió el 22/10 (ENT-14) · **Prioridad:** media · **Estado:** aprobado por el cliente
- **Requisito:** el operador (cualquier taller) o su coordinador (solo los suyos) pueden cancelar un taller que no empezó. Todos los confirmados y los que esperan quedan cancelados y reciben el aviso en pantalla. El taller se conserva para el historial y ya no recibe inscripciones.
- **Criterio de aceptación:**
  - Situación inicial: `TAL-DAN-01` con 2 confirmados y 1 en espera.
  - Acción: el operador cancela el taller.
  - Resultado esperado: las 3 inscripciones quedan canceladas, cada persona recibe «El taller … fue cancelado. Tu inscripción quedó anulada.» y no se suma ninguna cancelación a su historial.
- **Comprobado por:** `tests/test_operador.py` (`test_cancelar_taller_anula_a_todos_les_avisa_y_no_cuenta_para_el_bloqueo`, `test_el_coordinador_solo_cancela_sus_talleres`).

#### TAL-RF-12 — Categorías y búsqueda por categoría

- **Tipo:** funcional · **Origen:** agregado después (ENT-20 y ENT-21, reunión 02) · **Prioridad:** media · **Estado:** aprobado por el cliente
- **Requisito:** cada taller tiene una categoría de una lista parametrizada (vienen cargadas Deporte, Canto, Danza, Artes Marciales y Literatura), y los motivos de edición también están parametrizados. Solo el operador agrega categorías o motivos, sin vacíos ni repetidos. El participante filtra los talleres disponibles por categoría.
- **Criterio de aceptación:**
  - Situación inicial: `TAL-FUT-01` de Deporte y `TAL-DAN-01` de Danza, ambos aprobados.
  - Acción: el participante elige «Deporte»; luego el operador intenta agregar la categoría «deporte».
  - Resultado esperado: el participante solo ve `TAL-FUT-01`; con «Todas» ve los dos. La categoría «deporte» se rechaza por repetida.
- **Comprobado por:** `tests/test_participante.py`, `tests/test_catalogos_operador.py`.

#### TAL-RF-13 — Avisos en pantalla

- **Tipo:** funcional · **Origen:** agregado después. En la sesión 6 el envío de notificaciones estaba fuera de alcance; el 22/10 el cliente definió que basta con mostrarlas en pantalla (ENT-13, ENT-14) · **Prioridad:** media · **Estado:** aprobado por el cliente
- **Requisito:** el sistema guarda un aviso para la persona afectada cuando se inscribe, entra a la espera, pasa de la espera a confirmado, cancela, queda bloqueada, se cancela su taller o su taller vuelve a su horario original; y para el coordinador, cuando su taller o su edición es aprobada o rechazada. Se ven en la pantalla «Notificaciones», el más nuevo primero, y quedan leídos al abrirla.
- **Criterio de aceptación:**
  - Situación inicial: P-01 en espera en la posición 1; P-02 confirmado.
  - Acción: P-02 cancela.
  - Resultado esperado: P-02 ve «Cancelaste tu inscripción…» y P-01 ve «Felicidades, se liberó una plaza…» marcado como «Nuevo:». Al volver a abrir la pantalla ya no aparece como nuevo.
- **Comprobado por:** `tests/test_notificaciones.py`.

#### TAL-RF-14 — Consultas del operador

- **Tipo:** funcional · **Origen:** agregado después (ENT-12, 8/10; TAL-02 y TAL-08 del encargo) · **Prioridad:** media, es la forma de explicar por qué alguien sigue esperando · **Estado:** aprobado por el cliente
- **Requisito:** el operador busca inscripciones por código, nombre o apellido del participante, o por código o nombre del taller, y ve estado y posición. El operador y el coordinador (de sus talleres) consultan la ocupación: ocupadas, libres y espera sobre el máximo. Las consultas no modifican datos.
- **Criterio de aceptación:**
  - Situación inicial: `TAL-DAN-01` con cupo 10, 2 confirmados, 1 en espera y 1 cancelado.
  - Acción: el operador busca «TAL-DAN-01» y abre su ocupación.
  - Resultado esperado: ve las 4 inscripciones con su estado; la ocupación muestra 2 ocupadas, 8 libres y la espera «1 de 2». Ningún dato cambia.
- **Comprobado por:** `tests/test_operador.py` (pruebas `test_buscar_*` y `test_calcular_ocupacion_con_2_confirmados_1_en_espera_y_1_cancelado`), `tests/test_buscar.py`.

#### TAL-RC-02 — Mensaje claro ante un rechazo

- **Tipo:** calidad (usabilidad) · **Origen:** agregado después (condiciones comunes del curso: «un error debe producir un mensaje comprensible y no dejar una operación incompleta») · **Prioridad:** alta, el operador debe poder explicar el rechazo · **Estado:** aprobado
- **Requisito:** cada rechazo muestra su causa concreta (taller ya empezado, choque de horario, ya inscrito, espera llena, bloqueado, fuera de plazo…) y no deja datos a medias.
- **Criterio de aceptación:** al ejecutar cada rechazo de TAL-RF-01 a TAL-RF-08 se muestra el mensaje de esa causa, y las plazas, la espera y las inscripciones previas quedan iguales.
- **Comprobado por:** las pruebas de rechazo de `tests/test_operador.py`, que verifican que nada cambia.

#### TAL-RC-03 — Pirámide de pruebas

- **Tipo:** calidad (verificación) · **Origen:** agregado después (ENT-22, reunión 02) · **Prioridad:** media · **Estado:** aprobado por el cliente
- **Requisito:** las pruebas automáticas se reparten aproximadamente en 80 % unitarias (servicios), 15 % de integración (pantallas con el cliente de pruebas de Django) y 5 % de punta a punta (navegador con Playwright).
- **Criterio de comprobación:** hoy hay 77 unitarias, 21 de integración y 5 de punta a punta (75 % / 20 % / 5 %). No se cuentan `tests/sesion12` ni `tests/version_inicial`, que se conservan como registro de esas sesiones.

#### TAL-RT-03 — Cupo permitido

- **Tipo:** restricción · **Origen:** agregado después (ENT-18, reunión 02) · **Prioridad:** alta · **Estado:** aprobado por el cliente
- **Requisito:** el cupo máximo de un taller está entre 4 y 40, al crearlo y al editarlo.
- **Criterio de comprobación:** un cupo fuera de 4–40 se rechaza con «El cupo máximo del taller debe estar entre 4 y 40 participantes.», tanto en el servicio como en el formulario. Comprobado en `tests/test_coordinador.py` (`test_rechaza_cupo_cero`).

#### TAL-RT-04 — Base de datos

- **Tipo:** restricción · **Origen:** agregado después (encargo del curso: persistencia de los datos) · **Prioridad:** alta · **Estado:** aprobado
- **Requisito:** los datos se guardan en una base de datos SQLite y se conservan después de reiniciar el sistema. El padrón de estudiantes está en una base separada que la aplicación solo consulta y nunca modifica.
- **Criterio de comprobación:** `config/settings.py` define dos bases SQLite: `db.sqlite3` (talleres, usuarios, inscripciones, historiales y avisos) y `estudiantes_estatica.sqlite3` (padrón). Al detener y volver a iniciar el servidor, los talleres e inscripciones siguen ahí. Las pruebas usan bases propias y no tocan estas.

## 4. Escenarios del flujo

| Caso | Requisito | Origen | Datos y acción | Resultado esperado |
|---|---|---|---|---|
| Normal | TAL-RF-01 | Inicial | `TAL-DAN-01` cupo 10, 5 ocupadas; P-01 solicita antes del inicio | P-01 confirmado; 6 ocupadas |
| Normal | TAL-RF-03 | Inicial | Cupo 4 lleno, C y D en espera; A cancela a tiempo | C confirmado con aviso; D pasa a la posición 1 |
| Límite | TAL-RF-02 | Inicial | `TAL-FUT-01` lleno (20/20) y espera 4 de 4; P-11 solicita | «El taller y la lista de espera están llenos.»; nada cambia |
| Límite | TAL-RF-06 | Inicial | Taller a las 12:00; cancelar a las 8:30 y a las 9:30 | 8:30 se acepta; 9:30 «Ya pasó el tiempo límite para cancelar.» |
| Límite | TAL-RF-08 | Agregado | 3 cancelaciones en 72 h y luego una cuarta | Con 3 no se bloquea; con la cuarta queda bloqueado 24 h |
| Rechazo | TAL-RF-05 | Inicial | P-01 en `TAL-DAN-01` (10:00–12:00) pide `TAL-FUT-01` a la misma hora | «El participante ya tiene otro taller en este horario.»; conserva su inscripción |
| Rechazo | TAL-RF-09 | Agregado | P-01 pide plaza en un taller pendiente de aprobación | «El taller todavía no fue aprobado por el operador.»; nada cambia |
| Rechazo | TAL-RC-01 | Inicial | Dos pedidos a la vez por la última plaza | Uno confirmado y otro en espera; nunca sobrecupo |

En la versión inicial estos escenarios solo estaban especificados. Hoy todos están cubiertos por pruebas automáticas que pasan en `main` (`python -m pytest -q`).

## 5. Preguntas resueltas

Todas las preguntas que quedaron abiertas en la versión inicial fueron respondidas por el cliente y están implementadas. No quedan preguntas pendientes.

| Pregunta abierta en la versión inicial | Respuesta del cliente | Requisito | Dónde se refleja en el código |
|---|---|---|---|
| ¿Las notificaciones se envían de verdad por WhatsApp o basta con mostrarlas? | Basta con mostrarlas en pantalla (22/10). | TAL-RF-13 | `inscripciones/servicios/notificaciones.py` y la pantalla «Notificaciones» |
| Si se cancela un taller completo, ¿qué pasa con los inscritos y la espera? | Se cancelan todos y reciben el aviso en pantalla (22/10). | TAL-RF-11 | `Operador.cancelar_taller` |
| ¿Cómo se identifica a un troll y cuántas cancelaciones llevan a un bloqueo? | Por su código universitario; más de 3 cancelaciones en 72 horas bloquean 24 horas; el operador puede quitar el bloqueo y, si se repite, vuelve a ser de 24 horas (22/10). | TAL-RF-08 | `Operador.calcular_fin_del_bloqueo`, `Operador.verificar_que_no_este_bloqueado`, `Operador.levantar_bloqueo` y el modelo `HistorialBloqueo` |
| Si se reduce el cupo, ¿quiénes pasan a la espera? | El cupo no puede quedar por debajo de los confirmados; nadie pierde su plaza (22/10). | TAL-RF-07 | `Coordinador.editar_taller` |
| ¿Qué significa `PAR` en el identificador? | El formato cambió a `TAL-DAN-01`, sin `PAR` (reunión 02). | TAL-RT-02 | `Coordinador.abreviatura_actividad` y `Coordinador.siguiente_codigo` |
| ¿Cómo se redondea el 20 % de la espera? | Hacia arriba: cupo 12 → espera de 3. | TAL-RF-02 | `Operador.capacidad_lista_de_espera` |
| ¿Se podrá inscribir alguien después de que empiece el taller? | No: desde la hora de inicio se rechaza toda solicitud. | TAL-RF-01 | `Operador.verificar_que_el_taller_no_haya_empezado` |

## 6. Revisión

- **Revisión por otro equipo:** no se hizo revisión cruzada con otro equipo.
- **Revisión interna:** cada cambio entró a `main` por pull request revisado por otro integrante. Antes de la presentación se recorrieron todos los roles con entradas inválidas y combinaciones de funciones.
- **Correcciones que salieron de esa revisión:**
  - El choque de horario ahora también cuenta las inscripciones en espera (TAL-RF-05).
  - Rechazar una edición devuelve el taller a sus datos anteriores sin quitar plazas (TAL-RF-10).
  - No se puede aprobar un taller cancelado (TAL-RF-09).
  - El bloqueo no toca los talleres que ya empezaron (TAL-RF-08).
  - El coordinador solo ve sus talleres y su ocupación (TAL-RF-09, TAL-RF-14).
  - No se puede editar un taller cancelado (TAL-RF-10).
  - Levantar un bloqueo conserva todo el historial de cancelaciones y registra qué operador lo levantó (TAL-RF-08).

## 7. Siguiente paso

- **Tarea:** presentar al cliente el incremento final con el recorrido completo de la sección 9.2 y la suite de pruebas pasando en `main`.
- **Requisitos relacionados:** todos los de la sección 3
- **Responsable inicial:** todo el equipo

## 8. Participación y asistencia utilizada

- **Aportes de cada integrante:** los tres hicieron preguntas al cliente, redactaron requisitos y escribieron el código y las pruebas de las reglas que les correspondían. La distribución por tarea está en el diagrama de Gantt (`docs/DiagramaIncremento1.0.mpp`).
- **Asistencia de IA:** se usó un asistente de IA para ordenar las respuestas del cliente en la documentacion. Cada regla y cada mensaje se verificó contra `inscripciones/servicios/` y ejecutando `python -m pytest -q`.

## 9. Cumplimiento del encargo inicial

### 9.1 Alcance obligatorio (encargo P03)

| ID | Necesidad obligatoria | Requisitos | Casos de uso | Cómo se cumple | Estado |
|---|---|---|---|---|---|
| TAL-01 | Registrar talleres y participantes con identificadores únicos | TAL-RF-09, TAL-RT-02 | CU-01, CU-15 | Código de taller único (`TAL-DAN-01`); cada participante se identifica por su código universitario del padrón, que no se repite. | Cumple |
| TAL-02 | Consultar talleres, fechas, cupos y disponibilidad | TAL-RF-12, TAL-RF-14 | CU-03, CU-08 | Lista de talleres con fechas, cupo, plazas libres y espera; búsqueda por categoría; ocupación de cada taller. | Cumple |
| TAL-03 | Registrar una inscripción y asignar el estado que corresponda | TAL-RF-01, TAL-RF-02 | CU-04 | Confirmado si hay cupo, En espera con posición si está lleno, rechazo si la espera también está llena. | Cumple |
| TAL-04 | Evitar duplicados y aplicar las condiciones de inscripción | TAL-RF-01, 04, 05, 08, 09; TAL-RC-01 | CU-04 | Sin inscripción activa repetida; padrón, bloqueo, taller aprobado y no empezado, choque de horario; dos pedidos a la vez no superan el cupo. | Cumple |
| TAL-05 | Cancelar una inscripción y gestionar la plaza liberada | TAL-RF-03, TAL-RF-06 | CU-05 | Cancelar hasta 3 horas antes; la plaza pasa sola al primero en espera; repetir la cancelación no cambia nada. | Cumple |
| TAL-06 | Mantener una lista de espera y promover según la política acordada | TAL-RF-02, 03, 07 | CU-04, CU-05, CU-06 | Espera de hasta el 20 % del cupo en orden de llegada; promoción automática con aviso; posiciones sin huecos. | Cumple |
| TAL-07 | Corregir datos o cambiar el cupo conservando motivo e historial | TAL-RF-07, TAL-RF-10 | CU-06, CU-02, CU-14 | Edición de fechas y cupo con motivo parametrizado; historial con los datos anteriores; aprobación y vuelta atrás si se rechaza. | Cumple |
| TAL-08 | Mostrar listas de confirmados, espera, cancelaciones y resumen de ocupación | TAL-RF-08, TAL-RF-14 | CU-08, CU-09, CU-12, CU-13 | Ocupación por taller; búsqueda por taller con confirmados, espera en orden y cancelados; historial de cancelaciones. | Cumple |

**Personas interesadas del encargo:** coordinador, participante y operador están implementados como roles. El instructor se quitó por decisión del cliente (ENT-19); la lista de confirmados la consultan el operador (CU-13) y el coordinador con la ocupación de sus talleres (CU-08).

### 9.2 Recorrido que debe poder demostrarse

| Paso del encargo | Cómo se demuestra |
|---|---|
| Se publica un taller | El coordinador lo crea (CU-01) y el operador lo aprueba (CU-02). |
| Las personas se inscriben hasta ocupar las plazas y las siguientes pasan al estado acordado | Los participantes solicitan plaza (CU-04): quedan Confirmados y, con el taller lleno, En espera con su posición. |
| Una cancelación libera una plaza y se aplica la política de espera sin exceder la capacidad | Un confirmado cancela (CU-05): el primero en espera pasa a Confirmado y recibe el aviso (CU-10); la ocupación sigue igual al cupo (CU-08). |
| El operador puede explicar el orden de la lista y los cambios de estado | Busca por el código del taller (CU-13) y ve cada estado y posición; el historial de cancelaciones (CU-12) explica los bloqueos. |

Este recorrido está automatizado en `tests/e2e/test_recorridos.py` y en `tests/test_operador.py`.

### 9.3 Condiciones comunes del curso

| Condición | Cómo se cumple | Estado |
|---|---|---|
| Lógica principal en Python, con PyCharm, GitHub y pytest | Python con Django 6.1; cada cambio entra por pull request; 103 pruebas con pytest. | Cumple |
| Reglas de negocio separadas de la interfaz y del acceso a datos | Las reglas están en `inscripciones/servicios/`; las vistas solo las llaman y los HTML solo muestran. | Cumple |
| Un error produce un mensaje comprensible y no deja una operación incompleta | Cada rechazo muestra su causa (TAL-RC-02) y las operaciones corren en una transacción que se revierte entera si falla. | Cumple |
| La misma operación no se duplica por un reintento | Pedir dos veces el mismo taller se rechaza; cancelar dos veces no cambia nada; volver tras cancelar reutiliza el mismo registro. | Cumple |
| Una consulta no modifica datos | Lista de talleres, ocupación, búsqueda, mis inscripciones e historial solo leen. | Cumple |
| Se conservan los registros necesarios para explicar un resultado | Historial de cancelaciones, registro de bloqueos levantados (quién y cuándo), historial de ediciones con motivo, talleres cancelados que no se borran y avisos guardados. | Cumple |
| Diferenciar acciones del operador y consultas de otros usuarios | Roles con inicio de sesión; cada pantalla responde 403 a quien no le corresponde. | Cumple |
| Datos ficticios | Padrón de estudiantes y usuarios de demostración inventados, cargados con los pasos del `README.md`. | Cumple |
| Persistencia de los datos | Base de datos SQLite manejada con Django; los datos se conservan al reiniciar (TAL-RT-04). | Cumple |
| Fuera de alcance: pagos, certificados, asistencia, videoconferencias y envío real de mensajes | Ninguno se implementó; los avisos son solo en pantalla. | Cumple |

### 9.4 Entrega final común

| Se pide | Dónde está | Estado |
|---|---|---|
| Código | `inscripciones/`, `config/` | Cumple |
| Pruebas | `tests/` (77 unitarias, 21 de integración y 5 de punta a punta) | Cumple |
| Instrucciones de instalación y ejecución | `README.md` | Cumple |
| Esquema y datos de demostración de la base de datos | Migraciones en `inscripciones/migrations/`, comando `poblar_db` (categorías y motivos) y carga de datos de demostración descrita en el `README.md` | Cumple |
| Requisitos vigentes | Este documento (secciones 1 y 3) | Cumple |
| Relación entre requisitos y pruebas | Línea «Comprobado por» de cada requisito y tabla de requisitos, historias y casos de uso (sección 1) de [sesion-07-modelos.md](sesion-07-modelos.md) | Cumple |
| Registro breve de los cambios aprobados | Línea «Cambio posterior» de cada requisito y sección 17 de [sesion-07-modelos.md](sesion-07-modelos.md) | Cumple |
| Cómo ejecutar las pruebas sin modificar una base de datos real | Las pruebas usan bases propias (`test_db.sqlite3` y `test_estudiantes.sqlite3`), explicado en `README.md` | Cumple |