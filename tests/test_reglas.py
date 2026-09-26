import pytest

from proyecto.reglas import crear_taller, registrar_inscripcion


def cis_inscritos(taller):
    return [registro["id_participante"] for registro in taller.inscritos]


def test_acepta_inscripcion_cuando_hay_cupo():
    # Uso normal: taller con 3 cupos y nadie inscrito.
    taller = crear_taller("Python básico", 3, "Programación")

    resultado = registrar_inscripcion(taller, "1234567")

    assert resultado["estado"] == "CONFIRMADO"
    assert cis_inscritos(taller) == ["1234567"]


def test_acepta_la_ultima_plaza_disponible():
    # Límite: cupo 2, ya hay 1 inscrito; la segunda persona toma la última plaza.
    taller = crear_taller("Oratoria", 2, "Comunicación")
    registrar_inscripcion(taller, "1111111")

    resultado = registrar_inscripcion(taller, "2222222")

    assert resultado["estado"] == "CONFIRMADO"
    assert len(taller.inscritos) == 2


def test_envia_a_espera_cuando_el_taller_esta_lleno():
    # Límite superado: cupo 1 ya ocupado; la siguiente persona pasa a espera
    # y no debe superar la capacidad.
    taller = crear_taller("Fotografía", 1, "Arte")
    registrar_inscripcion(taller, "1111111")

    resultado = registrar_inscripcion(taller, "2222222")

    assert resultado["estado"] == "EN_ESPERA"
    assert len(taller.inscritos) == 1
    assert "2222222" not in cis_inscritos(taller)


def test_rechaza_inscripcion_duplicada_del_mismo_ci():
    # Rechazo: la misma persona (mismo CI) intenta inscribirse dos veces.
    taller = crear_taller("Excel", 3, "Oficina")
    registrar_inscripcion(taller, "1234567")

    with pytest.raises(ValueError):
        registrar_inscripcion(taller, "1234567")

    assert cis_inscritos(taller) == ["1234567"]


def test_rechaza_crear_taller_con_cupo_cero():
    # Rechazo: un taller sin cupos no tiene sentido.
    with pytest.raises(ValueError):
        crear_taller("Taller vacío", 0, "General")

