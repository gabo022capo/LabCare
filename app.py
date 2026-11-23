import os
import traceback
from flask import Flask, render_template
from dotenv import load_dotenv
from controllers import bp
from db import close_db, init_db

load_dotenv()


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambiar-en-produccion")
    app.config["DATABASE_URL"] = None if db_path else os.environ.get("DATABASE_URL")
    app.config["DATABASE"] = db_path or os.environ.get("LABCARE_DB", "labcare.db")
    app.teardown_appcontext(close_db)
    @app.before_request
    def registrar_peticion():
        from flask import request
        print("PETICION:", request.method, request.path, flush=True)
    with app.app_context():
        init_db()
    app.register_blueprint(bp)

    @app.errorhandler(404)
    def no_encontrado(e):
        return render_template("error.html", titulo="No encontrado",
                               mensaje="El recurso solicitado no existe."), 404

    @app.errorhandler(Exception)
    def error_generico(e):  # no se muestran trazas al usuario
        print("ERROR LABCARE:", type(e).__name__, repr(e), flush=True)
        with open("labcare_error.log", "a", encoding="utf-8") as log:
            log.write(traceback.format_exc())
        app.logger.exception(e)
        return render_template("error.html", titulo="Error",
                               mensaje="Ocurrió un error inesperado. Intente de nuevo."), 500

    return app


if __name__ == "__main__":
    app = create_app()
    if app.config.get("DATABASE_URL"):
        print("LabCare conectado con PostgreSQL/Supabase")
    else:
        print("LabCare usando SQLite local")
    app.run(debug=False)
