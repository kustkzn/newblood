document.addEventListener('DOMContentLoaded', () => {
  const openBtn = document.getElementById('openFormBtn');
  const closeBtn = document.getElementById('closeFormBtn');
  const overlay = document.getElementById('overlay');
  const formPanel = document.getElementById('formPanel');
  const artForm = document.getElementById('artForm');
  const formMessage = document.getElementById('formMessage');
  const galleryGrid = document.getElementById('galleryGrid');

  if (!openBtn || !overlay || !formPanel) {
    console.error('❌ Не найдены элементы DOM');
    return;
  }

  // Открыть форму
  openBtn.addEventListener('click', () => {
    formPanel.style.display = 'block';
    overlay.style.display = 'block';
  });

  // Закрыть форму
  const closeForm = () => {
    formPanel.style.display = 'none';
    overlay.style.display = 'none';
    if (artForm) artForm.reset();
    if (formMessage) formMessage.style.display = 'none';
  };

  if (closeBtn) closeBtn.addEventListener('click', closeForm);
  overlay.addEventListener('click', closeForm);

  // Отправка формы
  if (artForm && galleryGrid) {
    artForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const imageUrl = document.getElementById('imageUrl').value.trim();
      const title = document.getElementById('title').value.trim();
      const description = document.getElementById('description').value.trim();

      if (!imageUrl || !title) {
        showMessage('url and title are required', false);
        return;
      }

      try {
        const res = await fetch('/api/artworks/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ imageUrl, title, description })
        });

        const result = await res.json();
        if (res.ok) {
          showMessage('submission accepted', true);
          setTimeout(() => {
            closeForm();
            loadGallery();
          }, 1500);
        } else {
          showMessage(result.error || 'submission failed', false);
        }
      } catch (err) {
        showMessage('network error', false);
      }
    });
  }

  // Сообщение
  function showMessage(text, isSuccess) {
    if (!formMessage) return;
    formMessage.textContent = text;
    formMessage.style.display = 'block';
    formMessage.style.backgroundColor = isSuccess 
      ? 'rgba(76, 175, 80, 0.2)' 
      : 'rgba(244, 67, 54, 0.2)';
    formMessage.style.color = isSuccess ? '#a5d6a7' : '#ffcdd2';
  }

  // Экранирование HTML
  const escapeHtml = (str) =>
    str.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m]));

  // Загрузка галереи
  async function loadGallery() {
    if (!galleryGrid) return;
    galleryGrid.innerHTML = '<p class="loading">loading...</p>';
    try {
      const res = await fetch('/api/artworks');
      const artworks = await res.json();

      if (artworks.length === 0) {
        galleryGrid.innerHTML = '<p class="empty">no submissions yet</p>';
        return;
      }

      galleryGrid.innerHTML = artworks.map(art => `
        <div class="artwork-card">
          <img src="/uploads/${encodeURIComponent(art.filename)}" alt="${art.title}" class="artwork-img">
          <div class="artwork-info">
            <h3>${escapeHtml(art.title)}</h3>
            <p>${art.description ? escapeHtml(art.description) : 'no description'}</p>
          </div>
        </div>
      `).join('');
    } catch (err) {
      galleryGrid.innerHTML = '<p class="empty">failed to load gallery</p>';
    }
  }

  loadGallery();
});