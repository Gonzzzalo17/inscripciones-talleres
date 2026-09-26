# Sesión 04 — Procesos de desarrollo: Scrum y prácticas de XP

**Punto de partida:** el proyecto asignado en la Sesión 02 y el flujo de colaboración practicado en la Sesión 03.

## 1. El desafío

**Entregar una pequeña capacidad de su proyecto que el cliente pueda verificar.**

El equipo deberá decidir qué vale la pena construir ahora, aclarar su comportamiento con el docente, implementarlo mediante pruebas y programación en grupo, y demostrar el resultado. Al terminar, utilizará la retroalimentación para decidir qué hacer después.

Esta actividad es una simulación educativa abreviada. Practicamos elementos de Scrum y algunas prácticas de Extreme Programming (XP).

Al finalizar podrán:

- Justificar la prioridad de una capacidad y delimitar un objetivo alcanzable.
- Diferenciar un requisito, una tarea técnica y una prueba.
- Convertir acuerdos con el cliente en ejemplos verificables.
- Desarrollar en grupos (parejas) mediante ciclos de prueba, implementación y mejora del código.
- Inspeccionar el producto y su forma de trabajar, y proponer una adaptación concreta.

**No se entrega una solución modelo.** Las reglas específicas deben surgir de su proyecto y de las respuestas del cliente. Una implementación que funciona pero resuelve un problema distinto no cumple el objetivo.

## 2. Qué estamos practicando

Scrum organiza el trabajo alrededor de objetivos, resultados inspeccionables y adaptación. XP aporta prácticas de desarrollo que utilizaremos para construir y comprobar el software. Se pueden combinar; programar en grupo no es un requisito de Scrum.

| Elemento | Aplicación en esta sesión |
|---|---|
| Product Backlog | Lista ordenada de capacidades pendientes del producto. |
| Objetivo de la iteración | Resultado útil que el equipo intentará conseguir hoy. |
| Plan de trabajo | Capacidad seleccionada y tareas para alcanzar el objetivo. Practica la función de un Sprint Backlog. |
| Incremento | Capacidad integrada y utilizable dentro del alcance acordado. |
| Definition of Done | Condiciones compartidas para considerar terminado el trabajo. |
| Revisión | Inspección del resultado con el cliente para orientar el trabajo futuro. |
| Retrospectiva | Inspección de la forma de trabajar del equipo para mejorarla. |

El tablero de tareas es una ayuda de esta práctica. Tener columnas y mover tarjetas no demuestra, por sí solo, que el equipo esté aplicando Scrum.

## 3. Tiempo y responsabilidades


| Minutos de laboratorio | Actividad | Evidencia mínima |
|---|---|---|
| 0–15 | Ordenar capacidades y seleccionar un objetivo. | Backlog de 4–6 elementos y objetivo. |
| 15–25 | Consultar al cliente, acordar ejemplos y organizar tareas. | Reglas aclaradas, ejemplos y plan. |
| 25–45 | Primer bloque de desarrollo en grupo. | Una prueba y comportamiento implementado. |
| 45–50 | Inspeccionar progreso y ajustar el plan. | Obstáculo o riesgo identificado y siguiente acción. |
| 50–70 | Completar, revisar e integrar. | Código y pruebas integrados. |
| 70–82 | Demostrar y recibir retroalimentación. | Resultado observable y siguiente prioridad. |
| 82–90 | Retrospectiva y cierre grupal. | Una mejora concreta y entrega. |

Es importante realizar revisiones breves por grupo. Esto depende de ustedes y su forma de trabajo que es constantemente evaluada.

### Dentro del equipo

- **Todos desarrollan y deben poder explicar el resultado.** No asignen a alguien exclusivamente a copiar documentación.
- Un integrante facilita la conversación y controla el tiempo; también participa en el trabajo técnico. Esta función de aula no representa todas las responsabilidades de un Scrum Master.
- El docente o uno de ustedes representa al cliente y proporciona decisiones de prioridad para la simulación. Los desarrolladores organizan cómo realizar el trabajo.
- En el grupo, una persona escribe, la otra revisa activamente la lógica y la ultima valida el flujo del sprint, los ejemplos y los riesgos. Intercambien posiciones aproximadamente cada diez minutos.
- En equipos, roten quién formula y verifica casos, quién escribe y quién acompaña la implementación.

