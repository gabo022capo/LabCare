# LabCare · Solicitudes de mantenimiento

Módulo web para registrar, consultar, editar, cambiar de estado, buscar/filtrar y eliminar (lógicamente) solicitudes de mantenimiento de equipos de laboratorio.

**Tecnologías:** Node.js, Express, Supabase (PostgreSQL), HTML/CSS/JavaScript.
**Arquitectura:** rutas → controlador → servicio (reglas) → modelo (supabase-js) → Supabase. El frontend (`public/`) consume la API REST.

## Requisitos
- Node.js 18 o superior
- Un proyecto en [supabase.com](https://supabase.com)

## Pasos de ejecución
1. En Supabase abre **SQL Editor**, pega todo `sql/001_schema.sql` y ejecútalo (crea tablas, trigger, RLS y datos de ejemplo).
2. En **Project Settings → API** copia la *Project URL* y la clave *service_role*. Esta clave tiene permisos elevados: no la compartas ni la publiques.
3. Copia `.env.example` a `.env` y reemplaza los valores de ejemplo por los de tu proyecto.
4. Instala y ejecuta:
   ```bash
   npm install
   npm test
   npm start
   ```
5. Abre http://localhost:3000

En Windows PowerShell, puedes crear el archivo con `Copy-Item .env.example .env`. Si una clave de servicio real estuvo incluida en un repositorio o se compartió públicamente, rótala desde Supabase antes de usarla.

## API
| Método | Ruta | Descripción |
|---|---|---|
| GET | /api/solicitudes?q=&prioridad=&estado= | Listar activas, con búsqueda y filtros |
| GET | /api/solicitudes/:id | Detalle |
| POST | /api/solicitudes | Registrar |
| PUT | /api/solicitudes/:id | Editar solicitante, descripción, prioridad |
| PATCH | /api/solicitudes/:id/estado | Cambiar estado (409 si la transición no es válida) |
| DELETE | /api/solicitudes/:id | Eliminación lógica |
| GET | /api/equipos | Catálogo de equipos |

## Flujo de estados
PENDIENTE → EN_PROCESO | CANCELADA · EN_PROCESO → RESUELTA | CANCELADA · RESUELTA y CANCELADA son finales.
