/**
 * contact.js — Script interativo da página de Contato.
 *
 * Configurações de Integração:
 * - EmailJS: Script carregado sob demanda (lazy-loading) no primeiro foco do formulário.
 * - Validações em tempo real com alertas visuais.
 * - Feedback dinâmico de botão de envio e mensagem Toast.
 */

const ContactForm = (() => {
  /* ────────────────────────────────────────────────────────────────────────────
     CONFIGURAÇÃO CENTRALIZADA DO EMAILJS
     ──────────────────────────────────────────────────────────────────────────── */
  const EMAILJS_PUBLIC_KEY  = 'lj3rBwe5g-LdBPM35';
  const EMAILJS_SERVICE_ID  = 'service_oa9atb3';
  const EMAILJS_TEMPLATE_ID = 'template_9yon5rf';   // ✅ ID real do painel EmailJS

  /* ────────────────────────────────────────────────────────────────────────────
     ELEMENTOS E VARIÁVEIS
     ──────────────────────────────────────────────────────────────────────────── */
  const form       = document.getElementById('contact-form');
  const submitBtn  = document.getElementById('submit-btn');
  const submitText = document.getElementById('submit-btn-text');
  const spinner    = document.getElementById('submit-spinner');
  const submitIcon = document.getElementById('submit-icon');
  const copyBtn    = document.getElementById('copy-email-btn');

  let isEmailJsLoaded = false;

  if (!form) return { init: () => {} };

  /* ── Validador por campo ──────────────────────────────────── */
  const validators = {
    name: (v) => v.trim().length >= 2
      ? null
      : 'Por favor, digite seu nome completo.',

    email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim())
      ? null
      : 'Digite um endereço de e-mail válido.',

    subject: (v) => v.trim().length >= 4
      ? null
      : 'O assunto deve conter pelo menos 4 caracteres.',

    message: (v) => v.trim().length >= 15
      ? null
      : 'Escreva uma mensagem com pelo menos 15 caracteres.',
  };

  /* ── Controle de erros visuais ────────────────────────────── */
  function showError(fieldId, msg) {
    const field = document.getElementById(fieldId);
    const error = document.getElementById(`${fieldId}-error`);
    if (field) field.classList.add('is-invalid');
    if (error) error.textContent = msg;
  }

  function clearError(fieldId) {
    const field = document.getElementById(fieldId);
    const error = document.getElementById(`${fieldId}-error`);
    if (field) field.classList.remove('is-invalid');
    if (error) error.textContent = '';
  }

  function validateAll() {
    let isValid = true;
    Object.keys(validators).forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (!field) return;
      const errorMsg = validators[fieldId](field.value);
      if (errorMsg) {
        showError(fieldId, errorMsg);
        isValid = false;
      } else {
        clearError(fieldId);
      }
    });
    return isValid;
  }

  /* ── Carregamento Lazy de EmailJS ─────────────────────────── */
  function loadEmailJsScript() {
    if (isEmailJsLoaded) return Promise.resolve();

    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/@emailjs/browser@3/dist/email.min.js';
      script.async = true;
      
      script.onload = () => {
        try {
          window.emailjs.init(EMAILJS_PUBLIC_KEY);
          isEmailJsLoaded = true;
          resolve();
        } catch (e) {
          reject(e);
        }
      };

      script.onerror = () => {
        console.error('[EmailJS] Falha ao carregar o script CDN.');
        reject(new Error('Script CDN de EmailJS falhou.'));
      };

      document.head.appendChild(script);
    });
  }

  /* ── Configura gatilho do lazy-load no foco ────────────────── */
  function setupLazyLoading() {
    const formFields = form.querySelectorAll('.form-input');
    formFields.forEach((field) => {
      field.addEventListener('focus', () => {
        loadEmailJsScript().catch((err) => {
          console.warn('[EmailJS] Script não pôde ser carregado preemptivamente:', err);
        });
      }, { once: true });
    });
  }

  /* ── Enviar Form via EmailJS ──────────────────────────────── */
  async function handleSubmit(e) {
    e.preventDefault();

    if (!validateAll()) return;

    setLoading(true);

    try {
      // Garante carregamento do EmailJS antes do envio
      await loadEmailJsScript();

      if (!window.emailjs) {
        throw new Error('EmailJS não inicializado na janela.');
      }

      // Envia formulário usando a API do EmailJS
      await window.emailjs.sendForm(
        EMAILJS_SERVICE_ID,
        EMAILJS_TEMPLATE_ID,
        form
      );

      showToast('Mensagem enviada com sucesso! Obrigado pelo contato. Responderei assim que possível. 🚀', 'success');
      form.reset();
      Object.keys(validators).forEach(clearError);

    } catch (err) {
      console.error('[ContactForm] Erro crítico no envio:');
      console.error('  Status:', err?.status);
      console.error('  Texto: ', err?.text);
      console.error('  Objeto completo:', err);
      showToast('Não foi possível enviar sua mensagem. Verifique sua conexão ou tente novamente mais tarde.', 'error');
    } finally {
      setLoading(false);
    }
  }

  /* ── Manipulação de Botão e Spinner ────────────────────────── */
  function setLoading(loading) {
    submitBtn.disabled = loading;
    spinner?.classList.toggle('hidden', !loading);
    submitIcon?.classList.toggle('hidden', loading);
    if (submitText) {
      submitText.textContent = loading ? 'Enviando...' : 'Enviar Mensagem';
    }
  }

  /* ── Validação em Tempo Real ──────────────────────────────── */
  function initRealtimeValidation() {
    Object.keys(validators).forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (!field) return;

      field.addEventListener('blur', () => {
        const error = validators[fieldId](field.value);
        if (error) showError(fieldId, error);
        else clearError(fieldId);
      });

      field.addEventListener('input', () => {
        if (field.classList.contains('is-invalid')) {
          const error = validators[fieldId](field.value);
          if (!error) clearError(fieldId);
        }
      });
    });
  }

  /* ── Copiar E-mail ────────────────────────────────────────── */
  function setupClipboard() {
    if (!copyBtn) return;
    
    copyBtn.addEventListener('click', async () => {
      const emailValue = copyBtn.getAttribute('data-email') || 'carlosdaniel.alves@ifce.edu.br';
      
      try {
        await navigator.clipboard.writeText(emailValue);
        
        // Feedback visual no botão
        const origHtml = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copiado!';
        copyBtn.classList.add('btn-copied');
        showToast('E-mail copiado para a área de transferência! 📋', 'success');
        
        setTimeout(() => {
          copyBtn.innerHTML = origHtml;
          copyBtn.classList.remove('btn-copied');
        }, 3000);
      } catch (err) {
        console.error('Falha ao copiar:', err);
        showToast('Não foi possível copiar automaticamente.', 'error');
      }
    });
  }

  /* ── Toast de Alerta ──────────────────────────────────────── */
  function showToast(message, type = 'success') {
    const existing = document.getElementById('contact-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'contact-toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.style.cssText = `
      position: fixed;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%) translateY(0);
      padding: 0.85rem 1.75rem;
      border-radius: var(--radius-xl);
      font-size: var(--text-sm);
      font-weight: 600;
      color: ${type === 'success' ? '#09090B' : '#fff'};
      background: ${type === 'success' ? 'var(--color-accent)' : '#ef4444'};
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
      border: 1px solid ${type === 'success' ? 'rgba(6, 182, 212, 0.3)' : 'rgba(239, 68, 68, 0.3)'};
      z-index: 10000;
      opacity: 1;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(-50%) translateY(10px)';
      setTimeout(() => toast.remove(), 400);
    }, 4500);
  }

  /* ── Inicialização ────────────────────────────────────────── */
  function init() {
    form.addEventListener('submit', handleSubmit);
    initRealtimeValidation();
    setupLazyLoading();
    setupClipboard();
  }

  return { init };
})();

document.addEventListener('DOMContentLoaded', () => {
  ContactForm.init();
});