## 4. Preparar el repositorio del proyecto

Utilicen el repositorio de su proyecto semestral. **No cambien el nombre del repositorio de Campus Challenge para convertirlo en otro proyecto.** Reutilizamos su flujo de trabajo, no necesariamente sus funciones ni sus requisitos R-01 a R-08.

Si todavía no existe el repositorio, una persona lo crea en GitHub con README, invita al equipo y prepara los archivos mínimos. Los demás aceptan la invitación y lo clonan. Apliquen las instrucciones de la Sesión 03 para autenticación, identidad Git y entorno virtual.

Si ya existe código o una organización de carpetas, consérvenlos. Para un proyecto nuevo pueden empezar con:

| Ruta | Propósito |
|---|---|
| `proyecto/__init__.py` | Archivo vacío que identifica el paquete. |
| `proyecto/reglas.py` | Funciones de la capacidad seleccionada. |
| `tests/test_reglas.py` | Pruebas de esas funciones. |
| `docs/sesion04.md` | Acuerdos y registro breve de la práctica. |
| `README.md` | Propósito del proyecto y ejecución. |
| `requirements.txt` | `pytest>=8,<10`. |
| `pytest.ini` | Configuración de pruebas. |
| `.gitignore` | Excluye entorno virtual, cachés y archivos locales del editor. |

Configuración mínima de `pytest.ini`, si el proyecto aún no tiene otra equivalente:

```ini
[pytest]
testpaths = tests
pythonpath = .
```

Desde la raíz y con el entorno virtual activado:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Si el proyecto es nuevo y todavía no tiene pruebas, pytest indicará que no encontró ninguna. Eso no demuestra que el programa sea correcto: aún deben escribir y ejecutar las pruebas.

**Alcance técnico:** para esta sesión bastan Python, colecciones en memoria y pytest. No necesitan interfaz gráfica, servidor web ni base de datos. La capacidad debe poder utilizarse y comprobarse desde código. No dediquen la práctica a instalar infraestructura.

## 5. Construir un backlog pequeño y ordenado

Revisen el enunciado de su proyecto. Identifiquen entre cuatro y seis capacidades que aporten valor a un usuario.

Escriban una línea por capacidad en `docs/sesion04.md`:

| Orden | ID | Capacidad | ¿A quién ayuda y para qué? | Duda pendiente |
|---|---|---|---|---|
| 1 | PB-01 | Completar | Completar | Completar |

Los identificadores PB-01, PB-02, etc. pertenecen a su backlog; no sustituyen identificadores de requisitos ya establecidos.

Distingan:

- **Capacidad:** algo que una persona podrá conseguir con el producto.
- **Tarea:** trabajo necesario para construir esa capacidad, como escribir una prueba o implementar una validación.

«Crear un archivo Python» es una tarea; no explica el valor del producto.

Para ordenar, discutan:

1. ¿Qué necesidad es más importante para el cliente?
2. ¿Qué parte permite comprobar pronto una regla incierta?
3. ¿Qué depende de otras capacidades que todavía no existen?
4. ¿Cuál puede quedar utilizable durante esta clase?

Registren una razón concreta para la primera prioridad. No basta «porque es la más importante». Si tienen una duda que afecta al orden, consulten al profe o sean criticos con la respuesta de su LLM.

## 6. Elegir una capacidad y un objetivo

Estas son propuestas de alcance inicial. **Contrástenlas con el enunciado del proyecto y confirmen las reglas que aún no estén acordadas.**

| Proyecto | Capacidad propuesta | Preguntas que deben resolver |
|---|---|---|
| Préstamos de equipos | Registrar un préstamo de un equipo disponible y rechazar otro préstamo activo del mismo equipo. | ¿Cómo se identifica el equipo? ¿Qué significa disponible? ¿Cómo se informa un rechazo? |
| Reservas de espacios | Aceptar una reserva cuando no se solapa con otra del mismo espacio. | ¿Se permite que una reserva empiece cuando otra termina? ¿Qué sucede si el intervalo tiene duración cero? |
| Inscripción a talleres | Inscribir mientras existan cupos y evitar una inscripción duplicada. | ¿Qué identifica a una persona? ¿Qué ocurre cuando se llena el taller? |
| Plataforma CTF | Calcular la puntuación de una resolución correcta considerando penalización por intentos incorrectos y un tope configurable. | ¿Qué parámetros recibe? ¿Cómo se aplica el tope? ¿Puede resultar una puntuación negativa? |

