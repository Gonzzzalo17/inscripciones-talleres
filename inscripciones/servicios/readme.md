# MODELO · Reglas de negocio (MVC)

Aquí van las clases y funciones con la lógica del sistema.

- Un archivo por área: `operador.py` (inscripción, espera, cancelación), `talleres.py` (talleres y cupos), …
- No usan HTML ni `request`: reciben datos y devuelven un resultado o lanzan un error.
- Cada archivo tiene sus pruebas en test