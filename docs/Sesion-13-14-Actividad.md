# Sesiones 13–14 — Revisión del estado del proyecto

## 1. Proyecto y versión revisada

- Proyecto: P03 — Inscripciones a talleres y listas de espera.
- Integrantes: Gonzalo Cárdenas, Santiago Arauz y Andrea Trujillo.
- Fecha real de la revisión: 14 de octubre de 2026.
- Operación revisada: solicitar inscripción a un taller (`registrar_inscripcion`, TAL-CU-01).
- Versión revisada:
  - Rama `main`, commit `a7239e1` (merge de la rama `gonzalo`, 14/10/2026).
  - Rama `sesion12`, commit `75e0e8e` (contiene `docs/sesion-12-arquitectura.md`, `tests/sesion12/` y el workflow de CI; **no está integrada en `main`**).
- Evidencias anteriores:
  - [Sesión 6](sesion-06-requisitos.md)
  - [Sesión 7](sesion-07-modelos.md)
  - [Sesiones 8–9](sesion-08-09-plan.md)
  - [Sesión 12](https://github.com/Gonzzzalo17/inscripciones-talleres/blob/sesion12/docs/sesion-12-arquitectura.md) (solo existe en la rama `sesion12`)
  - [CI #1 de la rama `sesion12`](https://github.com/Gonzzzalo17/inscripciones-talleres/actions/runs/38462841472), commit probado `8c4c22a`.
- Límite de esta revisión: las vistas y templates de la rama local de Santiago no están publicados (la rama `Santiago` remota está en el commit del 06/10 y su `views.py` está vacío), así que no se pudieron revisar.

## 2. Diagnóstico

| Punto # | Estado | Evidencia concreta | Hallazgo: qué está bien o qué falta |
|---|---|---|---|
| 1. Requisitos (S6) | P | `sesion-06-requisitos.md`: TAL-RF-01…07, TAL-RC-01, TAL-RT-01/02; `operador.py` L13 (`int(cupo * 0.20)`) | Las reglas tienen IDs, criterios y estado (aprobado/pendiente), pero el redondeo del 20 % sigue pendiente (ENT-07) y el código trunca; `TAL-RF-08` se cita en S7 y S8–9 pero no existe en S6; `Taller.codigo` no valida el formato `DAN-PAR-01` (TAL-RT-02). |
| 2. Flujo (S7) | P | `sesion-07-modelos.md` (flujo principal, E1–E5, TAL-MOD-01) vs `Operador.registrar_inscripcion` (`operador.py` L38–48) | Actor, objetivo y rechazos son coherentes, pero el código tiene pasos que el modelo no tiene (estudiante registrado en la BD estática, duplicado) y no tiene E2.
| 4. Responsabilidades (S12) | R | `models.py` L4–5 y `servicios/operador.py` L5–6; `servicios/reglas_service.py`; `docs/sesion-12-arquitectura.md` (solo en `sesion12`) | Las reglas (operador.py) están separadas de los datos (models.py), pero porcentaje_lista_espera y horas_limite_cancelacion están escritas dos veces, y falta la parte que habla con el usuario (views.py).
|
| 5. Estilo arquitectónico (S13) | P | Estructura `inscripciones/{models,servicios,views}.py`; `config/settings.py` L76–87 y `db_router.py` | El sistema está en capas (vistas → reglas → datos) para poder cambiar una parte sin romper las otras, y cada capa solo usa a la de abajo; la capa de vistas todavía no existe en main.|
| 6. Entidades y datos (S13–14) | R | `models.py` (`Taller`, `Inscripcion`, `HistorialCancelacion`, `Usuario`); `migrations/0001_initial.py` L117 | Hay entidades, estados y migración inicial (SQLite; MySQL/MariaDB es etapa posterior). Discrepancia: `unique_together(participante, taller)` impediría crear la nueva inscripción que pide TAL-RF-04 si ya existe una fila `CANCELADO`. |
| 7. Clases y relaciones (S14) | P | `models.py` (Usuario → AbstractUser, perfiles `Coordinador/Operador/Participante/Instructor`, `Inscripcion` → `Usuario` y `Taller`) | Las relaciones Taller 1—* Inscripcion y Usuario 1—* Inscripcion son correctas y la herencia de `AbstractUser` es una especialización real; el rol está duplicado (campo `rol` y cuatro clases perfil) y no hay diagrama de clases en `docs/` (pendiente). |
| 8. Interfaz y secuencia (S12–14) | R | `operador.py` L40–48 vs `reglas_service.py` L20–38; no hay diagrama de secuencia | Cada paso del modelo (salvo E2) tiene su operación receptora con entradas y salidas compatibles, y los rechazos llegan antes de escribir; falta la interfaz que llame a la operación (views.py vacío), el diagrama de secuencia y pruebas que lo comprueben.|
| 9. Pruebas y CI | F | `tests/test_reglas.py` L1 y L3; `.github/` (no existe en `main`); CI #1 en `sesion12` | Se evaluara de acuerdo al diagrama de Gantt respecto a cada logica |
| 10. Documentación y comprensión | P | `README.md`; `sesion-12-arquitectura.md` §5 | La decisión A vs B tiene objetivo, alternativas y compromisos, pero README solo describe el proyecto y no dice cómo instalar ni ejecutar nada. |

## 3. Caso crítico

- **Requisitos relacionados:** TAL-RF-01 (plaza disponible), TAL-RF-02 (espera con límite del 20 %) y la precondición de TAL-CU-01 (sin inscripción activa en el mismo taller).
- **Recorrido revisado:** taller de cupo 2 con P-01 y P-02 confirmados; P-02 repite; después P-03 solicita plaza. Leí requisito → modelo S7 → `Operador.registrar_inscripcion` (`operador.py`). Como `views.py` está vacío, el caso se recorrió directamente en la función, no desde una interfaz.
- **Resultado esperado:** la repetición de P-02 se rechaza sin cambiar nada; P-03 no obtiene plaza; los confirmados siguen siendo exactamente dos.
- **Qué hace el código:**
  - Repetición de P-02: `verificar_que_el_usuario_no_este_inscrito` (L99–106) consulta los estados `CONFIRMADO` y `EN_ESPERA` y lanza `ValidationError` antes de calcular el cupo y sin escribir. La inscripción de P-02 se conserva.
  - Solicitud de P-03: `confirmados = 2` (L44) no es menor que el cupo, entonces entra a `agregar_a_lista_de_espera`; con `int(2 * 0.20) = 0` (L13) no cabe nadie en espera y lanza «El taller y la lista de espera están llenos» (L22). Los confirmados siguen en 2.
- **Resultado: correspondencia correcta, con una condición.** El recorrido coincide con el modelo de S7 (duplicado antes del cupo, rechazo sin escribir, dos confirmados). Pero el rechazo de P-03 depende de que el 20 % se trunque (ENT-07 pendiente): con otro redondeo, P-03 podría quedar en espera. Además, este comportamiento solo se verificó leyendo el código; todavía no tiene pruebas (**NV**).
- **Dos fortalezas que conviene conservar:**
  1. Todas las verificaciones (L39–42) ocurren antes de cualquier escritura (L46 y L16), y el duplicado se revisa antes que el cupo, igual que en S7. Así los rechazos conservan los datos.
  2. Las plazas ocupadas se cuentan solo con estado `CONFIRMADO` (L44), así que las inscripciones `EN_ESPERA` y `CANCELADO` no ocupan plaza y el historial se conserva sin afectar el cupo.

## 4. Correcciones prioritarias

| Prioridad | Problema | Cambio posterior | Cómo comprobaremos la corrección | Responsable / tarea del plan |
|---|---|---|---|---|
| Alta | El redondeo del 20 % no está definido (ENT-07) y el código trunca con `int()`: con cupo 2 la lista de espera es 0 y con cupo menor a 5 nunca hay espera. | Consultar al docente cómo se redondea, registrar la regla en S6 y ajustar `agregar_a_lista_de_espera` (L13) a esa regla. | Casos documentados con resultado esperado: cupo 2 (caso de P-03) y cupo 12, y la prueba del caso crítico pasa con la regla acordada. | Andrea; riesgo del redondeo en el plan (tarea A). |
| Media | `porcentaje_lista_espera` y `horas_limite_cancelacion` están definidas dos veces (`models.py` L4–5 y `operador.py` L5–6). | Dejar una sola definición e importarla desde el otro archivo. | Una búsqueda en el código encuentra cada constante definida una sola vez y cambiar el valor en un lugar afecta a todo el flujo. | Gonzalo; tarea D. |
| Media | S6 y S7 no coinciden con el código: `TAL-RF-08` se cita pero no existe en S6, E2 usa una regla de 3 cancelaciones en 72 h que el cliente no aprobó, y los pasos «estudiante registrado» y «duplicado» están en el código pero no en el modelo. | Definir `TAL-RF-08` como provisional en S6, marcar E2 como pendiente de ENT-11, y agregar al modelo de S7 los pasos que el código ya tiene. | Revisión cruzada: cada ID citado en S7 y S8–9 existe en S6, y cada paso del código tiene su paso en S7. | Andrea y Gonzalo; tarea A. |

**Conclusión sobre el incremento:** necesita correcciones. No está bloqueado, porque las reglas del flujo ya están en `Operador` y el caso crítico es coherente con el modelo. Pero el redondeo sin definir y los documentos desalineados impiden dar por comprobado el flujo, y falta la interfaz. También queda registrado para revisar antes de implementar TAL-RF-04 que `unique_together(participante, taller)` choca con volver a inscribirse después de cancelar.