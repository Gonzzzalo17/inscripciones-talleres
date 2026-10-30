from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from inscripciones.models import EstudianteEstatico, Inscripcion, Taller, Usuario
from inscripciones.servicios.operador import ALIAS_PADRON

class Participante:

    @staticmethod
    def buscar_talleres_por_categoria(categoria=None):
        # el participante ve los talleres a los que todavía se puede inscribir:
        # aprobados, no cancelados y que no empezaron. Si elige una categoría, solo ve esos
        # si no elige ninguna categoria, ve todos.
        disponibles = (Taller.objects
                       .filter(estado=Taller.Estado.APROBADO, cancelado=False,
                               fecha_inicio__gt=timezone.now())
                       .select_related("categoria")
                       .order_by("fecha_inicio"))
        if categoria is not None:
            disponibles = disponibles.filter(categoria=categoria)
        return disponibles

    @staticmethod
    def consultar_mis_inscripciones(participante):
        # todas las inscripciones del participante con su taller,
        # estado y posición en espera, de la más próxima a la más lejana.
        return (Inscripcion.objects
                .filter(participante=participante)
                .select_related("taller")
                .order_by("taller__fecha_inicio"))

    @staticmethod
    def registrar_cuenta(codigo, contrasena):
        codigo = (codigo or "").strip()

        if not codigo:
            raise ValidationError("Debes ingresar tu código universitario.")

        estudiante = (
            EstudianteEstatico.objects.using(ALIAS_PADRON)
            .only("codigo", "nombre", "apellido")
            .filter(codigo=codigo)
            .first()
        )

        if estudiante is None:
            raise ValidationError(
                f"El código {codigo} no figura en la lista de estudiantes de la universidad."
            )

        if Usuario.objects.filter(
                Q(codigo=codigo) | Q(username=codigo)
        ).exists():
            raise ValidationError(
                f"El código {codigo} ya tiene una cuenta. Ingresa con tu contraseña."
            )

        nuevo = Usuario(
            username=codigo,
            codigo=codigo,
            rol=Usuario.Rol.PARTICIPANTE,
            first_name=estudiante.nombre,
            last_name=estudiante.apellido
        )

        validate_password(contrasena, user=nuevo)
        nuevo.set_password(contrasena)
        nuevo.save()

        return nuevo