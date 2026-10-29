import re
import unicodedata

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from inscripciones.models import Taller, TallerHistorial, Usuario
from inscripciones.servicios.operador import Operador

PREFIJO = "TAL"
PALABRAS_VACIAS = {"taller", "talleres", "clase", "clases", "de", "del", "la", "el", "los", "las","como","dejar","ser"}
MAX_NOMBRE = 100
class Coordinador:
    @staticmethod
    def abreviatura_actividad(nombre):
        sin_tildes = "".join(
            c for c in unicodedata.normalize("NFD", nombre or "")
            if not unicodedata.combining(c))
        palabras = [p for p in re.findall(r"[A-Za-z]+", sin_tildes)
                    if p.lower() not in PALABRAS_VACIAS]
        if not palabras or len(palabras[0]) < 3:
            raise ValidationError(
                "El nombre del taller debe incluir una actividad de al menos 3 letras.")
        return palabras[0][:3].upper()

    @staticmethod
    def siguiente_codigo(abreviatura):
        base = f"{PREFIJO}-{abreviatura}-"
        patron = re.compile(rf"^{re.escape(base)}(\d+)$")
        numeros = [int(m.group(1))
                   for c in Taller.objects.filter(codigo__startswith=base)
                                          .values_list("codigo", flat=True)
                   if (m := patron.match(c))]
        return f"{base}{max(numeros, default=0) + 1:02d}"

    @classmethod
    def crear_taller(cls, nombre, cupo_maximo, fecha_inicio, fecha_fin,categoria,usuario_creador):
        if usuario_creador.rol not in (
                Usuario.Rol.COORDINADOR,
                Usuario.Rol.OPERADOR,
        ):
            raise ValidationError(
                "El usuario no tiene permisos para crear talleres."
            )

        if cupo_maximo < 4 or cupo_maximo > 40:
            raise ValidationError("El cupo máximo del taller debe estar entre 4 y 40 participantes.")
        if fecha_fin <= fecha_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la de inicio.")
        if categoria is None:
            raise ValidationError("La categoría del taller es obligatoria.")
        abreviatura = cls.abreviatura_actividad(nombre)

        if usuario_creador.rol == Usuario.Rol.COORDINADOR:
            estado_inicial = Taller.Estado.PENDIENTE
            coordinador =usuario_creador
        else:
            estado_inicial = Taller.Estado.APROBADO
            coordinador = None

        for _ in range(5):  # reintenta si otra petición tomó el mismo número
            try:
                with transaction.atomic():
                    return Taller.objects.create(
                        codigo=cls.siguiente_codigo(abreviatura),
                        nombre=nombre,
                        categoria=categoria,
                        coordinador=coordinador,
                        estado=estado_inicial,
                        cupo_maximo=cupo_maximo,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,)
            except IntegrityError:
                continue
        raise ValidationError("No se pudo generar un código único. Intenta de nuevo.")

    @staticmethod
    @transaction.atomic
    def editar_taller(taller_id, nombre, cupo_maximo, fecha_inicio, fecha_fin, motivo):
        motivo = (motivo or "").strip()
        if not motivo:
            raise ValidationError("Debe proporcionar un motivo obligatorio para la edición del taller.")

        try:
            taller = Taller.objects.select_for_update().get(pk=taller_id)
        except Taller.DoesNotExist:
            raise ValidationError("El taller no existe.")

        ahora = timezone.now()
        if taller.fecha_inicio <= ahora:
            raise ValidationError("El taller ya empezó y no se puede editar.")

        nombre = (nombre or "").strip()
        if not nombre:
            raise ValidationError("El nombre del taller no puede estar vacío.")
        if len(nombre) > MAX_NOMBRE:
            raise ValidationError(f"El nombre no puede superar {MAX_NOMBRE} caracteres.")
        if cupo_maximo <= 0:
            raise ValidationError("El cupo debe ser mayor que cero.")
        # se puede bajar el cupo, pero nunca por debajo de los que ya están
        # hasta la cantidad de confirmados (así nadie pierde su plaza ni pasa a la lista de espera).
        confirmados = taller.inscripciones.filter(estado="CONFIRMADO").count()
        if cupo_maximo < confirmados:
            raise ValidationError(
                f"No se puede bajar el cupo a {cupo_maximo}: ya hay {confirmados} participantes confirmados.")

        if fecha_inicio < ahora:
            raise ValidationError("La fecha de inicio no puede ser anterior a la actual.")
        if fecha_fin <= fecha_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la de inicio.")
        TallerHistorial.objects.create(
            taller=taller,
            motivo=motivo,
            codigo_anterior=taller.codigo,
            nombre_anterior=taller.nombre,
            cupo_maximo_anterior=taller.cupo_maximo,
            fecha_inicio_anterior=taller.fecha_inicio,
            fecha_fin_anterior=taller.fecha_fin,
        )
        taller.nombre = nombre
        taller.cupo_maximo = cupo_maximo
        taller.fecha_inicio = fecha_inicio
        taller.fecha_fin = fecha_fin
        taller.save(update_fields=["nombre", "cupo_maximo", "fecha_inicio", "fecha_fin"])
        Operador.promover_hasta_llenar(taller)
        return taller
