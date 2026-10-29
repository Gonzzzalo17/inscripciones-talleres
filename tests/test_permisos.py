from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from inscripciones.models import Taller, Usuario
from inscripciones.servicios.permisos import verificar_que_pueda_manejar_el_taller, verificar_que_sea_operador

# quién puede manejar un taller.
pytestmark = pytest.mark.django_db


def persona(nombre, rol):
    return Usuario.objects.create(username=nombre, rol=rol)


def taller_de(coordinador):
    inicio = timezone.now() + timedelta(days=1)
    return Taller.objects.create(codigo=f"TAL-PER-{Taller.objects.count() + 1:02d}", nombre="Taller",
                                 cupo_maximo=10, fecha_inicio=inicio, fecha_fin=inicio + timedelta(hours=2),
                                 coordinador=coordinador)


def test_el_operador_puede_manejar_cualquier_taller():
    operador = persona("operador", Usuario.Rol.OPERADOR)
    taller_ajeno = taller_de(persona("coordinadora", Usuario.Rol.COORDINADOR))

    verificar_que_pueda_manejar_el_taller(operador, taller_ajeno)    # no lanza error
    verificar_que_sea_operador(operador)


def test_el_coordinador_solo_puede_manejar_sus_talleres():
    ana = persona("ana", Usuario.Rol.COORDINADOR)
    luis = persona("luis", Usuario.Rol.COORDINADOR)

    verificar_que_pueda_manejar_el_taller(ana, taller_de(ana))       # el suyo: sí
    with pytest.raises(ValidationError):
        verificar_que_pueda_manejar_el_taller(ana, taller_de(luis))  # el de otro: no
    with pytest.raises(ValidationError):
        verificar_que_sea_operador(ana)


def test_el_participante_no_puede_manejar_talleres():
    participante = persona("participante", Usuario.Rol.PARTICIPANTE)

    with pytest.raises(ValidationError):
        verificar_que_pueda_manejar_el_taller(participante, taller_de(None))