En CTF, la validación de banderas, la clasificación general y el bono por primera resolución quedan fuera de esta primera capacidad. Se pueden mantener en el backlog para después. No inventen valores predeterminados ni reglas de puntuación sin confirmarlos.

Si una capacidad ya está implementada, identifiquen un comportamiento pendiente relacionado y confirmen el nuevo alcance con el docente. No borren código correcto para repetir trabajo.

Escriban su objetivo en una sola frase:

> Al finalizar, [persona usuaria] podrá [resultado observable] bajo [condiciones esenciales acordadas].

**Pregunta de control:** ¿pueden demostrar el objetivo con una ejecución breve? Si necesitan explicar muchas funcionalidades todavía inexistentes, reduzcan el alcance.

## 7. Consultar al cliente y definir ejemplos

Antes de programar, lleven al docente dos o tres preguntas cuya respuesta pueda cambiar su implementación. Eviten preguntas vagas como «¿está bien nuestro proyecto?».

Para cada aclaración, registren brevemente:

| Pregunta | Respuesta del cliente | Efecto sobre el comportamiento esperado |
|---|---|---|
| Completar | Completar con la respuesta real | Completar |

No escriban «aprobado por el cliente» si no hubo consulta. Si una decisión sigue pendiente, márquenla como pendiente y acuerden cómo continuar sin asumirla silenciosamente.

A continuación definan **al menos tres ejemplos**, antes de escribir la implementación:

| Caso | Estado inicial y entrada | Resultado esperado | Regla que lo justifica |
|---|---|---|---|
| Uso normal | Datos concretos | Resultado concreto | Regla acordada |
| Límite | Datos concretos en una frontera | Resultado concreto | Regla acordada |
| Rechazo o situación excepcional prevista | Datos concretos | Resultado concreto | Regla acordada |

«Debe funcionar» no es un resultado esperado. Si una operación cambia el estado, indiquen también qué debe quedar registrado y qué debe permanecer igual. Si solo calcula un valor, indiquen ese valor y expliquen cómo lo obtuvieron.

Para CTF, el tercer caso puede ser una combinación de parámetros que fuerce a aplicar el tope; no agreguen validaciones arbitrarias para cumplir la tabla.

Elijan entradas propias. Un ejemplo copiado sin poder justificar su salida no demuestra comprensión del requisito.

## 8. Acordar qué significa terminado

Los ejemplos anteriores describen **el comportamiento de esta capacidad**. La siguiente Definition of Done describe **las condiciones de calidad para considerar terminado el trabajo**:

- Los ejemplos acordados tienen pruebas ejecutables que pasan.
- Las pruebas anteriores del proyecto continúan pasando.
- El código fue revisado por otro integrante.
- La contribución está integrada en `main` y fue comprobada allí.
- El README permite ejecutar las pruebas.
- El equipo puede demostrar el resultado y explicar sus límites.

No reduzcan estas condiciones al final para presentar trabajo incompleto como terminado. Una capacidad parcialmente implementada puede discutirse con el cliente, pero debe identificarse como pendiente.

Dividan el trabajo en entre tres y cinco tareas concretas. Registren su estado como **Por hacer**, **En curso**, **En revisión** o **Terminado** en el mismo documento o en un tablero que ya utilicen. No necesitan configurar GitHub Projects durante esta práctica.

| Tarea | Personas que colaboran | Estado | Evidencia o ubicación |
|---|---|---|---|
| Completar | Completar | Por hacer | Archivo, prueba o PR |

Definan juntos la interfaz mínima de la función: entradas, resultado y forma de representar el estado. Esto evita que una pareja escriba pruebas para una interfaz y otra implemente una distinta.

## 9. Desarrollar en pareja: prueba, implementación y refactorización

