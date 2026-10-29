from django.core.exceptions import ValidationError

from inscripciones.models import Usuario


def puede_manejar_el_taller(usuario, taller):
    # El operador maneja todos los talleres; el coordinador solo los que él solicitó.
    if usuario.rol == Usuario.Rol.OPERADOR:
        return True
    if usuario.rol == Usuario.Rol.COORDINADOR:
        return taller.coordinador_id == usuario.pk
    return False


def verificar_que_pueda_manejar_el_taller(usuario, taller):
    if not puede_manejar_el_taller(usuario, taller):
        raise ValidationError("No puedes hacer cambios en un taller que no es tuyo.")


def verificar_que_sea_operador(usuario):
    if usuario.rol != Usuario.Rol.OPERADOR:
        raise ValidationError("Solo el operador puede hacer esta acción.")