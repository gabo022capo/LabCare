# Plan de commits (reemplaza apellido-nombre)
```bash
git init
git checkout -b examen/apellido-nombre
git add ANALISIS.md && git commit -m "docs: agrega analisis, casos de uso y esquema MVC"
git add schema.sql db.py requirements.txt .gitignore && git commit -m "feat: crea tablas, restricciones y datos semilla"
git add models.py && git commit -m "feat: agrega modelo con validaciones y flujo de estados"
git add controllers.py app.py && git commit -m "feat: agrega controlador y rutas de solicitudes"
git add templates && git commit -m "feat: agrega vistas de listado, formulario y detalle"
git add tests.py && git commit -m "test: documenta escenarios de solicitudes"
git add README.md COMANDOS_GIT.md && git commit -m "docs: agrega README con instrucciones de ejecucion"
git status && git log --oneline
git remote add origin https://github.com/USUARIO/labcare.git
git push -u origin examen/apellido-nombre
```
