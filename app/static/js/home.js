/**
 * home.js — Módulo exclusivo da página inicial.
 *
 * Responsabilidades:
 *   1. Typed.js — efeito de digitação nas áreas de atuação (subtítulo)
 *   2. Contadores animados das estatísticas
 */

/* ══════════════════════════════════════════════════════════════
   1. TYPED.JS — Texto rotativo no hero
   (As 3 áreas de atuação são exibidas com efeito de digitação)
══════════════════════════════════════════════════════════════ */
function initTyped() {
  const el = document.getElementById('typed-output');
  if (!el || typeof Typed === 'undefined') return;

  new Typed('#typed-output', {
    strings: [
      'Engenharia Mecânica',
      'Desenvolvimento Python',
      'Modelagem CAD',
      'Aprendizagem Contínua',
    ],
    typeSpeed:    55,
    backSpeed:    30,
    backDelay:    2200,
    startDelay:   600,
    loop:         true,
    smartBackspace: true,
    cursorChar:   '|',
  });
}


/* ══════════════════════════════════════════════════════════════
   2. CONTADORES ANIMADOS — Estatísticas do hero
══════════════════════════════════════════════════════════════ */
function animateCounter(el, target, duration = 1200) {
  const start   = performance.now();
  const initial = 0;

  function step(timestamp) {
    const elapsed  = timestamp - start;
    const progress = Math.min(elapsed / duration, 1);
    // Easing: ease-out cubic
    const eased    = 1 - Math.pow(1 - progress, 3);
    const current  = Math.round(initial + (target - initial) * eased);

    el.textContent = current;

    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      el.textContent = target;
    }
  }

  requestAnimationFrame(step);
}

function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  // Respeita prefers-reduced-motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    counters.forEach((el) => {
      el.textContent = el.dataset.count;
    });
    return;
  }

  // IntersectionObserver: anima apenas quando o elemento entra na tela
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el     = entry.target;
        const target = parseInt(el.dataset.count, 10);
        animateCounter(el, target);
        observer.unobserve(el);
      });
    },
    { threshold: 0.5 }
  );

  counters.forEach((el) => observer.observe(el));
}


/* ══════════════════════════════════════════════════════════════
   Bootstrap — aguarda DOM
══════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  initTyped();
  initCounters();
});
