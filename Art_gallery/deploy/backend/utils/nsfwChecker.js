const nsfw = require('nsfwjs');
const tf = require('@tensorflow/tfjs-node');
const fs = require('fs').promises;

let _model;

/**
 * Загружает модель NSFWJS один раз.
 * Модель должна быть доступна по: http://localhost:3000/nsfw-model/
 * (раздаётся через express.static в server.js)
 */
async function loadModel() {
  if (!_model) {
    console.log('🧠 Загружаем NSFWJS модель из http://localhost:3000/nsfw-model/');
    // NSFWJS автоматически добавит /model.json и /group1-shard1of1.bin
    _model = await nsfw.load('http://localhost:3000/nsfw-model/');
    console.log('✅ Модель успешно загружена');
  }
  return _model;
}

/**
 * Проверяет, является ли изображение безопасным (без 18+ контента).
 * @param {string} imagePath - путь к локальному файлу изображения
 * @returns {Promise<boolean>} true — если безопасно
 */
async function isSafeForWork(imagePath) {
  try {
    const model = await loadModel();
    const imageBuffer = await fs.readFile(imagePath);
    const image = tf.node.decodeImage(imageBuffer, 3); // 3 канала (RGB)

    const predictions = await model.classify(image);
    image.dispose();

    // Классы NSFWJS: 'Neutral', 'Porn', 'Sexy', 'Hentai', 'Drawing'
    const unsafeClasses = ['Porn', 'Sexy', 'Hentai'];
    const isUnsafe = predictions.some(p =>
      unsafeClasses.includes(p.className) && p.probability > 0.6
    );

    console.log('🔍 Результат NSFW-проверки:', predictions);
    return !isUnsafe;
  } catch (err) {
    console.error('❌ Ошибка при проверке изображения:', err.message);
    // В случае ошибки — считаем небезопасным (или можно выбросить исключение)
    return false;
  }
}

module.exports = { isSafeForWork };