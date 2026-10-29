from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.utils import timezone

from inscripciones.models import (
    Usuario,
    Taller,
    EstudianteEstatico,
    Categoria,
    MotivoEdicion,
)


class Command(BaseCommand):
    help = "Pobla la base de datos con datos de prueba para el MVP"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Iniciando la carga de datos de prueba...")

        # 1. Crear o actualizar usuarios de demostración.
        usuarios_data = [
            {
                "username": "admin_coord",
                "email": "coord@universidad.edu",
                "rol": Usuario.Rol.COORDINADOR,
                "codigo": "COORD01",
            },
            {
                "username": "coordinador_juan",
                "email": "juan@universidad.edu",
                "rol": Usuario.Rol.COORDINADOR,
                "codigo": "COORD02",
            },
            {
                "username": "operador1",
                "email": "operador@universidad.edu",
                "rol": Usuario.Rol.OPERADOR,
                "codigo": "OP01",
            },
            {
                "username": "alejandro_parraga",
                "email": "alejandro@universidad.edu",
                "rol": Usuario.Rol.PARTICIPANTE,
                "codigo": "91870",
            },
            {
                "username": "oliver_chavez",
                "email": "oliver@universidad.edu",
                "rol": Usuario.Rol.PARTICIPANTE,
                "codigo": "92649",
            },
            {
                "username": "jeff_borda",
                "email": "jeff@universidad.edu",
                "rol": Usuario.Rol.PARTICIPANTE,
                "codigo": "94663",
            },
            {
                "username": "hugo_zuniga",
                "email": "hugo@universidad.edu",
                "rol": Usuario.Rol.PARTICIPANTE,
                "codigo": "95503",
            },
            {
                "username": "gonzalo_cardenas",
                "email": "gonzalo@universidad.edu",
                "rol": Usuario.Rol.PARTICIPANTE,
                "codigo": "94102",
            },
        ]

        usuarios = {}

        for datos in usuarios_data:
            usuario = Usuario.objects.filter(
                username=datos["username"]
            ).first()

            if usuario is None:
                usuario_con_codigo = Usuario.objects.filter(
                    codigo=datos["codigo"]
                ).first()

                if usuario_con_codigo is not None:
                    raise CommandError(
                        "No se puede crear el usuario "
                        f"'{datos['username']}': el código "
                        f"'{datos['codigo']}' ya pertenece a "
                        f"'{usuario_con_codigo.username}'."
                    )

                usuario = Usuario(**datos)
                usuario.set_password("password123")
                creado = True
            else:
                creado = False

                # Verificar que el código no pertenezca a otra cuenta.
                conflicto = Usuario.objects.filter(
                    codigo=datos["codigo"]
                ).exclude(pk=usuario.pk).first()

                if conflicto is not None:
                    raise CommandError(
                        f"El código '{datos['codigo']}' de "
                        f"'{datos['username']}' ya pertenece a "
                        f"'{conflicto.username}'."
                    )

                for campo, valor in datos.items():
                    setattr(usuario, campo, valor)

            try:
                usuario.save()
            except IntegrityError as error:
                raise CommandError(
                    "No se pudo guardar el usuario "
                    f"'{datos['username']}': {error}"
                ) from error

            usuarios[usuario.username] = usuario

            accion = "creado" if creado else "actualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario {accion}: {usuario.username} "
                    f"({usuario.rol})"
                )
            )

        # 2. Crear categorías de demostración sin duplicarlas.
        categorias_data = [
            "Robótica",
            "Danza",
            "Tecnología",
        ]

        categorias = {}

        for nombre in categorias_data:
            categoria = Categoria.objects.filter(
                nombre__iexact=nombre
            ).first()

            if categoria is None:
                categoria = Categoria.objects.create(nombre=nombre)
                accion = "creada"
            else:
                accion = "verificada"

            categorias[nombre] = categoria

            self.stdout.write(
                self.style.SUCCESS(
                    f"Categoría {accion}: {categoria.nombre}"
                )
            )

        # 3. Crear motivos de edición sin duplicarlos.
        motivos_data = [
            "Cambio de horario",
            "Ajuste de fechas",
            "Ampliación de cupos",
        ]

        for descripcion in motivos_data:
            motivo = MotivoEdicion.objects.filter(
                descripcion__iexact=descripcion
            ).first()

            if motivo is None:
                MotivoEdicion.objects.create(
                    descripcion=descripcion
                )
                accion = "creado"
            else:
                accion = "verificado"

            self.stdout.write(
                self.style.SUCCESS(
                    f"Motivo {accion}: {descripcion}"
                )
            )

        # 4. Cargar estudiantes en la base de datos estática.
        estudiantes_data = [
            {
                "codigo": "91870",
                "nombre": "Alejandro",
                "apellido": "Parraga",
                "carrera": "Ingenieria Comercial",
            },
            {
                "codigo": "92649",
                "nombre": "Oliver",
                "apellido": "Chavez",
                "carrera": "Ingenieria Industrial",
            },
            {
                "codigo": "94663",
                "nombre": "Jeff",
                "apellido": "Borda",
                "carrera": "Ingenieria Industrial",
            },
            {
                "codigo": "95503",
                "nombre": "Hugo",
                "apellido": "Zuñiga",
                "carrera": "Ingenieria en Sistemas",
            },
            {
                "codigo": "94102",
                "nombre": "Gonzalo",
                "apellido": "Cardenas",
                "carrera": "Ingenieria en Sistemas",
            },
        ]

        for estudiante in estudiantes_data:
            EstudianteEstatico.objects.using(
                "estudiantes_db"
            ).update_or_create(
                codigo=estudiante["codigo"],
                defaults={
                    "nombre": estudiante["nombre"],
                    "apellido": estudiante["apellido"],
                    "carrera": estudiante["carrera"],
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Estudiantes estáticos verificados."
            )
        )

        # 5. Crear o actualizar talleres de demostración.
        ahora = timezone.now()

        talleres_data = [
            {
                "codigo": "TAL-ROB-01",
                "nombre": "Taller de Robotica Basica",
                "categoria": categorias["Robótica"],
                "coordinador": usuarios["admin_coord"],
                "estado": Taller.Estado.APROBADO,
                "cupo_maximo": 20,
                "fecha_inicio": ahora + timedelta(days=2),
                "fecha_fin": ahora + timedelta(days=5),
            },
            {
                "codigo": "TAL-DAN-01",
                "nombre": "Taller de Danza Folklorica",
                "categoria": categorias["Danza"],
                "coordinador": usuarios["coordinador_juan"],
                "estado": Taller.Estado.PENDIENTE,
                "cupo_maximo": 15,
                "fecha_inicio": ahora + timedelta(days=7),
                "fecha_fin": ahora + timedelta(days=10),
            },
            {
                "codigo": "TAL-TEC-01",
                "nombre": "Taller de Tecnologia Creativa",
                "categoria": categorias["Tecnología"],
                "coordinador": usuarios["admin_coord"],
                "estado": Taller.Estado.RECHAZADO,
                "cupo_maximo": 12,
                "fecha_inicio": ahora + timedelta(days=12),
                "fecha_fin": ahora + timedelta(days=14),
            },
        ]

        for datos in talleres_data:
            datos = datos.copy()
            codigo = datos.pop("codigo")

            taller, creado = Taller.objects.update_or_create(
                codigo=codigo,
                defaults=datos,
            )

            accion = "creado" if creado else "actualizado"

            self.stdout.write(
                self.style.SUCCESS(
                    f"Taller {accion}: {taller.nombre} "
                    f"({taller.estado})"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "\n¡Base de datos poblada exitosamente!"
            )
        )
