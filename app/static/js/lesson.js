/**
 * lesson.js — Interatividade da Página de Reprodução da Aula
 *
 * Sincroniza o status de conclusão com o localStorage (chave trail_progress_{trailId})
 * para que fique 100% integrado com a página principal da trilha.
 */

(function () {
  'use strict';

  const metaEl = document.getElementById('lesson-meta-data');
  if (!metaEl) return;

  let meta;
  try {
    meta = JSON.parse(metaEl.textContent);
  } catch (e) {
    return;
  }

  const TRAIL_ID = meta.trailId;
  const AULA_ID = meta.aulaId;
  const TOTAL_AULAS = meta.totalAulas || 0;
  const STORAGE_KEY = `trail_progress_${TRAIL_ID}`;

  const btnComplete = document.getElementById('btn-complete-lesson');
  const btnCompleteText = document.getElementById('btn-complete-text');
  const btnCompleteIcon = document.getElementById('btn-complete-icon');
  const playlistPct = document.getElementById('playlist-pct-label');
  const playlistFill = document.getElementById('playlist-progress-fill');

  function loadCompleted() {
    try {
      return new Set(JSON.parse(localStorage.getItem(STORAGE_KEY)) || []);
    } catch {
      return new Set();
    }
  }

  function saveCompleted(set) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
    } catch {}
  }

  function updatePlaylistProgress(completed) {
    const count = completed.size;
    const pct = TOTAL_AULAS > 0 ? Math.round((count / TOTAL_AULAS) * 100) : 0;
    if (playlistPct) playlistPct.textContent = pct + '%';
    if (playlistFill) playlistFill.style.width = pct + '%';

    // Atualiza ícones da playlist
    document.querySelectorAll('.playlist-row__status, .playlist-item-status-icon').forEach(icon => {
      const id = icon.dataset.aulaId;
      if (completed.has(id)) {
        icon.innerHTML = '<i class="fa-solid fa-check" style="color:#34d399"></i>';
      } else if (id === AULA_ID) {
        icon.innerHTML = '<i class="fa-solid fa-play"></i>';
      } else {
        icon.innerHTML = '<i class="fa-regular fa-circle"></i>';
      }
    });
  }

  function updateButtonState(isCompleted) {
    if (!btnComplete) return;
    if (isCompleted) {
      btnComplete.classList.add('btn-complete-toggle--completed', 'btn-toggle-complete--completed');
      if (btnCompleteText) btnCompleteText.textContent = 'Aula Concluída';
      if (btnCompleteIcon) btnCompleteIcon.className = 'fa-solid fa-circle-check';
    } else {
      btnComplete.classList.remove('btn-complete-toggle--completed', 'btn-toggle-complete--completed');
      if (btnCompleteText) btnCompleteText.textContent = 'Concluir Aula';
      if (btnCompleteIcon) btnCompleteIcon.className = 'fa-regular fa-circle-check';
    }
  }


  function handleToggleComplete() {
    const completed = loadCompleted();
    const willComplete = !completed.has(AULA_ID);

    if (willComplete) {
      completed.add(AULA_ID);
    } else {
      completed.delete(AULA_ID);
    }

    saveCompleted(completed);
    updateButtonState(willComplete);
    updatePlaylistProgress(completed);
  }

  function init() {
    const completed = loadCompleted();
    updateButtonState(completed.has(AULA_ID));
    updatePlaylistProgress(completed);

    if (btnComplete) {
      btnComplete.addEventListener('click', handleToggleComplete);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
