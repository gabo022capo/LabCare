require('dotenv').config();
const express = require('express');
const path = require('path');
const { errorHandler } = require('./src/middlewares/errorHandler');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use('/api/solicitudes', require('./src/routes/solicitud.routes'));
app.use('/api/equipos', require('./src/routes/equipo.routes'));
app.use('/api', (req, res) => res.status(404).json({ ok: false, mensaje: 'Ruta no encontrada.' }));
app.use(errorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`LabCare en http://localhost:${PORT}`));
