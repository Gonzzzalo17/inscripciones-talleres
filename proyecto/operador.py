from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from inscripciones.models import Inscripcion, HistorialCancelacion

porcentaje_lista_espera = 0.20
horas_limite_cancelacion = 3


class Operador:

    @staticmethod
    def agregar_a_lista_de_espera(participante, taller):
        """Asigna un lugar en la lista de espera si hay espacio (20% del cupo total)."""
        cupo_espera = int(taller.cupo_maximo * porcentaje_lista_espera)
        en_espera = Inscripcion.objects.filter(taller=taller, estado='EN_ESPERA').count()
        if en_espera < cupo_espera:
            return Inscripcion.objects.create(
                participante=participante,
                taller=taller,
                estado='EN_ESPERA',
                posicion_espera=en_espera + 1
            )
        raise ValidationError("El taller y la lista de espera están llenos.")

    @staticmethod
    def promover_siguiente_en_espera(taller):
        """Promueve al primer participante en espera a CONFIRMADO y reordena las posiciones."""
        primero = Inscripcion.objects.filter(taller=taller, estado='EN_ESPERA').order_by('posicion_espera').first()
        if primero:
            primero.estado = 'CONFIRMADO'
            primero.posicion_espera = None
            primero.save()

            restantes = Inscripcion.objects.filter(taller=taller, estado='EN_ESPERA').order_by('posicion_espera')
            for posicion, item in enumerate(restantes, start=1):
                item.posicion_espera = posicion
                item.save()

    @classmethod
    def registrar_inscripcion(cls, participante, taller):
        cls.verificar_que_el_taller_no_haya_empezado(taller)
        cls.verificar_que_el_usuario_no_este_inscrito(participante, taller)
        cls.verificar_que_no_tenga_cruce_de_horario(participante, taller)

        confirmados = Inscripcion.objects.filter(taller=taller, estado='CONFIRMADO').count()
        if confirmados < taller.cupo_maximo:
            return Inscripcion.objects.create(participante=participante, taller=taller, estado='CONFIRMADO')

        return cls.agregar_a_lista_de_espera(participante, taller)

    @classmethod
    def cancelar_inscripcion(cls, participante, taller):
        plazo_limite = taller.fecha_inicio - timedelta(hours=horas_limite_cancelacion)
        if timezone.now() > plazo_limite:
            raise ValidationError("Ya pasó el tiempo límite para cancelar.")

        inscripcion = Inscripcion.objects.filter(
            participante=participante,
            taller=taller,
            estado__in=['CONFIRMADO', 'EN_ESPERA']
        ).first()

        if not inscripcion:
            raise ValidationError("No existe inscripción activa para cancelar.")

        era_confirmado = (inscripcion.estado == 'CONFIRMADO')
        inscripcion.estado = 'CANCELADO'
        inscripcion.posicion_espera = None
        inscripcion.save()

        HistorialCancelacion.objects.create(participante=participante, taller=taller)

        if era_confirmado:
            cls.promover_siguiente_en_espera(taller)

        return inscripcion