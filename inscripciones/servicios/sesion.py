from django.core.exceptions import ValidationError
from inscripciones.models import Usuario

# HU-12 / CU-20: pantalla a la que va cada rol después de iniciar sesión
# (son los nombres de las rutas en urls.py)
PANTALLA_POR_ROL = {
    Usuario.Rol.PARTICIPANTE: 'mis_inscripciones',
    Usuario.Rol.COORDINADOR: 'crear_taller',
    Usuario.Rol.OPERADOR: 'lista_talleres',
}

MENSAJE_DATOS_INCORRECTOS = "El código o la contraseña no coinciden."


class Sesion:

    @staticmethod
    def iniciar_sesion(codigo, contrasena):
        # Busca la cuenta por su código y comprueba la contraseña.
        # Devuelve el usuario y el nombre de la pantalla a la que debe ir.
        codigo = (codigo or "").strip()
        usuario = Usuario.objects.filter(codigo=codigo).first()
        # Mismo mensaje si el código no existe o si la contraseña está mal:
        # así nadie puede averiguar qué códigos tienen cuenta.
        if usuario is None or not usuario.is_active or not usuario.check_password(contrasena or ""):
            raise ValidationError(MENSAJE_DATOS_INCORRECTOS)

        return usuario, Sesion.pantalla_de_inicio(usuario)

    @staticmethod
    def pantalla_de_inicio(usuario):
        # Decide a qué pantalla va cada rol.
        return PANTALLA_POR_ROL.get(usuario.rol, 'lista_talleres')