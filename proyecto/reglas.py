import uuid


class Taller:
    def __init__(self, nombreTaller: str, cupo_maximo: int, categoriaTaller: str):
        if cupo_maximo <= 0:
            raise ValueError("El cupo debe ser mayor a cero.")

        self.id_taller = f"TAL-{uuid.uuid4().hex[:8].upper()}"
        self.nombreTaller = nombreTaller
        self.categoriaTaller = categoriaTaller
        self.cupo_maximo = cupo_maximo
        self.inscritos = []


def crear_taller(nombre: str, cupo_maximo: int, categoria: str) -> Taller:
    return Taller(nombreTaller=nombre, cupo_maximo=cupo_maximo, categoriaTaller=categoria)


def registrar_inscripcion(taller: Taller, ci_participante: str) -> dict:
    for registro in taller.inscritos:
        if registro["id_participante"] == ci_participante:
            raise ValueError(f"El participante con CI '{ci_participante}' ya está inscrito en este taller.")

    if len(taller.inscritos) < taller.cupo_maximo:
        nuevo_registro = {
            "id_participante": ci_participante,
            "estado": "CONFIRMADO",
            "mensaje": "Inscripción confirmada con éxito."
        }
        taller.inscritos.append(nuevo_registro)
        return nuevo_registro
    else:
        return {
            "id_participante": ci_participante,
            "estado": "EN_ESPERA",
            "mensaje": "Cupo lleno. El participante ingresó a la lista de espera."
        }