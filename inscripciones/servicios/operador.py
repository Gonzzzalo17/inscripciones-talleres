import math
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from inscripciones.models import Inscripcion, HistorialCancelacion, EstudianteEstatico, Notificacion, Taller, Categoria, MotivoEdicion
from inscripciones.servicios.permisos import verificar_que_pueda_manejar_el_taller, verificar_que_sea_operador
from inscripciones.servicios.notificaciones import notificar

porcentaje_lista_espera = 0.20
horas_limite_cancelacion = 3

mensaje_al_pasar_de_espera_a_confirmado = "Felicidades, se liberó una plaza y ya estás inscrito en el taller {taller}."
mensaje_inscripcion_confirmada = "Quedaste inscrito en el taller {taller}."
mensaje_inscripcion_en_espera = "Estás en la lista de espera del taller {taller}, en la posición {posicion}."
mensaje_inscripcion_cancelada = "Cancelaste tu inscripción en el taller {taller}."
mensaje_bloqueo = ("Quedaste bloqueado hasta el {fin:%d/%m %H:%M} por cancelar más de {limite} veces "
                   "en {horas} horas. Perdiste tus inscripciones y saliste de las listas de espera.")
mensaje_taller_aprobado = "Tu taller {taller} fue aprobado y ya recibe inscripciones."
mensaje_taller_rechazado = "Tu taller {taller} fue rechazado. Puedes corregirlo y volver a enviarlo."
mensaje_taller_cancelado = "El taller {taller} fue cancelado. Tu inscripción quedó anulada."
mensaje_edicion_rechazada = "El cambio que pediste para el taller {taller} no fue aprobado. El taller sigue con sus datos anteriores."
mensaje_taller_vuelve_a_sus_datos = "El taller {taller} sigue con su horario original: empieza el {inicio:%d/%m %H:%M}."

limite_maximo_cancelaciones = 3
horas_en_que_se_cuentan_cancelaciones = 72
horas_que_dura_el_bloqueo = 24
ALIAS_PADRON = 'estudiantes_db'


