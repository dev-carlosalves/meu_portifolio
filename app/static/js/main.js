/**
 * main.js — Bootstrap principal da aplicação.
 *
 * Inicializa todos os módulos na ordem correta,
 * adiciona efeitos visuais globais e utilitários compartilhados.
 */

/* ── Utilitário: ano no footer ────────────────────────────── */
function setFooterYear() {
  const el = document.getElementById('footer-year');
  if (el) el.textContent = new Date().getFullYear();
}

/* ── Scroll Indicator: clique rola para seção seguinte ────── */
function initScrollIndicator() {
  const indicator = document.getElementById('scroll-indicator');
  if (!indicator) return;

  function scrollToNext() {
    const hero = document.getElementById('hero');
    if (!hero) return;
    const nextSection = hero.nextElementSibling;
    if (nextSection) {
      nextSection.scrollIntoView({ behavior: 'smooth' });
    }
  }

  indicator.addEventListener('click', scrollToNext);
  indicator.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      scrollToNext();
    }
  });
}

/* ── Partículas decorativas no hero ──────────────────────── */
function initHeroParticles() {
  const hero = document.getElementById('hero');
  if (!hero) return;

  // Respeita preferência de acessibilidade
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const colors = [
    'rgba(6, 182, 212, 0.4)',
    'rgba(34, 211, 238, 0.3)',
    'rgba(255, 255, 255, 0.15)',
  ];

  for (let i = 0; i < 18; i++) {
    const particle = document.createElement('div');
    particle.className = 'hero-particle';

    const size  = Math.random() * 4 + 2;
    const delay = Math.random() * 20;
    const dur   = Math.random() * 25 + 20;
    const left  = Math.random() * 100;
    const color = colors[Math.floor(Math.random() * colors.length)];

    particle.style.cssText = `
      left: ${left}%;
      bottom: -${size + 2}px;
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      animation-duration: ${dur}s;
      animation-delay: -${delay}s;
      border-radius: 50%;
    `;

    hero.appendChild(particle);
  }
}

/* ── Lazy loading de imagens via IntersectionObserver ─────── */
function initLazyImages() {
  const images = document.querySelectorAll('img[data-src]');
  if (!images.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          observer.unobserve(img);
        }
      });
    },
    { rootMargin: '200px' }
  );

  images.forEach((img) => observer.observe(img));
}

/* ── Smooth scroll para âncoras internas ─────────────────── */
function initSmoothAnchorLinks() {
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const href   = link.getAttribute('href');
      const target = document.querySelector(href);
      if (!target) return;

      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });

      // Atualiza foco para acessibilidade
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    });
  });
}

/* ── Botões de download ───────────────────────────────────────── */
function initDownloadButtons() {
  document.querySelectorAll('a[download]').forEach((btn) => {
    btn.addEventListener('click', function () {
      const originalHTML = this.innerHTML;
      this.innerHTML = '<i class="fa-solid fa-check" aria-hidden="true"></i><span>Download iniciado</span>';
      this.style.pointerEvents = 'none';
      
      setTimeout(() => {
        this.innerHTML = originalHTML;
        this.style.pointerEvents = 'auto';
      }, 3000);
    });
  });
}

/* ── Bootstrap ────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // 1. Layout e navegação
  Navbar.init();

  // 2. Animações
  AOSInit.init();

  // 3. Efeitos visuais
  initHeroParticles();
  initScrollIndicator();

  // 4. Performance
  initLazyImages();

  // 5. UX
  initSmoothAnchorLinks();
  setFooterYear();
  initDownloadButtons();
});
