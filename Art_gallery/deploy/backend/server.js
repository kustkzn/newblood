const express = require('express');
const path = require('path');
const artworksRoutes = require('./routes/artworks');

const app = express();
const PORT = process.env.PORT || 3000;

// Раздаём фронтенд
app.use(express.static(path.join(__dirname, '../frontend')));

// Раздаём загруженные изображения
app.use('/uploads', express.static(path.join(__dirname, 'public')));

// ⭐️ КРИТИЧЕСКИ ВАЖНО: раздаём ПАПКУ С МОДЕЛЬЮ по пути /nsfw-model
// Файлы model.json и group1-shard1of1.bin должны лежать в ./nsfwjs/model/
app.use('/nsfw-model', express.static(path.join(__dirname, 'nsfwjs/model')));

// Парсинг JSON
app.use(express.json());

// API маршруты
app.use('/api/artworks', artworksRoutes);

// SPA fallback — все остальные запросы → index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});


app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ Сервер запущен на http://localhost:${PORT}`);
  console.log(`🧠 Модель доступна по: http://localhost:${PORT}/nsfw-model/model.json`);
});