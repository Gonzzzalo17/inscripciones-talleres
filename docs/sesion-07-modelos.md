# Sesión 7 — Historias, casos de uso y modelos

- Proyecto: P03 — Inscripciones a talleres y listas de espera
- Integrantes: Gonzalo Cárdenas, Santiago Arauz, Andrea Trujillo
- Fecha: 2 de octubre de 2026
- Requisitos de origen: [Sesión 6](sesion-06-requisitos.md)
- Flujo seleccionado: Inscripción a un taller (Solicitud de plaza, control de cupo y lista de espera)
- IDs seleccionados y estado de aprobación: `TAL-RF-01` (Aprobado), `TAL-RF-02` (Aprobado por el cliente; redondeo pendiente), `TAL-RF-05` (Aprobado) y `TAL-RF-08` / `ENT-11` (Provisional - Historial de cancelaciones).

## 1. Historia TAL-HU-01

Como participante, quiero solicitar mi inscripción a un taller para asegurar una plaza disponible o quedar registrado en la lista de espera si la capacidad máxima está cubierta.

- Requisitos relacionados: `TAL-RF-01`, `TAL-RF-02`, `TAL-RF-05`, `TAL-RF-08`

## 2. Caso de uso TAL-CU-01 — Solicitar inscripción a un taller

- Objetivo: registrar la solicitud de un participante en un taller, asignándole una plaza confirmada o una posición en la lista de espera según la disponibilidad, las validaciones horarias y su historial de cancelaciones.
- Actor principal: participante.
- Disparador: el participante solicita inscribirse a un taller específico.
- Precondiciones: 
  - El taller y el participante existen en el sistema.
  - El participante no tiene una inscripción activa en ese mismo taller.
  - El participante no tiene más de 3 cancelaciones registradas en las últimas 72 horas (regla de restricción por historial - provisional).
- Poscondición de éxito: la solicitud se procesa correctamente; el participante queda en estado **Confirmada** (incrementando en 1 las plazas ocupadas) o en estado **En espera** (asignándole una posición en la lista).
- Garantía ante rechazo: el sistema rechaza la solicitud sin alterar el cupo ocupado, la lista de espera ni las inscripciones previas del participante.

### Flujo principal

1. El participante solicita inscribirse en un taller indicando su identificador y el del taller.
2. El sistema verifica que la hora actual sea anterior a la hora de inicio del taller (`TAL-RF-01`).
3. El sistema verifica el historial del participante y comprueba que no tenga más de 3 cancelaciones en las últimas 72 horas (`TAL-RF-08`).
4. El sistema verifica que el participante no tenga otra inscripción activa en un taller con choque de horario (`TAL-RF-05`).
5. El sistema evalúa la disponibilidad del taller:
   - Si las plazas ocupadas son menores al cupo máximo, el sistema crea la inscripción en estado **Confirmada** y aumenta en 1 las plazas ocupadas (`TAL-RF-01`).
6. El sistema confirma la inscripción exitosa y muestra el estado final.

### E1 — Rechazo por taller ya iniciado (Paso 2)

- Ocurre en el paso: 2.
- Condición: la solicitud se realiza en o después de la hora de inicio del taller.
- Respuesta del sistema: informa el mensaje «El taller ya empezó».
- Estado final y datos que se conservan: no se crea inscripción; el cupo ocupado y la lista de espera no sufren cambios.
- El caso termina en: rechazo.

### E2 — Rechazo por exceso de cancelaciones recientes (Paso 3)

- Ocurre en el paso: 3.
- Condición: el participante tiene más de 3 cancelaciones registradas en las últimas 72 horas.
- Respuesta del sistema: rechaza la solicitud con el mensaje «Inscripción bloqueada: superaste el límite de 3 cancelaciones en las últimas 72 horas».
- Estado final y datos que se conservan: no se crea inscripción; el cupo del taller y el historial del usuario se conservan sin modificaciones.
- El caso termina en: rechazo.

### E3 — Rechazo por choque de horario (Paso 4)

- Ocurre en el paso: 4.
- Condición: el participante ya posee una inscripción activa en otro taller en la misma franja horaria.
- Respuesta del sistema: informa el mensaje «Ya estás inscrito en otro taller a esa hora».
- Estado final y datos que se conservan: no se crea inscripción para el nuevo taller; la inscripción previa se conserva intacta.
- El caso termina en: rechazo.

### E4 — Asignación a lista de espera (Paso 5)

- Ocurre en el paso: 5.
- Condición: el taller está lleno (plazas ocupadas == cupo máximo), pero la lista de espera no ha alcanzado su capacidad máxima (20 % del cupo).
- Respuesta del sistema: registra al participante en estado **En espera**, asignándole la última posición disponible en la lista (`TAL-RF-02`).
- Estado final y datos que se conservan: la inscripción queda en estado **En espera**; las plazas ocupadas se mantienen al máximo; la lista de espera aumenta en 1.
- El caso termina en: éxito alternativo (en espera).

### E5 — Rechazo por cupo y lista de espera llenos (Paso 5)

- Ocurre en el paso: 5.
- Condición: las plazas del taller y el límite del 20 % de la lista de espera están cubiertos en su totalidad.
- Respuesta del sistema: rechaza la solicitud con el mensaje «El taller y la lista de espera están llenos».
- Estado final y datos que se conservan: no se crea registro de inscripción; el taller y la lista de espera permanecen sin modificaciones.
- El caso termina en: rechazo.

## 3. Modelo TAL-MOD-01

- Tipo elegido: Diagrama de flujo simplificado
- Pregunta que responde: ¿Qué condiciones determinan si la solicitud de un participante es confirmada, enviada a lista de espera o rechazada?
- Alcance y aspectos que deja fuera: no abarca los procesos de pago, envío de notificaciones reales (WhatsApp), la acción manual de cancelar ni la gestión de credenciales o autenticación del usuario.

```mermaid
flowchart TD
    A[Participante solicita inscripción] --> B{¿El taller ya inició?}
    B -- Sí --> C[Rechazar: 'El taller ya empezó']
    B -- No --> D{¿Tiene >3 cancelaciones en las últimas 72h?}
    D -- Sí --> E[Rechazar: 'Superaste el límite de cancelaciones']
    D -- No --> F{¿Tiene choque de horario con otro taller?}
    F -- Sí --> G[Rechazar: 'Ya estás inscrito en otro taller a esa hora']
    F -- No --> H{¿Hay plazas libres en el taller?}
    H -- Sí --> I[Registrar inscripción CONFIRMADA e incrementar cupo]
    H -- No --> J{¿La lista de espera superó el 20% del cupo?}
    J -- No --> K[Registrar inscripción EN ESPERA y asignar posición]
    J -- Sí --> L[Rechazar: 'El taller y la lista de espera están llenos']
    I --> M[Fin]
    K --> M
    C --> M
    E --> M
    G --> M
    L --> M