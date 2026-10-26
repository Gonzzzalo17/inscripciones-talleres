from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inscripciones.models import Usuario, Taller, EstudianteEstatico


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos reales de prueba para el MVP'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando la carga de datos de prueba...")

        usuarios_data = [
            {
                'username': 'admin_coord',
                'email': 'coord@universidad.edu',
                'rol': Usuario.Rol.COORDINADOR,
                'codigo': 'COORD01',
            },
            {
                'username': 'operador1',
                'email': 'operador@universidad.edu',
                'rol': Usuario.Rol.OPERADOR,
                'codigo': 'OP01',
            },
            {
                'username': 'instructor_juan',
                'email': 'instructor@universidad.edu',
                'rol': Usuario.Rol.INSTRUCTOR,
                'codigo': 'INST01',
            },
            {
                'username': 'alejandro_parraga',
                'email': 'alejandro@universidad.edu',
                'rol': Usuario.Rol.PARTICIPANTE,
                'codigo': '91870',
            },
            {
                'username': 'oliver_chavez',
                'email': 'oliver@universidad.edu',
                'rol': Usuario.Rol.PARTICIPANTE,
                'codigo': '92649',
            },
            {
                'username': 'jeff_borda',
                'email': 'jeff@universidad.edu',
                'rol': Usuario.Rol.PARTICIPANTE,
                'codigo': '94663',
            },
            {
                'username': 'hugo_zuniga',
                'email': 'hugo@universidad.edu',
                'rol': Usuario.Rol.PARTICIPANTE,
                'codigo': '95503',
            },
            {
                'username': 'gonzalo_cardenas',
                'email': 'gonzalo@universidad.edu',
                'rol': Usuario.Rol.PARTICIPANTE,
                'codigo': '94102',
            },
        ]

        for u_data in usuarios_data:
            user, created = Usuario.objects.get_or_create(
                codigo=u_data['codigo'],
                defaults={
                    'username': u_data['username'],
                    'email': u_data['email'],
                    'rol': u_data['rol'],
                },
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✔ Usuario creado: {user.username} ({user.rol})")
                )
            else:
                self.stdout.write(f"ℹ Usuario ya existe: {user.username}")

        # 2. Cargar  5 estudiantes en la Base Estática
        estudiantes_data = [
            {
                'codigo': '91870',
                'nombre': 'Alejandro',
                'apellido': 'Parraga',
                'carrera': 'Ingenieria Comercial',
            },
            {
                'codigo': '92649',
                'nombre': 'Oliver',
                'apellido': 'Chavez',
                'carrera': 'Ingenieria Industrial',
            },
            {
                'codigo': '94663',
                'nombre': 'Jeff',
                'apellido': 'Borda',
                'carrera': 'Ingenieria Industrial',
            },
            {
                'codigo': '95503',
                'nombre': 'Hugo',
                'apellido': 'Zuñiga',
                'carrera': 'Ingenieria en Sistemas',
            },
            {
                'codigo': '94102',
                'nombre': 'Gonzalo',
                'apellido': 'Cardenas',
                'carrera': 'Ingenieria en Sistemas',
            },
        ]

        for est in estudiantes_data:
            obj, created = EstudianteEstatico.objects.using('estudiantes_db').get_or_create(
                codigo=est['codigo'],
                defaults={
                    'nombre': est['nombre'],
                    'apellido': est['apellido'],
                    'carrera': est['carrera'],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✔ Estudiante estático registrado: {est['nombre']} {est['apellido']}"
                    )
                )

        # 3. Crear Talleres de ejemplo
        ahora = timezone.now()
        talleres_data = [
            {
                'codigo': 'TAL-ROB-01',
                'nombre': 'Taller de Robotica Basica',
                'cupo_maximo': 20,
                'fecha_inicio': ahora + timedelta(days=2),
                'fecha_fin': ahora + timedelta(days=5),
            },
            {
                'codigo': 'TAL-DAN-01',
                'nombre': 'Taller de Danza Folklorica',
                'cupo_maximo': 15,
                'fecha_inicio': ahora + timedelta(days=7),
                'fecha_fin': ahora + timedelta(days=10),
            },
        ]

        for tal in talleres_data:
            taller, created = Taller.objects.get_or_create(
                codigo=tal['codigo'],
                defaults={
                    'nombre': tal['nombre'],
                    'cupo_maximo': tal['cupo_maximo'],
                    'fecha_inicio': tal['fecha_inicio'],
                    'fecha_fin': tal['fecha_fin'],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✔ Taller creado: {taller.nombre} ({taller.codigo})")
                )

        self.stdout.write(
            self.style.SUCCESS("\n¡Base de datos poblada exitosamente con los datos reales! 🚀")
        )