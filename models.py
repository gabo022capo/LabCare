"""MODELO: acceso a datos (consultas parametrizadas) y reglas de negocio."""
from datetime import datetime
from flask import current_app
from db import get_db

PRIORIDADES = ("BAJA", "MEDIA", "ALTA")
ESTADOS = ("PENDIENTE", "EN_PROCESO", "RESUELTA", "CANCELADA")
TRANSICIONES = {
    "PENDIENTE": ("EN_PROCESO", "CANCELADA"),
    "EN_PROCESO": ("RESUELTA", "CANCELADA"),
    "RESUELTA": (),
    "CANCELADA": (),
}


def ahora():
    if current_app.config.get("DATABASE_URL"):
        return datetime.now().astimezone()
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def equipos_disponibles():
    return get_db().execute(
        "SELECT * FROM equipo WHERE estado = 'OPERATIVO' ORDER BY codigo").fetchall()


def validar(datos, con_equipo=True):
    errores = []
    if len(datos.get("solicitante", "")) < 3:
        errores.append("El solicitante es obligatorio (mínimo 3 caracteres).")
    if len(datos.get("descripcion", "")) < 10:
        errores.append("La descripción es obligatoria (mínimo 10 caracteres).")
    if datos.get("prioridad") not in PRIORIDADES:
        errores.append("La prioridad debe ser BAJA, MEDIA o ALTA.")
    if con_equipo:
        equipo = None
        if datos.get("equipo_id", "").isdigit():
            equipo = get_db().execute(
                "SELECT id FROM equipo WHERE id = ? AND estado = 'OPERATIVO'",
                (int(datos["equipo_id"]),)).fetchone()
        if equipo is None:
            errores.append("Debe seleccionar un equipo existente y disponible.")
    return errores


def _generar_codigo(db):
    prefijo = "SOL-" + datetime.now().strftime("%Y%m%d") + "-"
    n = db.execute(
        "SELECT COUNT(*) AS cantidad FROM solicitud WHERE codigo_solicitud LIKE ?",
        (prefijo + "%",)).fetchone()["cantidad"]
    consecutivo = int(n) + 1
    while True:
        codigo = f"{prefijo}{consecutivo:03d}"
        existe = db.execute(
            "SELECT 1 FROM solicitud WHERE codigo_solicitud = ?",
            (codigo,)).fetchone()
        if existe is None:
            return codigo
        consecutivo += 1


def listar(q="", prioridad="", estado=""):
    sql = """SELECT s.*, e.nombre AS equipo_nombre, e.codigo AS equipo_codigo
             FROM solicitud s JOIN equipo e ON e.id = s.equipo_id
             WHERE s.activo = TRUE"""
    params = []
    if q:
        sql += (" AND (LOWER(s.codigo_solicitud) LIKE ? OR LOWER(s.solicitante) LIKE ?"
                " OR LOWER(e.nombre) LIKE ?)")
        params += [f"%{q.lower()}%"] * 3
    if prioridad:
        sql += " AND s.prioridad = ?"
        params.append(prioridad)
    if estado:
        sql += " AND s.estado = ?"
        params.append(estado)
    sql += " ORDER BY s.id DESC"
    return get_db().execute(sql, params).fetchall()


def obtener(id):
    return get_db().execute(
        """SELECT s.*, e.nombre AS equipo_nombre, e.codigo AS equipo_codigo,
                  e.ubicacion AS equipo_ubicacion
           FROM solicitud s JOIN equipo e ON e.id = s.equipo_id
           WHERE s.id = ? AND s.activo = TRUE""", (id,)).fetchone()


def crear(datos):
    db = get_db()
    fecha = ahora()
    cur = db.execute(
        """INSERT INTO solicitud (codigo_solicitud, equipo_id, solicitante, descripcion,
               prioridad, estado, fecha_registro, fecha_actualizacion, activo)
           VALUES (?, ?, ?, ?, ?, 'PENDIENTE', ?, ?, TRUE) RETURNING id""",
        (_generar_codigo(db), int(datos["equipo_id"]), datos["solicitante"],
         datos["descripcion"], datos["prioridad"], fecha, fecha))
    id = cur.fetchone()["id"]
    db.commit()
    return id


def editar(id, datos):
    """Solo cambia datos descriptivos. No toca id, código ni fecha_registro."""
    db = get_db()
    db.execute(
        """UPDATE solicitud SET solicitante = ?, descripcion = ?, prioridad = ?,
               fecha_actualizacion = ? WHERE id = ? AND activo = TRUE""",
        (datos["solicitante"], datos["descripcion"], datos["prioridad"], ahora(), id))
    db.commit()


def cambiar_estado(id, nuevo):
    """Devuelve (codigo_http, mensaje)."""
    s = obtener(id)
    if s is None:
        return 404, "La solicitud no existe."
    if nuevo not in TRANSICIONES[s["estado"]]:
        return 409, f"Transición no permitida: {s['estado']} → {nuevo}."
    db = get_db()
    db.execute("UPDATE solicitud SET estado = ?, fecha_actualizacion = ? WHERE id = ?",
               (nuevo, ahora(), id))
    db.commit()
    return 200, f"Estado actualizado a {nuevo}."


def eliminar(id):
    """Eliminación lógica: activo = FALSE."""
    db = get_db()
    db.execute("UPDATE solicitud SET activo = FALSE, fecha_actualizacion = ? WHERE id = ?",
               (ahora(), id))
    db.commit()
