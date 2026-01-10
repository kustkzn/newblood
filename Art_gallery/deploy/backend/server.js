const express = require('express');
const path = require('path');
const artworksRoutes = require('./routes/artworks');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, '../frontend')));

app.use('/uploads', express.static(path.join(__dirname, 'public')));

app.use('/nsfw-model', express.static(path.join(__dirname, 'nsfwjs/model')));

app.use(express.json());

app.use('/api/artworks', artworksRoutes);

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});


app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ Сервер запущен на http://localhost:${PORT}`);
  console.log(`🧠 Модель доступна по: http://localhost:${PORT}/nsfw-model/model.json`);
});