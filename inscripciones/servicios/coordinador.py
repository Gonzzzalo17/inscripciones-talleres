import re
import unicodedata

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from inscripciones.models import Taller

PREFIJO = "TAL"
PALABRAS_VACIAS = {"taller", "talleres", "clase", "clases", "de", "del", "la", "el", "los", "las"}

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
    def crear_taller(cls, nombre, cupo_maximo, fecha_inicio, fecha_fin):
        if cupo_maximo <= 0:
            raise ValidationError("El cupo debe ser mayor que cero.")
        if fecha_fin <= fecha_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la de inicio.")
        abreviatura = cls.abreviatura_actividad(nombre)

        for _ in range(5):  # reintenta si otra petición tomó el mismo número
            try:
                with transaction.atomic():
                    return Taller.objects.create(
                        codigo=cls.siguiente_codigo(abreviatura), nombre=nombre,
                        cupo_maximo=cupo_maximo,
                        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
            except IntegrityError:
                continue
        raise ValidationError("No se pudo generar un código único. Intenta de nuevo.")
