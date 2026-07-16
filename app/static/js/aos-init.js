/**
 * aos-init.js — Configuração centralizada do AOS (Animate On Scroll).
 *
 * Documentação AOS: https://michalsnik.github.io/aos/
 */

const AOSInit = (() => {
  function init() {
    if (typeof AOS === 'undefined') {
      console.warn('[AOSInit] AOS não foi carregado.');
      return;
    }

    AOS.init({
      duration:   700,       // duração padrão (ms)
      easing:     'ease-out-cubic',
      once:       true,      // anima apenas uma vez ao entrar na viewport
      offset:     80,        // margem antes de disparar
      delay:      0,         // delay padrão
      mirror:     false,     // não anima ao sair da viewport
      anchorPlacement: 'top-bottom',
    });
  }

  return { init };
})();
