/**
 * navbar.js — Controla todos os comportamentos da navbar.
 *
 * Responsabilidades:
 *   1. Scroll → adiciona/remove classe .scrolled (blur, borda)
 *   2. Hamburger → toggle do mobile drawer
 *   3. Overlay → fecha o menu ao clicar fora
 *   4. Fecha drawer ao clicar em qualquer link mobile
 *   5. Back to top → exibe/oculta e rola para o topo
 *   6. Atualiza link ativo na navbar baseado em scroll (IntersectionObserver)
 */

const Navbar = (() => {
  /* ── Elementos do DOM ─────────────────────────────────────── */
  const navbar     = document.getElementById('navbar');
  const hamburger  = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  const overlay    = document.getElementById('mobile-overlay');
  const closeBtn   = document.getElementById('mobile-close');
  const backToTop  = document.getElementById('back-to-top');

  /* ── Estado ───────────────────────────────────────────────── */
  let isMenuOpen = false;
  const SCROLL_THRESHOLD = 60;

  /* ── Scroll: navbar blur + back-to-top ───────────────────── */
  function handleScroll() {
    const scrolled = window.scrollY > SCROLL_THRESHOLD;

    navbar.classList.toggle('scrolled', scrolled);

    if (backToTop) {
      backToTop.classList.toggle('is-visible', window.scrollY > 400);
    }
  }

  /* ── Mobile menu: abrir ───────────────────────────────────── */
  function openMenu() {
    isMenuOpen = true;
    mobileMenu.classList.add('is-open');
    overlay.classList.add('is-open');
    hamburger.setAttribute('aria-expanded', 'true');
    mobileMenu.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // Foco no primeiro link do menu para acessibilidade
    const firstLink = mobileMenu.querySelector('.mobile-menu__link');
    if (firstLink) firstLink.focus();
  }

  /* ── Mobile menu: fechar ──────────────────────────────────── */
  function closeMenu() {
    isMenuOpen = false;
    mobileMenu.classList.remove('is-open');
    overlay.classList.remove('is-open');
    hamburger.setAttribute('aria-expanded', 'false');
    mobileMenu.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    hamburger.focus();
  }

  /* ── Toggle menu ──────────────────────────────────────────── */
  function toggleMenu() {
    isMenuOpen ? closeMenu() : openMenu();
  }

  /* ── Fechar com Escape ────────────────────────────────────── */
  function handleKeydown(e) {
    if (e.key === 'Escape' && isMenuOpen) closeMenu();
  }

  /* ── Back to top ──────────────────────────────────────────── */
  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /* ── IntersectionObserver: destaca link ativo ─────────────── */
  function initActiveLinks() {
    const sections  = document.querySelectorAll('section[id]');
    const navLinks  = document.querySelectorAll('.navbar__link');
    if (!sections.length || !navLinks.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            navLinks.forEach((link) => {
              const isActive = link.getAttribute('href') === `#${id}`;
              link.classList.toggle('navbar__link--active', isActive);
            });
          }
        });
      },
      { rootMargin: '-40% 0px -55% 0px' }
    );

    sections.forEach((section) => observer.observe(section));
  }

  /* ── Inicialização ────────────────────────────────────────── */
  function init() {
    // Scroll
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Checa estado inicial

    // Hamburger
    if (hamburger) hamburger.addEventListener('click', toggleMenu);
    if (closeBtn)  closeBtn.addEventListener('click', closeMenu);
    if (overlay)   overlay.addEventListener('click', closeMenu);

    // Fecha ao clicar em links do menu mobile
    if (mobileMenu) {
      mobileMenu.querySelectorAll('.mobile-menu__link').forEach((link) => {
        link.addEventListener('click', closeMenu);
      });
    }

    // Escape
    document.addEventListener('keydown', handleKeydown);

    // Back to top
    if (backToTop) {
      backToTop.addEventListener('click', scrollToTop);
    }

    // Active links (apenas para página com seções)
    initActiveLinks();
  }

  return { init };
})();
