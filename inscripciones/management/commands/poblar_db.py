
from django.core.management.base import BaseCommand
from django.db import transaction

from inscripciones.models import Categoria, MotivoEdicion


class Command(BaseCommand):
    help = "Crea categorías y motivos iniciales para el MVP"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Iniciando la carga de datos...")

        # 1. Crear categorías sin duplicarlas.
        categorias_data = [
            "Robótica",
            "Danza",
            "Tecnología",
        ]

        for nombre in categorias_data:
            categoria = Categoria.objects.filter(
                nombre__iexact=nombre
            ).first()

            if categoria is None:
                categoria = Categoria.objects.create(nombre=nombre)
                accion = "creada"
            else:
                accion = "verificada"

            self.stdout.write(
                self.style.SUCCESS(
                    f"Categoría {accion}: {categoria.nombre}"
                )
            )

        # 2. Crear motivos de edición sin duplicarlos.
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

        self.stdout.write(
            self.style.SUCCESS(
                "\n¡Datos iniciales cargados exitosamente!"
            )
        )
