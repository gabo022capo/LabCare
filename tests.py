"""Pruebas automáticas CP-01 a CP-12. Ejecutar: python -m unittest tests -v"""
import os
import sqlite3
import tempfile
import unittest
from app import create_app

VALIDO = {"equipo_id": "1", "solicitante": "Ana Pérez",
          "descripcion": "El equipo no enciende nunca", "prioridad": "ALTA"}


class PruebasLabCare(unittest.TestCase):
    def setUp(self):
        fd, self.ruta = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.app = create_app(self.ruta)
        self.c = self.app.test_client()

    def tearDown(self):
        os.remove(self.ruta)

    def sql(self, consulta, params=()):
        con = sqlite3.connect(self.ruta)
        fila = con.execute(consulta, params).fetchall()
        con.close()
        return fila

    def crear(self, **cambios):
        return self.c.post("/solicitudes/nueva", data={**VALIDO, **cambios})

    def total(self):
        return self.sql("SELECT COUNT(*) FROM solicitud")[0][0]

    def test_cp01_registro_valido(self):
        r = self.crear()
        self.assertEqual(r.status_code, 302)
        fila = self.sql("SELECT codigo_solicitud, estado FROM solicitud")[0]
        self.assertTrue(fila[0].startswith("SOL-"))
        self.assertEqual(fila[1], "PENDIENTE")

    def test_cp02_solicitante_invalido(self):
        for valor in ("", "  ab  "):
            self.assertEqual(self.crear(solicitante=valor).status_code, 400)
        self.assertEqual(self.total(), 0)

    def test_cp03_descripcion_invalida(self):
        for valor in ("", "corta"):
            self.assertEqual(self.crear(descripcion=valor).status_code, 400)
        self.assertEqual(self.total(), 0)

    def test_cp04_prioridad_invalida(self):
        self.assertEqual(self.crear(prioridad="URGENTE").status_code, 400)
        self.assertEqual(self.total(), 0)

    def test_cp05_equipo_inexistente(self):
        self.assertEqual(self.crear(equipo_id="999").status_code, 400)
        self.assertEqual(self.total(), 0)

    def test_cp06_editar_solo_el_seleccionado(self):
        self.crear()
        self.crear(solicitante="Luis Gómez")
        antes = self.sql("SELECT codigo_solicitud, fecha_registro FROM solicitud WHERE id=1")
        r = self.c.post("/solicitudes/1/editar", data={
            "solicitante": "Carlos Nuevo", "descripcion": "Descripción modificada ok",
            "prioridad": "BAJA"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.sql("SELECT solicitante FROM solicitud WHERE id=1")[0][0], "Carlos Nuevo")
        self.assertEqual(self.sql("SELECT solicitante FROM solicitud WHERE id=2")[0][0], "Luis Gómez")
        self.assertEqual(antes, self.sql("SELECT codigo_solicitud, fecha_registro FROM solicitud WHERE id=1"))

    def test_cp07_pendiente_a_en_proceso(self):
        self.crear()
        self.c.post("/solicitudes/1/estado", data={"estado": "EN_PROCESO"})
        self.assertEqual(self.sql("SELECT estado FROM solicitud")[0][0], "EN_PROCESO")

    def test_cp08_resuelta_a_pendiente_rechazada(self):
        self.crear()
        self.c.post("/solicitudes/1/estado", data={"estado": "EN_PROCESO"})
        self.c.post("/solicitudes/1/estado", data={"estado": "RESUELTA"})
        self.c.post("/solicitudes/1/estado", data={"estado": "PENDIENTE"})
        self.assertEqual(self.sql("SELECT estado FROM solicitud")[0][0], "RESUELTA")

    def test_cp09_eliminacion_logica(self):
        self.crear()
        self.c.post("/solicitudes/1/eliminar")
        self.assertEqual(self.total(), 1)
        self.assertEqual(self.sql("SELECT activo FROM solicitud")[0][0], 0)
        self.assertNotIn("SOL-", self.c.get("/solicitudes").get_data(as_text=True))

    def test_cp10_busqueda_y_filtros(self):
        self.crear(solicitante="Ana Pérez", prioridad="ALTA")
        self.crear(solicitante="Luis Gómez", prioridad="BAJA", equipo_id="2")
        html = self.c.get("/solicitudes?q=ana").get_data(as_text=True)
        self.assertIn("Ana Pérez", html); self.assertNotIn("Luis Gómez", html)
        html = self.c.get("/solicitudes?q=PROYECTOR").get_data(as_text=True)
        self.assertIn("Luis Gómez", html); self.assertNotIn("Ana Pérez", html)
        html = self.c.get("/solicitudes?prioridad=BAJA").get_data(as_text=True)
        self.assertIn("Luis Gómez", html); self.assertNotIn("Ana Pérez", html)
        html = self.c.get("/solicitudes?estado=RESUELTA").get_data(as_text=True)
        self.assertNotIn("Luis Gómez", html)

    def test_cp11_id_inexistente(self):
        self.assertEqual(self.c.get("/solicitudes/999").status_code, 404)
        self.assertEqual(self.c.get("/solicitudes/999/editar").status_code, 404)
        self.assertEqual(self.c.post("/solicitudes/999/editar", data=VALIDO).status_code, 404)

    def test_cp12_persistencia(self):
        self.crear()
        otra = create_app(self.ruta).test_client()  # "reinicia" la aplicación
        self.assertIn("Ana Pérez", otra.get("/solicitudes").get_data(as_text=True))

    def test_xss_se_escapa(self):
        self.crear(solicitante="<script>alert(1)</script>")
        html = self.c.get("/solicitudes").get_data(as_text=True)
        self.assertNotIn("<script>alert(1)</script>", html)


if __name__ == "__main__":
    unittest.main()
