import uuid
class Taller:
    def __init__(self, nombreTaller : str, cupo_maximo : int, categoriaTaller : str, idTaller : int):
            if cupo_maximo <= 0:
                raise ValueError("El cupo debe ser mayor a cero.")

            self.id_taller = f"TAL-{uuid.uuid4().hex[:8].upper()}"
            self.nombreTaller = nombreTaller
            self.categoriaTaller = categoriaTaller
            self.cupo_maximo = cupo_maximo
            self.inscritos = []






