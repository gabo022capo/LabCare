"""CONTROLADOR: recibe peticiones, llama al modelo y elige la vista."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
import models

bp = Blueprint("main", __name__)


def _limpiar(form):
    return {k: form.get(k, "").strip()
            for k in ("equipo_id", "solicitante", "descripcion", "prioridad")}


def _form(s, errores, editar, status=200):
    return render_template("form.html", s=s, errores=errores, editar=editar,
                           equipos=models.equipos_disponibles(),
                           prioridades=models.PRIORIDADES), status


@bp.route("/")
def inicio():
    return redirect(url_for("main.index"))


@bp.route("/solicitudes")
def index():
    q = request.args.get("q", "").strip()
    prioridad = request.args.get("prioridad", "")
    estado = request.args.get("estado", "")
    return render_template("index.html", solicitudes=models.listar(q, prioridad, estado),
                           q=q, prioridad=prioridad, estado=estado,
                           prioridades=models.PRIORIDADES, estados=models.ESTADOS)


@bp.route("/solicitudes/nueva", methods=["GET", "POST"])
def nueva():
    if request.method == "GET":
        return _form({}, [], False)
    datos = _limpiar(request.form)
    errores = models.validar(datos)
    if errores:
        return _form(datos, errores, False, 400)
    print("POST NUEVA:", datos, flush=True)
    try:
        id = models.crear(datos)
        print("POST GUARDADA:", id, flush=True)
    except Exception as e:
        print("POST ERROR:", type(e).__name__, repr(e), flush=True)
        raise
    flash("Solicitud registrada correctamente.", "ok")
    return redirect(url_for("main.detalle", id=id))


@bp.route("/solicitudes/<int:id>")
def detalle(id):
    s = models.obtener(id)
    if s is None:
        abort(404)
    return render_template("detalle.html", s=s,
                           permitidos=models.TRANSICIONES[s["estado"]])


@bp.route("/solicitudes/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    s = models.obtener(id)
    if s is None:
        abort(404)
    if request.method == "GET":
        return _form(s, [], True)
    datos = _limpiar(request.form)
    errores = models.validar(datos, con_equipo=False)
    if errores:
        datos.update(id=id, codigo_solicitud=s["codigo_solicitud"],
                     equipo_nombre=s["equipo_nombre"])
        return _form(datos, errores, True, 400)
    models.editar(id, datos)
    flash("Solicitud actualizada correctamente.", "ok")
    return redirect(url_for("main.detalle", id=id))


@bp.route("/solicitudes/<int:id>/estado", methods=["POST"])
def estado(id):
    codigo, mensaje = models.cambiar_estado(id, request.form.get("estado", ""))
    if codigo == 404:
        abort(404)
    flash(mensaje, "ok" if codigo == 200 else "error")
    return redirect(url_for("main.detalle", id=id))


@bp.route("/solicitudes/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    if models.obtener(id) is None:
        abort(404)
    models.eliminar(id)
    flash("Solicitud eliminada (eliminación lógica).", "ok")
    return redirect(url_for("main.index"))
