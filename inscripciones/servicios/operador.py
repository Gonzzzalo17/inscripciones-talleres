import math
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from inscripciones.models import Inscripcion, HistorialCancelacion, EstudianteEstatico, Notificacion

porcentaje_lista_espera = 0.20
horas_limite_cancelacion = 3
mensaje_al_pasar_de_espera_a_confirmado = "Felicidades, se liberó una plaza y ya estás inscrito en el taller {taller}."
limite_maximo_cancelaciones = 3
horas_en_que_se_cuentan_cancelaciones = 72
horas_que_dura_el_bloqueo = 24
ALIAS_PADRON = 'estudiantes_db'


class Operador: #Andrea

    @staticmethod
    def capacidad_lista_de_espera(cupo_maximo):
        #20% redondeado hacia arriba
        return math.ceil(round(cupo_maximo * porcentaje_lista_espera,9))
    @classmethod
    def agregar_a_lista_de_espera(cls,participante, taller):
        capacidad=cls.capacidad_lista_de_espera(taller.cupo_maximo)
        en_espera = Inscripcion.objects.filter(taller=taller, estado='EN_ESPERA').count()
        if en_espera < capacidad:
            return Inscripcion.objects.create(
                participante=participante,
                taller=taller,
                estado='EN_ESPERA',
                posicion_espera=en_espera + 1
            )
        raise ValidationError("El taller y la lista de espera están llenos.")

    @staticmethod
    def promover_siguiente_en_espera(taller):
        primero_en_espera = (Inscripcion.objects
                   .filter(taller=taller, estado='EN_ESPERA')
                   .order_by('posicion_espera').first())
        if primero_en_espera is None:
            return None
        primero_en_espera.estado = 'CONFIRMADO'
        primero_en_espera.posicion_espera = None
        primero_en_espera.save()

        Notificacion.objects.create(
            participante=primero_en_espera.participante,
            taller=taller,
            mensaje=mensaje_al_pasar_de_espera_a_confirmado.format(taller=taller.nombre),
        )
        return primero_en_espera



    @staticmethod
    def actualizar_posiciones_lista_de_espera(taller):
        # Vuelve a numerar la espera desde 1, sin huecos (ej.: 2, 3 -> 1, 2)
        inscripciones_en_espera= (Inscripcion.objects.filter(taller=taller, estado='EN_ESPERA').order_by('posicion_espera'))
        for nueva_posicion, inscripcion in enumerate(inscripciones_en_espera, start=1):
            inscripcion.posicion_espera = nueva_posicion
            inscripcion.save()

    @classmethod
    @transaction.atomic
    def registrar_inscripcion(cls, participante, taller):
        cls.verificar_que_sea_estudiante_registrado(participante)
        cls.verificar_que_no_este_bloqueado(participante)
        cls.verificar_que_el_taller_no_haya_empezado(taller)
        cls.verificar_que_el_usuario_no_este_inscrito(participante, taller)
        cls.verificar_que_no_tenga_cruce_de_horario(participante, taller)

        confirmados = Inscripcion.objects.filter(taller=taller, estado='CONFIRMADO').count()
        if confirmados < taller.cupo_maximo:
            return Inscripcion.objects.create(participante=participante, taller=taller, estado='CONFIRMADO')

        return cls.agregar_a_lista_de_espera(participante, taller)

    @classmethod
    @transaction.atomic
    def cancelar_inscripcion(cls, participante, taller):
        plazo_limite = taller.fecha_inicio - timedelta(hours=horas_limite_cancelacion)
        if timezone.now() > plazo_limite:
            raise ValidationError("Ya pasó el tiempo límite para cancelar.")

        inscripcion = Inscripcion.objects.filter(
            participante=participante, taller=taller,
            estado__in=['CONFIRMADO', 'EN_ESPERA']
        ).first()
        if not inscripcion:
            raise ValidationError("No existe inscripción activa para cancelar.")

        era_confirmado = (inscripcion.estado == 'CONFIRMADO')
        inscripcion.estado = 'CANCELADO'
        inscripcion.posicion_espera = None
        inscripcion.save()

        HistorialCancelacion.objects.create(participante=participante, taller=taller)

        promovido = None
        if era_confirmado:
            promovido = cls.promover_siguiente_en_espera(taller)
        cls.actualizar_posiciones_lista_de_espera(taller)
        return inscripcion, promovido  # <- ahora devuelve ambos

    @classmethod
    @transaction.atomic
    def promover_hasta_llenar(cls, taller):
        """Confirma a la espera en orden hasta llenar el cupo. Devuelve los promovidos."""
        promovidos = []
        while True:
            confirmados = Inscripcion.objects.filter(
                taller=taller, estado='CONFIRMADO').count()
            if confirmados >= taller.cupo_maximo:
                break
            promovido = cls.promover_siguiente_en_espera(taller)
            if promovido is None:
                break
            promovidos.append(promovido)
        cls.actualizar_posiciones_lista_de_espera(taller)  # <- renumerar al final
        return promovidos

    @staticmethod
    def consultar_historial_cancelaciones(participante):
        return (HistorialCancelacion.objects
                .filter(participante=participante)
                .select_related("taller")
                .order_by("-fecha_cancelacion"))

    # --- MÉTODOS DE VALIDACIÓN ---
    @staticmethod
    def verificar_que_sea_estudiante_registrado(participante):
        """
        Consulta la BD estática para confirmar que el código del participante
        pertenezca a la lista de estudiantes autorizados.
        """

        ci = getattr(participante, 'codigo', None)
        if not ci or not EstudianteEstatico.objects.using(ALIAS_PADRON).filter(codigo=ci).exists():
            raise ValidationError("El usuario no figura en la lista estática de estudiantes autorizados.")
    @staticmethod
    def verificar_que_el_taller_no_haya_empezado(taller):
        if timezone.now() >= taller.fecha_inicio:
            raise ValidationError("El taller ya empezó.")

    @staticmethod
    def verificar_que_el_usuario_no_este_inscrito(participante, taller):
       if Inscripcion.objects.filter(
           participante=participante,taller=taller,
           estado__in=['CONFIRMADO', 'EN_ESPERA'],
       ).exists():
            raise ValidationError(f"El participante ya se encuentra registrado en el taller {taller.codigo}.")

    @staticmethod
    def verificar_que_no_tenga_cruce_de_horario(participante, taller):

        hay_cruce = Inscripcion.objects.filter(
            participante=participante,
            estado='CONFIRMADO',
            taller__fecha_inicio__lt=taller.fecha_fin,
            taller__fecha_fin__gt=taller.fecha_inicio
        ).exists()
        if hay_cruce:
            raise ValidationError("El participante ya tiene otro taller en este horario.")

    @staticmethod
    def calcular_fin_del_bloqueo(participante):
        # HU-09: la cancelación que supera el máximo dentro de 72 horas bloquea 24 horas desde ella.
        # Devuelve cuándo termina el último bloqueo, o None si nunca lo tuvo.
        fechas_de_cancelacion = list(HistorialCancelacion.objects
                                     .filter(participante=participante)
                                     .order_by("fecha_cancelacion")
                                     .values_list("fecha_cancelacion", flat=True))
        fin_del_bloqueo = None
        for fecha_cancelacion in fechas_de_cancelacion:
            inicio_del_periodo = fecha_cancelacion - timedelta(hours=horas_en_que_se_cuentan_cancelaciones)
            cancelaciones_en_el_periodo = [otra_fecha for otra_fecha in fechas_de_cancelacion
                                           if inicio_del_periodo < otra_fecha <= fecha_cancelacion]
            if len(cancelaciones_en_el_periodo) > limite_maximo_cancelaciones:
                fin_del_bloqueo = fecha_cancelacion + timedelta(hours=horas_que_dura_el_bloqueo)
        return fin_del_bloqueo

    @classmethod
    def verificar_que_no_este_bloqueado(cls, participante):
        fin_del_bloqueo = cls.calcular_fin_del_bloqueo(participante)
        sigue_bloqueado = fin_del_bloqueo is not None and timezone.now() < fin_del_bloqueo
        if sigue_bloqueado:
            raise ValidationError(f"Bloqueado hasta el {fin_del_bloqueo:%d/%m %H:%M} por cancelar más de "
                                  f"{limite_maximo_cancelaciones} veces en "
                                  f"{horas_en_que_se_cuentan_cancelaciones} horas.")