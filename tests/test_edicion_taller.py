
from datetime import timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from inscripciones.models import (
    Taller,
    TallerHistorial,
    MotivoEdicion,
    Usuario,
)
from inscripciones.servicios.coordinador import Coordinador


class EdicionTallerAuditoriaTestCase(TestCase):
    def setUp(self):
        ahora = timezone.now()

        self.usuario = Usuario.objects.create_user(
            username="coordinador_edicion",
            password="test123",
            rol=Usuario.Rol.COORDINADOR,
        )

        self.motivo = MotivoEdicion.objects.create(
            descripcion="Aumento de cupos por alta demanda"
        )

        self.taller = Taller.objects.create(
            codigo="TAL-DAN-01",
            nombre="Taller de Danza",
            coordinador=self.usuario,
            estado=Taller.Estado.APROBADO,
            cupo_maximo=10,
            fecha_inicio=ahora + timedelta(days=2),
            fecha_fin=ahora + timedelta(days=2, hours=2),
        )

    def test_editar_taller_exitoso_registra_auditoria(self):
        nueva_fecha_inicio = timezone.now() + timedelta(days=3)
        nueva_fecha_fin = nueva_fecha_inicio + timedelta(hours=2)

        Coordinador.editar_taller(
            taller_id=self.taller.pk,
            cupo_maximo=15,
            fecha_inicio=nueva_fecha_inicio,
            fecha_fin=nueva_fecha_fin,
            motivo=self.motivo,
            usuario=self.usuario,
        )

        self.taller.refresh_from_db()

        self.assertEqual(self.taller.nombre, "Taller de Danza")
        self.assertEqual(self.taller.cupo_maximo, 15)
        self.assertEqual(self.taller.estado, Taller.Estado.PENDIENTE)

        historial = TallerHistorial.objects.get(taller=self.taller)
        self.assertEqual(historial.motivo, self.motivo.descripcion)
        self.assertEqual(historial.nombre_anterior, "Taller de Danza")
        self.assertEqual(historial.cupo_maximo_anterior, 10)

    def test_editar_taller_sin_motivo_falla(self):
        with self.assertRaises(ValidationError):
            Coordinador.editar_taller(
                taller_id=self.taller.pk,
                cupo_maximo=12,
                fecha_inicio=self.taller.fecha_inicio,
                fecha_fin=self.taller.fecha_fin,
                motivo="",
                usuario=self.usuario,
            )

    def test_no_permite_editar_taller_que_ya_inicio(self):
        self.taller.fecha_inicio = timezone.now() - timedelta(hours=1)
        self.taller.fecha_fin = timezone.now() + timedelta(hours=1)
        self.taller.save()

        with self.assertRaisesRegex(ValidationError, "ya empezó"):
            Coordinador.editar_taller(
                taller_id=self.taller.pk,
                cupo_maximo=15,
                fecha_inicio=timezone.now() + timedelta(days=3),
                fecha_fin=timezone.now() + timedelta(days=3, hours=2),
                motivo=self.motivo,
                usuario=self.usuario,
            )

    def test_coordinador_no_puede_editar_taller_ajeno(self):
        otro_coordinador = Usuario.objects.create_user(
            username="otro_coordinador",
            password="test123",
            rol=Usuario.Rol.COORDINADOR,
        )

        with self.assertRaises(ValidationError):
            Coordinador.editar_taller(
                taller_id=self.taller.pk,
                cupo_maximo=15,
                fecha_inicio=timezone.now() + timedelta(days=3),
                fecha_fin=timezone.now() + timedelta(days=3, hours=2),
                motivo=self.motivo,
                usuario=otro_coordinador,
            )

    def test_no_permite_reducir_cupo_bajo_inscripciones_confirmadas(self):
        for numero in range(4):
            participante = Usuario.objects.create_user(
                username=f"participante_{numero}",
                password="test123",
                rol=Usuario.Rol.PARTICIPANTE,
            )
            from inscripciones.models import Inscripcion
            Inscripcion.objects.create(
                participante=participante,
                taller=self.taller,
                estado="CONFIRMADO",
            )

        with self.assertRaises(ValidationError):
            Coordinador.editar_taller(
                taller_id=self.taller.pk,
                cupo_maximo=3,
                fecha_inicio=timezone.now() + timedelta(days=3),
                fecha_fin=timezone.now() + timedelta(days=3, hours=2),
                motivo=self.motivo,
                usuario=self.usuario,
            )

    def test_historial_guarda_fechas_anteriores(self):
        fecha_inicio_original = self.taller.fecha_inicio
        fecha_fin_original = self.taller.fecha_fin

        nueva_fecha_inicio = timezone.now() + timedelta(days=3)
        nueva_fecha_fin = nueva_fecha_inicio + timedelta(hours=2)

        Coordinador.editar_taller(
            taller_id=self.taller.pk,
            cupo_maximo=15,
            fecha_inicio=nueva_fecha_inicio,
            fecha_fin=nueva_fecha_fin,
            motivo=self.motivo,
            usuario=self.usuario,
        )

        historial = TallerHistorial.objects.get(taller=self.taller)

        self.assertEqual(historial.fecha_inicio_anterior, fecha_inicio_original)
        self.assertEqual(historial.fecha_fin_anterior, fecha_fin_original)