Trabajen en una rama. Con el trabajo previo registrado y `git status` limpio:

```bash
git switch main
git pull --ff-only origin main
git switch -c iteracion01/capacidad-acordada
```

Sustituyan `capacidad-acordada` por una descripción breve. Una pareja puede trabajar conjuntamente en una rama; eviten editar y publicar esa misma rama desde dos computadoras al mismo tiempo.

### Paso A — Escribir una prueba

Seleccionen uno de sus ejemplos y conviértanlo en una prueba con tres partes:

1. Preparar el estado y las entradas.
2. Invocar la función real del proyecto.
3. Comparar el resultado y, cuando corresponda, el estado posterior con lo acordado.

Usen nombres que expliquen el comportamiento, como `test_rechaza_...` o `test_acepta_...`, completados con la condición concreta.

No calculen el resultado esperado llamando a la misma función que están probando. No creen una prueba que solo compare dos constantes y nunca use el programa.

### Paso B — Ejecutar y comprender

```bash
python -m pytest tests/test_reglas.py -q
```

Si la capacidad todavía no existe, puede fallar inicialmente. Primero distingan un problema de importación o una función ausente de un fallo del comportamiento esperado. Preparen la interfaz mínima y comprueben que la prueba evalúa la regla que pretenden desarrollar.

**No introduzcan un defecto en código correcto para fabricar una prueba fallida.** Si la prueba ya pasa, comprueben qué evidencia nueva aporta y continúen con otro comportamiento pendiente.

### Paso C — Implementar el comportamiento necesario

Escriban el código que satisface la regla acordada. Eviten agregar anticipadamente usuarios, pantallas, bases de datos o reglas de futuras iteraciones.

Pasar un único ejemplo devolviendo siempre su resultado no implementa una regla general. Elijan otro caso válido que permita distinguir ambos comportamientos.

### Paso D — Mejorar sin alterar el comportamiento

Cuando las pruebas pasen, inspeccionen nombres, duplicación y claridad. Si hay una mejora justificada, realícenla y vuelvan a ejecutar:

```bash
python -m pytest -q
```

Refactorizar conserva el comportamiento; cambiar una regla de negocio requiere un acuerdo distinto. No hagan modificaciones cosméticas únicamente para afirmar que refactorizaron.

Repitan el ciclo con los demás ejemplos. Intercambien quién escribe y quién revisa. Quien acompaña debe anticipar un caso, cuestionar una decisión o detectar un riesgo; mirar en silencio no constituye colaboración activa.

## 10. Punto de inspección de cinco minutos

Detengan brevemente la escritura de código y respondan entre ustedes:

1. ¿Qué comportamiento está comprobado ahora mismo?
2. ¿Qué falta para alcanzar el objetivo y la Definition of Done?
3. ¿Cuál es el obstáculo principal?
4. ¿Qué vamos a hacer en los siguientes veinte minutos?

Este punto de coordinación es una adaptación de aula, no un Daily Scrum completo ni un reporte de actividad al docente.

Actualicen el plan. Si seleccionaron demasiado trabajo, hablen con el cliente para recortar alcance conservando un resultado útil. No eliminen silenciosamente una regla acordada para terminar más rápido.

## 11. Revisar e integrar con GitHub

Antes de abrir el PR:

```bash
python -m pytest -q
git status
git diff
```

Agreguen únicamente los archivos relacionados con el cambio. Para la estructura propuesta, un ejemplo es:

```bash
git add proyecto/reglas.py tests/test_reglas.py docs/sesion04.md
git diff --cached
git commit -m "Implementa capacidad acordada con pruebas"
git push -u origin iteracion01/capacidad-acordada
```

Adapten rutas y mensaje al cambio real. Agreguen el README u otros archivos de configuración solo si también los modificaron y revisaron.

En el PR, expliquen brevemente:

- Objetivo y elemento del backlog que atiende.
- Regla aclarada con el cliente que influyó en el código.
- Pruebas ejecutadas y resultado observado.
- Qué queda fuera del alcance.

Otro integrante revisa la correspondencia entre acuerdos, pruebas e implementación. En equipos de dos, quien acompañó la programación realiza una segunda lectura explícita del PR; reconozcan que participó en la solución y no representa una revisión independiente.

