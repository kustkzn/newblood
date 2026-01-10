const nsfw = require('nsfwjs');
const tf = require('@tensorflow/tfjs-node');
const fs = require('fs').promises;

let _model;

async function loadModel() {
  if (!_model) {
    console.log('🧠 Загружаем NSFWJS модель из http://localhost:3000/nsfw-model/');
    _model = await nsfw.load('http://localhost:3000/nsfw-model/');
    console.log('✅ Модель успешно загружена');
  }
  return _model;
}

/**
 * @param {string} imagePath 
 * @returns {Promise<boolean>} 
 */
async function isSafeForWork(imagePath) {
  try {
    const model = await loadModel();
    const imageBuffer = await fs.readFile(imagePath);
    const image = tf.node.decodeImage(imageBuffer, 3); 

    const predictions = await model.classify(image);
    image.dispose();
    

    await new Promise(resolve => setTimeout(resolve, 3000));
    const unsafeClasses = ['Porn', 'Sexy', 'Hentai'];
    const isUnsafe = predictions.some(p =>
      unsafeClasses.includes(p.className) && p.probability > 0.6
    );

    console.log('🔍 Результат NSFW-проверки:', predictions);
    return !isUnsafe;
  } catch (err) {
    console.error('❌ Ошибка при проверке изображения:', err.message);
    return false;
  }
}

module.exports = { isSafeForWork };