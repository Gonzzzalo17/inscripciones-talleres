# P03 — Inscripciones a talleres y listas de espera

Sistema web para que una organización publique talleres con cupo limitado, inscriba participantes, maneje la lista de espera y explique por qué alguien sigue esperando. Proyecto de Ingeniería de Software (UPB).

**Integrantes:** Andrea Trujillo Antezana, Gonzalo Andres Cárdenas Vargas, Santiago Arauz Peña

---

## Contenido

1. [Qué hace el sistema](#1-qué-hace-el-sistema)
2. [Qué necesitas instalar](#2-qué-necesitas-instalar-una-sola-vez)
3. [Descargar el proyecto](#3-descargar-el-proyecto)
4. [Preparar el entorno](#4-preparar-el-entorno-una-sola-vez)
5. [Usar el sistema](#5-usar-el-sistema)
6. [Ejecutar las pruebas](#6-ejecutar-las-pruebas)
7. [Problemas comunes](#7-problemas-comunes)
8. [Estructura del proyecto](#8-estructura-del-proyecto)
9. [Documentación](#9-documentación)

---

## 1. Qué hace el sistema

| Rol | Puede |
|---|---|
| **Participante** | Crear su cuenta con su código universitario, ver y buscar talleres (también por categoría), inscribirse, ver el estado de sus inscripciones, cancelar hasta 3 horas antes del inicio y ver sus avisos. |
| **Coordinador** | Crear talleres (quedan pendientes hasta que el operador los aprueba), editar las fechas y el cupo de sus talleres eligiendo un motivo, cancelarlos y ver su ocupación. |
| **Operador** | Todo lo anterior sobre cualquier taller; además aprueba o rechaza talleres, inscribe y cancela a nombre de un participante, busca inscripciones, revisa el historial de cancelaciones, levanta bloqueos y agrega categorías y motivos de edición. |

**Reglas principales**

- El cupo de un taller va de 4 a 40 personas.
- Con el taller lleno, la persona entra a la lista de espera, que admite hasta el 20 % del cupo (redondeado hacia arriba).
- Cuando se libera una plaza, el primero de la espera pasa a confirmado automáticamente y recibe un aviso.
- Nadie puede estar en dos talleres a la misma hora.
- Se puede cancelar hasta 3 horas antes del inicio.
- Quien cancela más de 3 veces en 72 horas queda bloqueado 24 horas. El operador puede levantar el bloqueo.

---

## 2. Qué necesitas instalar (una sola vez)

| Programa | Para qué | Dónde descargarlo |
|---|---|---|
| **Python 3.12 o más nuevo** | Ejecutar el sistema | https://www.python.org/downloads/ |
| **Git** | Descargar el proyecto | https://git-scm.com/downloads |
| Un navegador (Chrome, Edge o Firefox) | Usar el sistema | — |
| PyCharm (opcional) | Ver y editar el código | https://www.jetbrains.com/pycharm/ |

> **Al instalar Python en Windows:** en la primera pantalla del instalador marca la casilla **«Add python.exe to PATH»** antes de presionar *Install Now*.

Para comprobar la instalación, abre **PowerShell** (Windows) o la **Terminal** (Mac o Linux) y escribe:

```bash
python --version
git --version
```

Cada comando debe mostrar un número de versión. Si dice que no se reconoce, cierra la ventana, ábrela de nuevo y vuelve a probar; si sigue igual, reinstala marcando la opción del PATH.

---

## 3. Descargar el proyecto

Ve a la carpeta donde quieres guardarlo (por ejemplo `C:\proyectoSoftware`) y descarga el repositorio:

```bash
cd C:\proyectoSoftware
git clone https://github.com/Gonzzzalo17/inscripciones-talleres.git
cd inscripciones-talleres
```

Desde aquí, **todos los comandos se ejecutan dentro de la carpeta `inscripciones-talleres`**.

---

## 4. Preparar el entorno (una sola vez)

### 4.1 Crear el entorno virtual

El entorno virtual es una carpeta `.venv` donde se instalan las librerías del proyecto sin mezclarlas con otras.

```bash
python -m venv .venv
```

### 4.2 Activarlo

| Sistema | Comando |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |
| Mac o Linux | `source .venv/bin/activate` |

Cuando está activo, la línea de comandos empieza con `(.venv)`. **Hay que activarlo cada vez que abras una ventana nueva.**

> Si PowerShell dice *«la ejecución de scripts está deshabilitada en este sistema»*, ejecuta una sola vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, responde `S` y vuelve a activar.

### 4.3 Instalar las librerías

```bash
python -m pip install --upgrade pip
pip install -r requirements-ci.txt
```

Instala Django, pytest y pytest-django.

### 4.4 Crear las bases de datos

```bash
python manage.py migrate
python manage.py poblar_db
```

- `migrate` crea las tablas y carga las categorías (Deporte, Canto, Danza, Artes Marciales, Literatura) y los motivos de edición más comunes.
- `poblar_db` agrega más categorías (Robótica, Tecnología) y motivos.

El sistema usa **dos bases SQLite**, que son archivos dentro de la carpeta del proyecto. No hace falta instalar ningún servidor de base de datos:

| Archivo | Qué guarda |
|---|---|
| `db.sqlite3` | Talleres, usuarios, inscripciones, historiales y avisos |
| `estudiantes_estatica.sqlite3` | Padrón de estudiantes de la universidad (el sistema solo lo consulta) |

### 4.5 Cargar los datos de demostración

Este paso crea el padrón de estudiantes de prueba y los usuarios para entrar al sistema. Abre la consola de Django:

```bash
python manage.py shell
```

Copia y pega **todo** este bloque y presiona Enter:

```python
from django.db import connections
from inscripciones.models import Usuario
padron = connections["estudiantes_db"].cursor()
padron.execute("CREATE TABLE IF NOT EXISTS estudiantes (ci VARCHAR(20) PRIMARY KEY, nombre VARCHAR(100), apellido VARCHAR(100), carrera VARCHAR(100))")
padron.executemany("INSERT OR IGNORE INTO estudiantes (ci, nombre, apellido, carrera) VALUES (%s, %s, %s, %s)", [("91870", "Lucía", "Rojas", "Sistemas"), ("92649", "Mateo", "Vargas", "Industrial"), ("94663", "Sofía", "Méndez", "Comercial"), ("95503", "Diego", "Suárez", "Sistemas"), ("96210", "Valeria", "Paz", "Diseño"), ("97001", "Camila", "Torres", "Sistemas")])
usuarios = [("OP01", "Olga", "Operadora", Usuario.Rol.OPERADOR), ("COORD01", "Carlos", "Coordinador", Usuario.Rol.COORDINADOR), ("COORD02", "Carla", "Coordinadora", Usuario.Rol.COORDINADOR), ("91870", "Lucía", "Rojas", Usuario.Rol.PARTICIPANTE), ("92649", "Mateo", "Vargas", Usuario.Rol.PARTICIPANTE), ("94663", "Sofía", "Méndez", Usuario.Rol.PARTICIPANTE), ("95503", "Diego", "Suárez", Usuario.Rol.PARTICIPANTE), ("96210", "Valeria", "Paz", Usuario.Rol.PARTICIPANTE)]
creados = [Usuario.objects.create_user(username=c, password="password123", codigo=c, first_name=n, last_name=a, rol=r) for c, n, a, r in usuarios if not Usuario.objects.filter(codigo=c).exists()]
print(len(creados), "usuarios creados")
```

Debe aparecer `8 usuarios creados`. Para salir de la consola escribe `exit()` y presiona Enter.

Se puede ejecutar de nuevo sin problema: no duplica nada (la segunda vez dice `0 usuarios creados`).

---

## 5. Usar el sistema

### 5.1 Encenderlo

```bash
python manage.py runserver
```

Abre en el navegador: **http://127.0.0.1:8000/entrar/**

Para apagarlo, vuelve a la ventana de comandos y presiona **Ctrl + C**.

### 5.2 Usuarios de demostración

Se entra con el **código** (no con el nombre). Todos usan la contraseña **`password123`**.

| Rol | Código | Al entrar va a… |
|---|---|---|
| Operador | `OP01` | Talleres |
| Coordinador | `COORD01` o `COORD02` | Crear taller |
| Participante | `91870`, `92649`, `94663`, `95503` o `96210` | Mis inscripciones |

El código `97001` (Camila Torres) está en el padrón pero no tiene cuenta: sirve para probar **Registrarse**.

### 5.3 Recorrido de prueba

1. Entra como **coordinador** (`COORD01`) y crea un taller con cupo 4, por ejemplo «Taller de Danza». Recibe el código `TAL-DAN-01` y queda *Pendiente de aprobación*.
2. Sal y entra como **operador** (`OP01`). En **Pendientes**, apruébalo.
3. Entra con cuatro participantes distintos (`91870`, `92649`, `94663`, `95503`) y en cada uno presiona **Solicitar inscripción**: quedan **Confirmados**. Con el quinto (`96210`) queda **En espera, posición 1**.
4. Entra con `91870`, ve a **Mis inscripciones** y **cancela**. Luego entra con `96210`: ya está **Confirmado** y en **Notificaciones** ve «Felicidades, se liberó una plaza…».
5. Como operador, en **Buscar inscripciones** escribe `TAL-DAN-01` para ver confirmados, espera y cancelados, y en **Talleres** presiona **Ver ocupación**.
6. En **Registrarse**, crea la cuenta de `97001` con una contraseña segura.

---

## 6. Ejecutar las pruebas

Con el entorno virtual activado:

```bash
python -m pytest -q                         # todas las pruebas
python -m pytest -q --ignore=tests/e2e      # sin las de navegador (más rápido)
```

El resultado debe terminar en `passed`, sin ningún `failed`.

**Las pruebas no tocan tus datos:** crean sus propias bases (`test_db.sqlite3` y `test_estudiantes.sqlite3`) y las borran al terminar.

| Tipo | Qué prueba | Dónde |
|---|---|---|
| Unitarias (77) | Cada regla directamente en los servicios | `tests/test_*.py` |
| Integración (21) | Pantallas completas con el cliente de pruebas de Django | `tests/test_*.py` |
| Punta a punta (5) | Recorridos reales en un navegador | `tests/e2e/` |

### Pruebas de punta a punta (opcional)

Abren un navegador de verdad y hacen clic como lo haría una persona. Para ejecutarlas, instala una sola vez:

```bash
pip install pytest-playwright
playwright install chromium
```

Si no están instaladas, esas pruebas se saltan solas y el resto se ejecuta igual.

---

## 7. Problemas comunes

| Mensaje o situación | Solución |
|---|---|
| `python` no se reconoce como comando | Reinstala Python marcando «Add python.exe to PATH» y abre una ventana nueva. |
| `No module named django` o `No module named pytest_django` | El entorno virtual no está activado (falta `(.venv)` al inicio de la línea). Actívalo (paso 4.2) e instala las librerías (paso 4.3). |
| `no such table: estudiantes` | Falta el padrón de estudiantes: haz el paso 4.5. |
| `no such table: …` (otra tabla) | Falta crear las tablas: ejecuta `python manage.py migrate`. |
| «El código o la contraseña no coinciden.» | Revisa que entras con el **código** (por ejemplo `OP01`) y la contraseña `password123`. Si no existe ningún usuario, haz el paso 4.5. |
| `Error: That port is already in use.` | El servidor ya está abierto en otra ventana. Ciérralo con Ctrl + C o usa otro puerto: `python manage.py runserver 8001`. |
| Quiero empezar con los datos limpios | Detén el servidor, borra `db.sqlite3` y `estudiantes_estatica.sqlite3`, y repite los pasos 4.4 y 4.5. |

---

## 8. Estructura del proyecto

```
config/                        configuración de Django (settings, urls)
inscripciones/
├── models.py                  tablas de datos
├── servicios/                 reglas de negocio
│   ├── operador.py            inscribir, lista de espera, cancelar, bloqueos, aprobar talleres
│   ├── coordinador.py         crear y editar talleres
│   ├── participante.py        cuenta, mis inscripciones, búsqueda por categoría
│   ├── sesion.py              iniciar sesión y pantalla de cada rol
│   ├── permisos.py            quién puede manejar cada taller
│   └── notificaciones.py      avisos en pantalla
├── views.py y urls.py         conectan cada pantalla con su regla
├── acceso.py                  qué roles pueden abrir cada pantalla
├── templates/inscripciones/   pantallas HTML
└── management/commands/       comando poblar_db
tests/                         pruebas unitarias, de integración y de punta a punta (e2e/)
version_inicial/               primera versión de la sesión 4 (terminal, sin base de datos)
docs/                          requisitos, modelos y diagramas por sesión
```

Cómo viaja un pedido: **pantalla (HTML) → `urls.py` → vista (`views.py`) → servicio (`servicios/`) → base de datos**, y la respuesta vuelve por el mismo camino.

## 9. Documentación

- Requisitos, respuestas del cliente y cumplimiento del encargo: [docs/sesion-06-requisitos.md](docs/sesion-06-requisitos.md)
- Historias, casos de uso, modelo, trazabilidad y diagramas de secuencia: [docs/sesion-07-modelos.md](docs/sesion-07-modelos.md)
- [Planilla de historias de usuario, casos de uso y cumplimiento (Excel)](https://docs.google.com/spreadsheets/d/1oyhV76VcpE20u-caiYUrRQok9BZoxhekKmNNaoeJrDQ/edit?usp=sharing)
- Primera iteración y backlog: [docs/sesion04.md](docs/sesion04.md)
- Arquitectura: [docs/sesion-12-arquitectura.md](docs/sesion-12-arquitectura.md)