Si `main` cambió mientras trabajaban, con sus cambios registrados incorporen la versión reciente en su rama:

```bash
git fetch origin
git merge --no-edit origin/main
python -m pytest -q
git push
```

Resuelvan cualquier conflicto antes de continuar y revisen el resultado actualizado. Después de fusionar el PR en GitHub:

```bash
git switch main
git pull --ff-only origin main
python -m pytest -q
```

**La versión que se demuestra es la integrada.** Que GitHub permita fusionar un PR no implica que haya ejecutado sus pruebas.

En esta práctica se admite un PR conjunto por capacidad, con participación identificada. El énfasis está en la colaboración de la pareja y el objetivo común; no se exige un PR individual por persona como en la Sesión 03.

## 12. Demostrar y recibir retroalimentación

Preparen una demostración breve, sin diapositivas:

1. Expliquen el objetivo y una regla que aclararon con el cliente.
2. Ejecuten un caso normal y uno de límite o rechazo. Pueden usar pruebas identificables o una llamada breve a la función.
3. Muestren el resultado de la suite completa sobre `main`.
4. Indiquen qué está terminado y qué sigue pendiente.

El docente podrá proponer una entrada distinta **dentro de las reglas acordadas** y pedir que anticipen su resultado antes de ejecutarla. Si la pregunta introduce una regla nueva, identifíquenla como tal y soliciten aclaración.

Durante la revisión, el cliente planteará una necesidad posterior o una modificación. El equipo debe:

- Explicar qué parte del producto afecta.
- Aclarar las dudas relevantes.
- Agregar o actualizar un elemento del backlog.
- Justificar su prioridad respecto de los elementos existentes.

No necesitan implementar la nueva petición en el tiempo de cierre. Si el comentario revela que incumplieron un requisito ya acordado, registren un defecto pendiente; no lo presenten como una funcionalidad nueva.

## 13. Retrospectiva y comparación de procesos

Revisión y retrospectiva tienen propósitos distintos: la primera inspecciona el producto con el cliente; la segunda inspecciona cómo trabajó el equipo.

Escriban tres frases basadas en lo ocurrido:

1. **Mantener:** una práctica útil y la evidencia de que ayudó.
2. **Cambiar:** una dificultad concreta y su efecto.
3. **Experimentar:** una acción para la siguiente iteración, quién la impulsará y cómo comprobarán si ayudó.

«Comunicarnos mejor» es demasiado general. Describan una conducta observable y en qué momento la aplicarán.

Respondan también, de forma breve:

- ¿Qué decisión necesitaba planificación antes de programar?
- ¿Qué decisión pudieron mejorar gracias a una prueba o a la revisión del cliente?
- ¿En qué contexto de su proyecto sería útil fijar más detalles por anticipado? ¿Qué costo tendría hacerlo si las reglas todavía cambian?

La actividad no demuestra que un único modelo sea siempre superior. Justifiquen la elección según la estabilidad de los requisitos, la incertidumbre y las consecuencias de equivocarse.

## 14. Registro mínimo y entrega

Centralicen el registro en `docs/sesion04.md`. Utilicen estas secciones y completen solo con información real del equipo:

```markdown
# Iteración de la Sesión 04

## Equipo y proyecto
Integrantes y proyecto asignado.

## Backlog ordenado
Entre cuatro y seis capacidades y razón de la primera prioridad.

## Objetivo y alcance
Resultado acordado y límites.

## Aclaraciones del cliente
Preguntas, respuestas reales y decisiones pendientes.

## Ejemplos de aceptación
Estado inicial, entrada, resultado esperado y regla.

## Plan y seguimiento
Tareas, participantes, estado y ajuste del punto de inspección.

## Verificación e integración
Pruebas ejecutadas, resultado, enlace del PR y commit demostrado.

## Retroalimentación
Petición o defecto identificado y cambio correspondiente en el backlog.

## Retrospectiva
Mantener, cambiar y experimentar.

## Planificación y adaptación
Respuestas breves sobre las decisiones tomadas y su contexto.
```

No escriban un informe extenso. Se valoran decisiones concretas y evidencia verificable. Una persona puede consolidar el documento, pero todo el equipo debe conocerlo. La actualización final de revisión y retrospectiva puede integrarse mediante un PR breve de documentación después de la demostración.

