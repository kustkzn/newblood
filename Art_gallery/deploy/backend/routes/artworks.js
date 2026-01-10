const express = require('express');
const router = express.Router();
const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');
const { isSafeForWork } = require('../utils/nsfwChecker');
const Artwork = require('../models/Artwork');

const UPLOAD_DIR = path.join(__dirname, '../public');
const TEMP_DIR = path.join(__dirname, 'temp');

const fss = require('fs');
fss.mkdirSync(UPLOAD_DIR, { recursive: true });
fss.mkdirSync(TEMP_DIR, { recursive: true });

router.post('/submit', async (req, res) => {
  const { imageUrl, title, description } = req.body;

  if (!imageUrl || !title) {
    return res.status(400).json({ error: 'Требуются поля: imageUrl, title' });
  }

  try {
    const tempPath = path.join(TEMP_DIR, `upload_${Date.now()}.tmp`);
    console.log(`Скачиваем для проверки: ${imageUrl}`);
    const response = await axios({ url: imageUrl, responseType: 'arraybuffer', timeout: 10000 });
    await fs.writeFile(tempPath, response.data);

    console.log('Запуск NSFW-проверки...');
    const isSafe = await isSafeForWork(tempPath);
    if (!isSafe) {
      await fs.unlink(tempPath).catch(() => {});
      return res.status(400).json({ error: 'Изображение отклонено: обнаружен 18+ контент' });
    }

    console.log('Удаляем временный файл после проверки');
    await fs.unlink(tempPath);

    console.log(' Повторная загрузка из внешнего источника');
    const finalResponse = await axios({ url: imageUrl, responseType: 'arraybuffer', timeout: 10000 });

    const safeFilename = `${Date.now()}_${path.basename(imageUrl).replace(/\W/g, '_')}`;
    const finalPath = path.join(UPLOAD_DIR, safeFilename);
    await fs.writeFile(finalPath, finalResponse.data);

    await Artwork.create({ title, description, filename: safeFilename });

    console.log('Работа добавлена');
    res.json({ success: true, message: 'Работа одобрена и добавлена на выставку!', filename: safeFilename });

  } catch (err) {
    console.error('Ошибка:', err.message);
    res.status(500).json({ error: 'Не удалось обработать изображение' });
  }
});

router.get('/', async (req, res) => {
  const artworks = await Artwork.getAll();
  res.json(artworks);
});

module.exports = router;