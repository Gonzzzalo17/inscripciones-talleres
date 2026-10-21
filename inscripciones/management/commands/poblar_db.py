from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inscripciones.models import Taller
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Pobla la base de datos principal con usuarios y talleres de prueba."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando la carga de datos de prueba..."))

        # 1. Crear Usuarios de prueba (Admin y Coordinador)
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@universidad.edu", "admin123")
            self.stdout.write("-> Superusuario 'admin' creado (pass: admin123).")

        if not User.objects.filter(username="coordinador").exists():
            User.objects.create_user("coordinador", "coord@universidad.edu", "coord123", is_staff=True)
            self.stdout.write("-> Usuario 'coordinador' creado (pass: coord123).")

        # 2. Crear Talleres de prueba en la base de datos principal ('default')
        ahora = timezone.now()
        talleres_data = [
            {
                "codigo": "TAL-DAN-01",
                "nombre": "Taller de Danza Folclórica",
                "cupo_maximo": 20,
                "fecha_inicio": ahora + timedelta(days=2),
                "fecha_fin": ahora + timedelta(days=15),
            },
            {
                "codigo": "TAL-ROB-01",
                "nombre": "Taller de Robótica Básica",
                "cupo_maximo": 15,
                "fecha_inicio": ahora + timedelta(days=5),
                "fecha_fin": ahora + timedelta(days=25),
            },
        ]

        creados_talleres = 0
        for tal in talleres_data:
            obj, created = Taller.objects.get_or_create(
                codigo=tal["codigo"],
                defaults={
                    "nombre": tal["nombre"],
                    "cupo_maximo": tal["cupo_maximo"],
                    "fecha_inicio": tal["fecha_inicio"],
                    "fecha_fin": tal["fecha_fin"],
                }
            )
            if created:
                creados_talleres += 1

        self.stdout.write(f"-> Talleres de prueba creados: {creados_talleres}")
        self.stdout.write(self.style.SUCCESS("¡Base de datos principal poblada exitosamente! 🚀"))