Entreguen el enlace del repositorio y del PR principal, con acceso para el docente. No se requiere ZIP ni capturas de cada comando.

| Criterio | Evidencia esperada |
|---|---|
| Priorización | Razón vinculada a una necesidad y al alcance disponible. |
| Clarificación | Una decisión de implementación conectada con una respuesta real del cliente. |
| Verificación | Casos normales y límites derivados de acuerdos; resultados explicables. |
| Prácticas de desarrollo | Participación efectiva en pareja y pruebas utilizadas para orientar el trabajo. |
| Integración | Contribución revisada y suite aprobada en la versión demostrada. |
| Adaptación | Backlog actualizado a partir de retroalimentación concreta. |
| Aprendizaje del equipo | Mejora de proceso específica para la siguiente iteración. |
| Comprensión individual | Cada integrante puede explicar una regla, una prueba y su contribución. |

No se evalúa quién acumula más líneas de código o más commits. Todos los proyectos tienen la misma exigencia de planificación, verificación, integración y explicación.

## 15. Preguntas individuales de cierre

El docente puede seleccionar una o más:

1. ¿Por qué eligieron esa capacidad antes que otra de su backlog?
2. ¿Qué respuesta del cliente cambió o confirmó su diseño?
3. ¿Cómo obtuvieron el resultado esperado de una de sus pruebas?
4. ¿Qué caso mostraría que una implementación aparentemente correcta es insuficiente?
5. ¿Qué diferencia hay entre su ejemplo de aceptación y su Definition of Done?
6. ¿Qué hizo tu compañero mientras tú escribías? ¿Qué aportaste cuando cambiaron de posición?
7. ¿Qué comentario de la revisión cambió el backlog?
8. ¿Qué elemento de Scrum y qué práctica de XP pueden señalar en su trabajo real?

Una herramienta de IA puede ayudarles a consultar conceptos si la política del curso lo permite. No puede proporcionar la respuesta del cliente, sustituir la ejecución de pruebas ni demostrar por ustedes la comprensión de su código. La evidencia se comprueba sobre el repositorio y mediante sus explicaciones.

## 16. Si se bloquean

| Situación | Siguiente acción |
|---|---|
| Todo parece prioritario | Comparen valor, dependencia e incertidumbre; pidan al cliente elegir entre dos opciones concretas. |
| No hay acuerdo sobre el resultado | Pausen esa decisión y formulen un ejemplo pequeño para el cliente. |
| El alcance no cabe | Recorten capacidades futuras; mantengan las reglas esenciales del objetivo acordado. |
| La prueba falla al importar | Verifiquen la raíz, el paquete, los nombres y `pytest.ini` antes de modificar la lógica. |
| Todas las pruebas pasan desde el inicio | Comprueben si hay comportamiento pendiente; no reintroduzcan defectos. |
| No saben qué probar | Busquen fronteras en capacidad, intervalos, duplicación o topes según su proyecto. |
| Un integrante monopoliza el teclado | Cambien de posición y pidan a la otra persona explicar el siguiente caso. |
| Aparece una regresión | Identifiquen la regla afectada; no eliminen la prueba para terminar. |
| La capacidad queda incompleta | Demuestren honestamente lo comprobado y mantengan lo restante pendiente. |
| La revisión pide algo nuevo | Aclaren su valor y prioridad antes de prometer una implementación. |

## 17. Fuentes de consulta

La actividad, sus tiempos, preguntas y alcances son una adaptación docente para este curso. Las fuentes siguientes respaldan los conceptos y procedimientos generales; no contienen una solución de estos proyectos.

- Schwaber, K. y Sutherland, J. (2020). [The Scrum Guide](https://scrumguides.org/scrum-guide.html). Marco, responsabilidades, eventos, artefactos y compromisos.
- Agile Alliance. [Extreme Programming (XP)](https://agilealliance.org/glossary/xp/). Prácticas de desarrollo y colaboración.
- GitHub Docs. [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow). Colaboración mediante ramas y pull requests.
- pytest. [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html). Organización y descubrimiento de pruebas.
