# VISTA (MVC) — HTML básico

Aquí van los HTML de las pantallas.

- Un archivo por pantalla: `talleres_lista.html`, `taller_form.html`, `mis_inscripciones.html`, …
- No se escribe lógica aquí: solo se muestran las variables que manda el controlador.
- Los enlaces usan `{% url 'nombre' %}`, nunca rutas escritas a mano.
- Django busca los HTML en esta carpeta por su nombre (`templates/`). No la renombren.