class Operador:

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

        notificar(primero_en_espera.participante, taller,
                  mensaje_al_pasar_de_espera_a_confirmado.format(taller=taller.nombre))
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
        # no pueden tomar la misma última plaza (el segundo espera a que termine el primero).
        taller = Taller.objects.select_for_update().get(pk=taller.pk)
        cls.verificar_que_sea_estudiante_registrado(participante)
        cls.verificar_que_no_este_bloqueado(participante)
        cls.verificar_que_el_taller_no_este_cancelado(taller)
        cls.verificar_que_el_taller_este_aprobado(taller)
        cls.verificar_que_el_taller_no_haya_empezado(taller)
        cls.verificar_que_el_usuario_no_este_inscrito(participante, taller)
        cls.verificar_que_no_tenga_cruce_de_horario(participante, taller)

        inscripcion_previa = Inscripcion.objects.filter(
            participante=participante, taller=taller, estado='CANCELADO'
        ).first()

        confirmados = Inscripcion.objects.filter(taller=taller, estado='CONFIRMADO').count()
        if confirmados < taller.cupo_maximo:
            nuevo_estado = 'CONFIRMADO'
            posicion = None
        else:
            # Validar si hay espacio en la lista de espera antes de reutilizar o crear
            capacidad = cls.capacidad_lista_de_espera(taller.cupo_maximo)
            en_espera_count = Inscripcion.objects.filter(taller=taller, estado='EN_ESPERA').count()
            if en_espera_count >= capacidad:
                raise ValidationError("El taller y la lista de espera están llenos.")
            nuevo_estado = 'EN_ESPERA'
            posicion = en_espera_count + 1

        if inscripcion_previa:
            # Reactivar la inscripción existente en lugar de crear una nueva
            inscripcion_previa.estado = nuevo_estado
            inscripcion_previa.posicion_espera = posicion
            inscripcion_previa.save()
            if nuevo_estado == 'EN_ESPERA':
                cls.actualizar_posiciones_lista_de_espera(taller)
            inscripcion = inscripcion_previa
        elif confirmados < taller.cupo_maximo:
            inscripcion = Inscripcion.objects.create(participante=participante, taller=taller, estado='CONFIRMADO')
        else:
            inscripcion = cls.agregar_a_lista_de_espera(participante, taller)

        cls.avisar_resultado_de_la_inscripcion(inscripcion)
        return inscripcion

    @staticmethod
    def avisar_resultado_de_la_inscripcion(inscripcion):
        # el participante recibe un aviso diciendo si quedó confirmado o en espera.
        inscripcion.refresh_from_db()
        if inscripcion.estado == 'CONFIRMADO':
            mensaje = mensaje_inscripcion_confirmada.format(taller=inscripcion.taller.nombre)
        else:
            mensaje = mensaje_inscripcion_en_espera.format(taller=inscripcion.taller.nombre,
                                                           posicion=inscripcion.posicion_espera)
        notificar(inscripcion.participante, inscripcion.taller, mensaje)

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
        notificar(participante, taller, mensaje_inscripcion_cancelada.format(taller=taller.nombre))

        promovido = None
        if era_confirmado:
            promovido = cls.promover_siguiente_en_espera(taller)
        cls.actualizar_posiciones_lista_de_espera(taller)

        # --- REGLA DE BANEO  ---
        fin_bloqueo = cls.calcular_fin_del_bloqueo(participante)
        if fin_bloqueo and fin_bloqueo > timezone.now():
            notificar(participante, taller, mensaje_bloqueo.format(
                fin=fin_bloqueo, limite=limite_maximo_cancelaciones,
                horas=horas_en_que_se_cuentan_cancelaciones))
            # 1. Si estaba en listas de espera, se le saca de todo el sistema
            # Solo talleres que todavía no empezaron: lo pasado o en curso no se toca.
            ahora = timezone.now()
            inscripciones_espera = Inscripcion.objects.filter(participante=participante, estado='EN_ESPERA',
                                                              taller__fecha_inicio__gt=ahora)
            for espera in inscripciones_espera:
                taller_espera = espera.taller
                espera.estado = 'CANCELADO'
                espera.posicion_espera = None
                espera.save()
                cls.actualizar_posiciones_lista_de_espera(taller_espera)

            # 2. Pierde todo lo anterior (sus talleres confirmados pasan a cancelados)
            inscripciones_confirmadas = Inscripcion.objects.filter(participante=participante, estado='CONFIRMADO',
                                                                   taller__fecha_inicio__gt=ahora)
            for conf in inscripciones_confirmadas:
                taller_conf = conf.taller
                conf.estado = 'CANCELADO'
                conf.save()
                # Liberar cupo y promover al siguiente en la fila de ese taller
                cls.promover_hasta_llenar(taller_conf)
        return inscripcion, promovido

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
        cls.actualizar_posiciones_lista_de_espera(taller)  # renumera la espera al terminar
        return promovidos

    @staticmethod
    def consultar_historial_cancelaciones(participante):
        return (HistorialCancelacion.objects
                .filter(participante=participante)
                .select_related("taller")
                .order_by("-fecha_cancelacion"))

    @staticmethod
    def buscar_inscripciones(texto):
        # el operador busca inscripciones escribiendo un código,
        # nombre o apellido del participante, o el código o nombre del taller.
        texto = (texto or "").strip()
        if not texto:
            return Inscripcion.objects.none()
        coincide = (Q(participante__codigo__icontains=texto)
                    | Q(participante__username__icontains=texto)
                    | Q(participante__first_name__icontains=texto)
                    | Q(participante__last_name__icontains=texto)
                    | Q(taller__codigo__icontains=texto)
                    | Q(taller__nombre__icontains=texto))
        return (Inscripcion.objects.filter(coincide)
                .select_related("participante", "taller")
                .order_by("taller__fecha_inicio", "participante__last_name"))

    @staticmethod
    @transaction.atomic
    def aprobar_taller(operador, taller):
        # el operador acepta un taller que pidió un coordinador.
        return Operador.decidir_solicitud_de_taller(operador, taller, Taller.Estado.APROBADO)

    @staticmethod
    @transaction.atomic
    def rechazar_taller(operador, taller):
        # el operador rechaza el taller; el coordinador lo puede corregir y volver a enviar.
        return Operador.decidir_solicitud_de_taller(operador, taller, Taller.Estado.RECHAZADO)

    @staticmethod
    def decidir_solicitud_de_taller(operador, taller, nuevo_estado):
        verificar_que_sea_operador(operador)
        taller = Taller.objects.select_for_update().get(pk=taller.pk)
        if taller.cancelado:
            raise ValidationError("El taller fue cancelado: ya no se puede aceptar ni rechazar.")
        if taller.estado != Taller.Estado.PENDIENTE:
            raise ValidationError("Solo se puede aceptar o rechazar un taller que está pendiente.")

        mensaje = mensaje_taller_aprobado if nuevo_estado == Taller.Estado.APROBADO else mensaje_taller_rechazado
        tiene_inscritos = taller.inscripciones.filter(estado__in=['CONFIRMADO', 'EN_ESPERA']).exists()
        if nuevo_estado == Taller.Estado.RECHAZADO and tiene_inscritos:
            # Solo un taller ya aprobado puede tener inscritos: lo que se rechaza es la EDICIÓN que hizo
            # el coordinador. El taller vuelve a sus datos anteriores y sigue aprobado; nadie pierde su plaza.
            Operador.volver_a_los_datos_anteriores(taller)
            nuevo_estado = Taller.Estado.APROBADO
            mensaje = mensaje_edicion_rechazada

        taller.estado = nuevo_estado
        taller.save(update_fields=["estado"])
        if taller.coordinador is not None:
            notificar(taller.coordinador, taller, mensaje.format(taller=taller.nombre))
        return taller

    @staticmethod
    def volver_a_los_datos_anteriores(taller):
        # Toma los datos que había antes de la última edición (los guarda TallerHistorial al editar).
        anterior = taller.historial_cambios.order_by('-fecha_modificacion', '-id').first()
        if anterior is None:
            return
        confirmados = taller.inscripciones.filter(estado='CONFIRMADO').count()
        taller.fecha_inicio = anterior.fecha_inicio_anterior
        taller.fecha_fin = anterior.fecha_fin_anterior
        # Si con la edición subió el cupo y entraron personas de la espera, el cupo no baja de los confirmados.
        taller.cupo_maximo = max(anterior.cupo_maximo_anterior, confirmados)
        taller.save(update_fields=["fecha_inicio", "fecha_fin", "cupo_maximo"])
        Operador.promover_hasta_llenar(taller)
        for inscripcion in taller.inscripciones.filter(estado__in=['CONFIRMADO', 'EN_ESPERA']).select_related("participante"):
            notificar(inscripcion.participante, taller,
                      mensaje_taller_vuelve_a_sus_datos.format(taller=taller.nombre, inicio=taller.fecha_inicio))

    @staticmethod
    @transaction.atomic
    def cancelar_taller(usuario, taller):
        # el operador cancela cualquier taller y el coordinador solo los suyos.
        # Todos los inscritos y los de la lista de espera quedan cancelados y
        # reciben un aviso. No se guarda en HistorialCancelacion: no cuenta para el bloqueo.
        verificar_que_pueda_manejar_el_taller(usuario, taller)
        taller = Taller.objects.select_for_update().get(pk=taller.pk)
        if taller.cancelado:
            raise ValidationError("El taller ya estaba cancelado.")
        if taller.fecha_inicio <= timezone.now():
            raise ValidationError("El taller ya empezó y no se puede cancelar.")

        afectadas = taller.inscripciones.filter(estado__in=['CONFIRMADO', 'EN_ESPERA'])
        for inscripcion in afectadas.select_related("participante"):
            notificar(inscripcion.participante, taller, mensaje_taller_cancelado.format(taller=taller.nombre))
        afectadas.update(estado='CANCELADO', posicion_espera=None)

        taller.cancelado = True
        taller.save(update_fields=["cancelado"])
        return taller

    @staticmethod
    @transaction.atomic
    def levantar_bloqueo(operador,participante):
        """
        Levanta anticipadamente el bloqueo eliminando únicamente
        las cancelaciones de las últimas 72 horas.
        Conserva el historial anterior.
        """
        verificar_que_sea_operador(operador)

        limite = timezone.now() - timedelta(
            hours=horas_en_que_se_cuentan_cancelaciones
        )

        HistorialCancelacion.objects.filter(
            participante=participante,
            fecha_cancelacion__gte=limite,
        ).delete()

        return participante

    @staticmethod
    def agregar_categoria(usuario, nombre):
        verificar_que_sea_operador(usuario)

        nombre = nombre.strip()

        if not nombre:
            raise ValidationError(
                "El nombre de la categoría no puede estar vacío."
            )

        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            raise ValidationError(
                "Ya existe una categoría con ese nombre."
            )

        return Categoria.objects.create(nombre=nombre)

    @staticmethod
    def agregar_motivo_edicion(usuario, descripcion):
        verificar_que_sea_operador(usuario)

        descripcion = descripcion.strip()

        if not descripcion:
            raise ValidationError(
                "La descripción del motivo no puede estar vacía."
            )

        if MotivoEdicion.objects.filter(
            descripcion__iexact=descripcion
        ).exists():
            raise ValidationError(
                "Ya existe un motivo con esa descripción."
            )

        return MotivoEdicion.objects.create(descripcion=descripcion)
    # --- MÉTODOS DE VALIDACIÓN ---

    @staticmethod
    def verificar_que_el_taller_no_este_cancelado(taller):
        if taller.cancelado:
            raise ValidationError("El taller fue cancelado y ya no recibe inscripciones.")

    @staticmethod
    def verificar_que_el_taller_este_aprobado(taller):
        if taller.estado != Taller.Estado.APROBADO:
            raise ValidationError("El taller todavía no fue aprobado por el operador.")

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
            estado__in=['CONFIRMADO', 'EN_ESPERA'],
            taller__fecha_inicio__lt=taller.fecha_fin,
            taller__fecha_fin__gt=taller.fecha_inicio
        ).exists()
        if hay_cruce:
            raise ValidationError("El participante ya tiene otro taller en este horario.")

    @staticmethod
    def calcular_fin_del_bloqueo(participante):
        # la cancelación que supera el máximo dentro de 72 horas bloquea 24 horas desde ella.
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

    @staticmethod
    def calcular_ocupacion(taller):
        ocupadas = taller.inscripciones.filter(estado='CONFIRMADO').count()
        en_espera = taller.inscripciones.filter(estado='EN_ESPERA').count()
        maximo_espera = Operador.capacidad_lista_de_espera(taller.cupo_maximo)
        libres = max(0, taller.cupo_maximo - ocupadas)
        return {
            'ocupadas': ocupadas,
            'libres': libres,
            'en_espera': en_espera,
            'maximo_espera': maximo_espera,
        }