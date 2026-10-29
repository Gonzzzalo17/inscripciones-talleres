from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden

from .models import Usuario

# Atajos con los roles que pueden entrar a cada tipo de pantalla
TODOS = (Usuario.Rol.PARTICIPANTE, Usuario.Rol.COORDINADOR, Usuario.Rol.OPERADOR)


def solo_para(*roles):
    # HU-12: protege una vista para que solo la abran los roles indicados.
    # - Sin sesión iniciada: lo manda a la pantalla de entrar.
    # - Con sesión pero con otro rol: "403 Prohibido", aunque escriba la dirección a mano.
    def decorador(vista):
        @wraps(vista)
        def vista_protegida(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())  # va a LOGIN_URL
            if request.user.rol not in roles:
                return HttpResponseForbidden("No tienes permiso para ver esta página.")
            return vista(request, *args, **kwargs)
        return vista_protegida
    return decorador