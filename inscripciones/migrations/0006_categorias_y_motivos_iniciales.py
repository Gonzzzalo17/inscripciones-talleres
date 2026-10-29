from django.db import migrations

CATEGORIAS_INICIALES = ["Deporte", "Canto", "Danza", "Artes Marciales", "Literatura"]
MOTIVOS_INICIALES = [
    "Cambio de fecha u horario porque el ambiente no está disponible",
    "Aumento de cupo por alta demanda de inscripciones",
    "Reducción de plazas libres por la capacidad del ambiente",
    "Reprogramación porque el coordinador del taller no puede asistir",
]


def cargar_valores_iniciales(apps, schema_editor):
    Categoria = apps.get_model("inscripciones", "Categoria")
    MotivoEdicion = apps.get_model("inscripciones", "MotivoEdicion")
    for nombre in CATEGORIAS_INICIALES:
        Categoria.objects.get_or_create(nombre=nombre)
    for descripcion in MOTIVOS_INICIALES:
        MotivoEdicion.objects.get_or_create(descripcion=descripcion)


class Migration(migrations.Migration):

    dependencies = [
        ("inscripciones", "0005_roles_categorias_y_estado_del_taller"),
    ]

    operations = [
        migrations.RunPython(cargar_valores_iniciales, migrations.RunPython.noop),
    ]