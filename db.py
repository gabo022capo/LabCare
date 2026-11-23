import os
import sqlite3
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from flask import current_app, g


def _psycopg_url(database_url):
    parsed = urlsplit(database_url)
    query = [(key, value) for key, value in parse_qsl(parsed.query)
             if key.lower() != "pgbouncer"]
    return urlunsplit(parsed._replace(query=urlencode(query)))


class PostgresConnection:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, sql, params=()):
        return self.connection.execute(sql.replace("?", "%s"), params)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


def get_db():
    if "db" not in g:
        database_url = current_app.config.get("DATABASE_URL")
        if database_url:
            import psycopg
            from psycopg.rows import dict_row

            g.db = PostgresConnection(
                psycopg.connect(_psycopg_url(database_url), row_factory=dict_row,
                                prepare_threshold=None))
            print("LabCare: usando PostgreSQL/Supabase")
        else:
            g.db = sqlite3.connect(current_app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
            print("LabCare: usando SQLite local")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    database_url = current_app.config.get("DATABASE_URL")
    nombre_schema = "schema_postgres.sql" if database_url else "schema.sql"
    ruta = os.path.join(os.path.dirname(__file__), nombre_schema)
    with open(ruta, encoding="utf-8") as f:
        db = get_db()
        if database_url:
            for statement in f.read().split(";"):
                if statement.strip():
                    db.execute(statement)
        else:
            db.executescript(f.read())
        db.commit()
