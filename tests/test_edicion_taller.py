from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from inscripciones.models import Taller, TallerHistorial
from inscripciones.servicios.coordinador import Coordinador


class EdicionTallerAuditoriaTestCase(TestCase):
    def setUp(self):
        self.ahora = timezone.now()
        self.taller = Taller.objects.create(
            codigo="TAL-DAN-01",
            nombre="Taller de Danza",
            cupo_maximo=10,
            fecha_inicio=self.ahora + timedelta(days=2),
            fecha_fin=self.ahora + timedelta(days=2, hours=2)
        )

    def test_editar_taller_exitoso_registra_auditoria(self):
        nueva_fecha_inicio = self.ahora + timedelta(days=3)
        nueva_fecha_fin = self.ahora + timedelta(days=3, hours=2)

        # Ejecutar edición con motivo obligatorio
        Coordinador.editar_taller(
            taller_id=self.taller.pk,
            nombre="Taller de Danza Avanzada",
            cupo_maximo=15,
            fecha_inicio=nueva_fecha_inicio,
            fecha_fin=nueva_fecha_fin,
            motivo="Aumento de cupos por alta demanda estudiantil"
        )

        # Verificar que los datos del taller cambiaron
        self.taller.refresh_from_db()
        self.assertEqual(self.taller.nombre, "Taller de Danza Avanzada")
        self.assertEqual(self.taller.cupo_maximo, 15)

        # Verificar que se creó el registro de historial con los datos anteriores y el motivo
        historial = TallerHistorial.objects.filter(taller=self.taller).first()
        self.assertIsNotNone(historial)
        self.assertEqual(historial.motivo, "Aumento de cupos por alta demanda estudiantil")
        self.assertEqual(historial.nombre_anterior, "Taller de Danza")
        self.assertEqual(historial.cupo_maximo_anterior, 10)

    def test_editar_taller_sin_motivo_falla(self):
        # Intentar editar sin enviar motivo debe lanzar ValidationError
        with self.assertRaises(ValidationError) as ctx:
            Coordinador.editar_taller(
                taller_id=self.taller.pk,
                nombre="Taller Modificado",
                cupo_maximo=12,
                fecha_inicio=self.taller.fecha_inicio,
                fecha_fin=self.taller.fecha_fin,
                motivo=""  # Motivo vacío
            )
        self.assertIn("motivo", str(ctx.exception).lower())