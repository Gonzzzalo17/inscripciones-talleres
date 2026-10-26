from inscripciones.models import Usuario


class Instructor:

    @staticmethod
    def listar_confirmados(taller):
        # participantes con plaza confirmada en el taller.
        # En orden alfabético por apellido, para pasar lista.
        return (Usuario.objects
                .filter(inscripciones__taller=taller, inscripciones__estado='CONFIRMADO')
                .order_by('last_name', 'first_name', 'username'))