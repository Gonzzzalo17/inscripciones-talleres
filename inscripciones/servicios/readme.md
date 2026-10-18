# MODELO · Reglas de negocio (MVC)

Aquí van las clases y funciones con la lógica del sistema.

- Un archivo por área: `operador.py` (inscripción, espera, cancelación), `talleres.py` (talleres y cupos), …
- No usan HTML ni `request`: reciben datos y devuelven un resultado o lanzan un error.
- Los valores de las reglas (20 %, 3 horas) se importan desde `config.py`; no se escriben de nuevo.
- Cada archivo tiene sus pruebas en test