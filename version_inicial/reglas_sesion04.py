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
# Ejemplo de prueba ejecutable
if __name__ == "__main__":
    taller = crear_taller(nombre="Robótica Avanzada", cupo_maximo=2, categoria="Tecnología")
    print(f"Taller creado: {taller.nombreTaller} (ID: {taller.id_taller})")
    print(f"Cupo máximo: {taller.cupo_maximo}\n")

    # Inscripciones válidas
    print(registrar_inscripcion(taller, ci_participante="1234567"))
    print(registrar_inscripcion(taller, ci_participante="8901234"))

    # Intento de duplicado (mismo CI)
    try:
        registrar_inscripcion(taller, ci_participante="1234567")
    except ValueError as e:
        print(f"Error esperado por duplicado: {e}")

    # Cupo lleno -> Pasa a lista de espera
    print(registrar_inscripcion(taller, ci_participante="5554433"))

    print(f"\nInscritos confirmados en memoria: {len(taller.inscritos)}")