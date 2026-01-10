const db = require('../config/db');

class Artwork {
  static async create({ title, description, filename }) {
    const [result] = await db.execute(
      'INSERT INTO artworks (title, description, filename) VALUES (?, ?, ?)',
      [title, description, filename]
    );
    return result.insertId;
  }

  static async getAll() {
    const [rows] = await db.execute('SELECT id, title, description, filename, created_at FROM artworks');
    return rows;
  }
}

module.exports = Artwork;