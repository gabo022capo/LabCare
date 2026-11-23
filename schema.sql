-- Script de base de datos LabCare (SQLite). Se ejecuta al iniciar la app.
CREATE TABLE IF NOT EXISTS equipo (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo    TEXT NOT NULL UNIQUE,
    nombre    TEXT NOT NULL,
    ubicacion TEXT NOT NULL,
    estado    TEXT NOT NULL DEFAULT 'OPERATIVO'
);

CREATE TABLE IF NOT EXISTS solicitud (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_solicitud    TEXT NOT NULL UNIQUE,
    equipo_id           INTEGER NOT NULL REFERENCES equipo(id),
    solicitante         TEXT NOT NULL,
    descripcion         TEXT NOT NULL,
    prioridad           TEXT NOT NULL CHECK (prioridad IN ('BAJA','MEDIA','ALTA')),
    estado              TEXT NOT NULL CHECK (estado IN ('PENDIENTE','EN_PROCESO','RESUELTA','CANCELADA')),
    fecha_registro      TEXT NOT NULL,
    fecha_actualizacion TEXT NOT NULL,
    activo              INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

INSERT OR IGNORE INTO equipo (codigo, nombre, ubicacion, estado) VALUES
 ('EQ-001', 'Computadora de escritorio', 'Laboratorio 1',        'OPERATIVO'),
 ('EQ-002', 'Proyector multimedia',       'Aula 204',             'OPERATIVO'),
 ('EQ-003', 'Router de laboratorio',      'Laboratorio de Redes', 'OPERATIVO'),
 ('EQ-004', 'Impresora de oficina',       'Secretaría',           'OPERATIVO');
