# P03 — Sistema de Inscripciones a Talleres y Listas de Espera

Este repositorio contiene la implementación del proyecto semestral para la administración de talleres, participantes y listas de espera, desarrollado en el marco de la asignatura de Ingeniería de Software.

## Descripción del Proyecto
El sistema permite a una organización gestionar la oferta de talleres con cupos limitados, automatizando el registro de inscripciones, el control de cupos máximos, la prevención de registros duplicados y la gestión de listas de espera.

## Integrantes
* Andrea Trujillo Antezana
* Gonzalo Andres Cárdenas Vargas
* Santiago Arauz Peña


## Estructura del proyecto (MVC sobre Django)

En Django, el **Modelo** es `models.py` (datos) más nuestra carpeta `servicios/` (reglas de negocio), la **Vista** son los HTML de `templates/` y el **Controlador** es `views.py` con `urls.py`. Django busca estos nombres, por eso no se renombran.

```
inscripciones/
├── models.py                  MODELO · tablas de datos
├── servicios/                 MODELO · reglas de negocio
│   ├── config.py              valores de las reglas del cliente (20 %, 3 horas)
│   └── operador.py            inscribir, lista de espera, cancelar y promover
├── views.py                   CONTROLADOR
└── templates/inscripciones/   VISTA · HTML
tests/                         pruebas pytest
version_inicial/               primera versión de la sesión 4 (terminal, sin base de datos)
docs/                          documentación por sesión, plan y diagramas
```

| Si vas a hacer… | Va en… | Responsable |
|---|---|---|
| Una pantalla (HTML) | `inscripciones/templates/inscripciones/` | Santiago |
| Una regla (cupo, espera, cancelación) | `inscripciones/servicios/` | Andrea y Santiago |
| Una tabla de la base de datos | `inscripciones/models.py` | Gonzalo |
| Conectar una pantalla con su regla | `inscripciones/views.py` y `urls.py` | Gonzalo |
| Una prueba | `tests/test_<archivo>.py` | Quien hizo la regla |

## Cómo ejecutar

```bash
pip install -r requirements.txt
python manage.py migrate
python -m pytest
python version_inicial/reglas_sesion04.py
python manage.py runserver
```