from inscripciones.models import Inscripcion

class Participante:

    @staticmethod
    def consultar_mis_inscripciones(participante):
        # HU-08 / CU-11: todas las inscripciones del participante con su taller,
        # estado y posición en espera, de la más próxima a la más lejana.
        return (Inscripcion.objects
                .filter(participante=participante)
                .select_related("taller")
                .order_by("taller__fecha_inicio"))