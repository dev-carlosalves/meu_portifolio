/**
 * trail.js — Interatividade da página de trilha de aprendizado.
 *
 * Responsabilidades:
 *   1. Accordion — expande/recolhe seções ao clicar no cabeçalho
 *   2. Progresso — persiste aulas concluídas em localStorage por trilha
 *   3. Barra de progresso — atualiza em tempo real ao marcar/desmarcar
 *   4. Botão "Continuar de onde parei" — rola até a próxima aula pendente
 */

(function () {
  'use strict';

  // ── Leitura dos metadados da trilha ─────────────────────────────
  const metaEl = document.getElementById('trail-data');
  if (!metaEl) return;

  let meta;
  try {
    meta = JSON.parse(metaEl.textContent);
  } catch (e) {
    return;
  }

  const TRAIL_ID   = meta.trailId;
  const TOTAL      = meta.totalAulas;
  const STORAGE_KEY = `trail_progress_${TRAIL_ID}`;

  // ── Elementos do DOM ────────────────────────────────────────────
  const progressFill = document.getElementById('trail-progress-fill');
  const progressBar  = document.getElementById('trail-progress-bar');
  const pctLabel     = document.getElementById('trail-pct-label');
  const metaLabel    = document.getElementById('trail-progress-meta');
  const btnContinuar = document.getElementById('btn-continuar');
  const accordion    = document.getElementById('trail-accordion');

  // ── localStorage helpers ─────────────────────────────────────────
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
    } catch {
      // localStorage pode estar desabilitado em modo privado
    }
  }

  // ── Atualizar barra de progresso ─────────────────────────────────
  function updateProgress(completed) {
    const count = completed.size;
    const pct   = TOTAL > 0 ? Math.round((count / TOTAL) * 100) : 0;

    if (progressFill) {
      progressFill.style.width = pct + '%';
    }
    if (progressBar) {
      progressBar.setAttribute('aria-valuenow', pct);
    }
    if (pctLabel) {
      pctLabel.textContent = pct + '%';
    }
    if (metaLabel) {
      const plural = count !== 1 ? 's' : '';
      metaLabel.textContent = `${count} de ${TOTAL} aula${plural} concluída${plural}`;
    }
  }

  // ── Aplicar estado salvo nos checkboxes ───────────────────────────
  function applyState(completed) {
    document.querySelectorAll('.trail-lesson__checkbox').forEach(cb => {
      const id = cb.dataset.aulaId;
      const isChecked = completed.has(id);
      cb.checked = isChecked;
      cb.closest('.trail-lesson').classList.toggle('trail-lesson--done', isChecked);
    });
    updateProgress(completed);
  }

  // ── Toggle de aula concluída ─────────────────────────────────────
  function handleCheckbox(e) {
    const cb = e.target;
    if (!cb.classList.contains('trail-lesson__checkbox')) return;

    const aulaId   = cb.dataset.aulaId;
    const completed = loadCompleted();

    if (cb.checked) {
      completed.add(aulaId);
    } else {
      completed.delete(aulaId);
    }

    saveCompleted(completed);
    cb.closest('.trail-lesson').classList.toggle('trail-lesson--done', cb.checked);
    updateProgress(completed);
  }

  // ── Accordion: toggle seção ───────────────────────────────────────
  function toggleSection(btn) {
    const section   = btn.closest('.trail-section');
    const body      = section.querySelector('.trail-section__body');
    const isOpen    = section.classList.contains('trail-section--open');
    const expanded  = !isOpen;

    // Fecha todas as outras seções (opcional — remova para multi-open)
    // accordion.querySelectorAll('.trail-section').forEach(s => {
    //   if (s !== section) {
    //     s.classList.remove('trail-section--open');
    //     s.querySelector('.trail-section__header').setAttribute('aria-expanded', 'false');
    //   }
    // });

    section.classList.toggle('trail-section--open', expanded);
    btn.setAttribute('aria-expanded', String(expanded));
  }

  function handleAccordion(e) {
    const btn = e.target.closest('.trail-section__header');
    if (!btn) return;
    toggleSection(btn);
  }

  // ── Botão "Continuar de onde parei" ──────────────────────────────
  function handleContinuar() {
    const completed = loadCompleted();
    // Encontra a primeira aula não concluída
    const allAulas = document.querySelectorAll('.trail-lesson');
    let target = null;
    for (const aula of allAulas) {
      const id = aula.dataset.aulaId;
      if (!completed.has(id)) {
        target = aula;
        break;
      }
    }

    if (!target) {
      // Todas concluídas — rola para o início
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    // Abre a seção que contém a aula alvo
    const section = target.closest('.trail-section');
    if (section && !section.classList.contains('trail-section--open')) {
      const btn = section.querySelector('.trail-section__header');
      if (btn) toggleSection(btn);
    }

    // Rola até a aula com destaque temporário
    setTimeout(() => {
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      target.style.transition = 'background 0.2s';
      target.style.background = 'rgba(14, 165, 233, 0.06)';
      setTimeout(() => {
        target.style.background = '';
      }, 1500);
    }, 350);
  }

  // ── Inicialização ────────────────────────────────────────────────
  function init() {
    // Carrega progresso salvo e aplica estado inicial
    const completed = loadCompleted();
    applyState(completed);

    // Listener único no accordion (event delegation)
    if (accordion) {
      accordion.addEventListener('change', handleCheckbox);
      accordion.addEventListener('click', handleAccordion);
    }

    // Botão continuar
    if (btnContinuar) {
      btnContinuar.addEventListener('click', handleContinuar);
    }
  }

  // Aguarda o DOM estar pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
