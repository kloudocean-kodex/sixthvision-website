
(() => {
  'use strict';

  const VERSION = 'res-v2';
  const ATTR_KEY = 'svr_gp_first_touch_v1';
  const PENDING_KEY = 'svr_gp_pending_lead_v2';
  const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'msclkid'];

  function emit(name, params) {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', name, Object.assign({ measurement_version: VERSION }, params || {}));
  }

  function uuid() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') return window.crypto.randomUUID();
    return 'svr-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 12);
  }

  function safePath(raw) {
    if (!raw) return '';
    try {
      const u = new URL(raw, window.location.origin);
      return u.pathname || '/';
    } catch (_) {
      return '';
    }
  }

  function queryValues(prefix) {
    const q = new URLSearchParams(window.location.search);
    const values = {};
    UTM_KEYS.forEach((key) => { values[prefix + key] = q.get(key) || ''; });
    return values;
  }

  function loadFirstTouch() {
    try {
      const existing = window.localStorage.getItem(ATTR_KEY);
      if (existing) return JSON.parse(existing);
    } catch (_) {}

    const record = Object.assign({
      landing_path: window.location.pathname || '/',
      referrer_path: safePath(document.referrer),
      captured_at: new Date().toISOString()
    }, queryValues(''));

    try { window.localStorage.setItem(ATTR_KEY, JSON.stringify(record)); } catch (_) {}
    return record;
  }

  function captureSubmitTouch() {
    return Object.assign({
      submit_path: window.location.pathname || '/',
      submit_referrer_path: safePath(document.referrer),
      submit_touch_at: new Date().toISOString()
    }, queryValues('submit_'));
  }

  function setHidden(form, name, value) {
    let input = form.querySelector('input[type="hidden"][name="' + name + '"]');
    if (!input) {
      input = document.createElement('input');
      input.type = 'hidden';
      input.name = name;
      form.appendChild(input);
    }
    input.value = value == null ? '' : String(value);
  }

  function ctaLocation(anchor) {
    if (anchor.closest('header')) return 'header';
    if (anchor.closest('footer')) return 'footer';
    if (anchor.closest('#package')) return 'package';
    if (anchor.closest('#contact')) return 'contact';
    if (anchor.classList.contains('wa-float')) return 'floating_whatsapp';
    return 'body';
  }

  const firstTouch = loadFirstTouch();

  document.addEventListener('click', (event) => {
    const anchor = event.target.closest && event.target.closest('a[href]');
    if (!anchor) return;
    const href = String(anchor.getAttribute('href') || '');
    const params = { cta_location: ctaLocation(anchor) };

    if (href.startsWith('tel:')) emit('phone_click', params);
    else if (href.startsWith('mailto:')) emit('email_click', params);
    else if (/^https:\/\/(?:www\.)?wa\.me\//i.test(href)) emit('whatsapp_click', params);
    else if (anchor.hasAttribute('data-commercial-handoff') || /sixthvisioncommercial\.com\.au/i.test(href)) {
      emit('commercial_handoff', Object.assign(params, { destination: 'sixthvisioncommercial.com.au' }));
    }
    else if (href === '#contact' && /book/i.test(anchor.textContent || '')) emit('book_shoot_click', params);
  }, { passive: true });

  const packageSection = document.getElementById('package');
  if (packageSection && 'IntersectionObserver' in window) {
    let packageSeen = false;
    const observer = new IntersectionObserver((entries) => {
      if (packageSeen || !entries.some((entry) => entry.isIntersecting)) return;
      packageSeen = true;
      emit('package_view', { section: 'ultimate_marketing_package' });
      observer.disconnect();
    }, { threshold: 0.35 });
    observer.observe(packageSection);
  }

  const form = document.querySelector('form[action^="https://api.web3forms.com/submit"]');
  if (!form) return;

  let formStarted = false;
  function markFormStart() {
    if (formStarted) return;
    formStarted = true;
    emit('form_start', { form_name: 'residential_enquiry' });
  }
  form.addEventListener('focusin', markFormStart, { once: true });
  form.addEventListener('input', markFormStart, { once: true });

  // A native HTML POST remains in the markup for visitors without JavaScript.
  // With JavaScript enabled, only redirect to thank-you after Web3Forms explicitly
  // confirms delivery. A rejected access key or quota must never look like a lead.
  const submitButton = form.querySelector('button[type="submit"]');
  const originalButtonText = submitButton ? submitButton.textContent : '';
  const resultStatus = document.createElement('p');
  resultStatus.className = 'form-note';
  resultStatus.setAttribute('role', 'status');
  resultStatus.setAttribute('aria-live', 'polite');
  if (submitButton) submitButton.insertAdjacentElement('afterend', resultStatus);
  else form.appendChild(resultStatus);

  let sending = false;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (sending) return;
    sending = true;

    const leadId = uuid();
    const submittedAt = new Date().toISOString();
    const submitTouch = captureSubmitTouch();
    const fields = Object.assign({}, firstTouch, submitTouch, {
      attribution_model: 'first_and_submit_touch_v2',
      growthproof_measurement_version: VERSION,
      lead_id: leadId,
      submitted_at: submittedAt
    });
    Object.keys(fields).forEach((key) => setHidden(form, key, fields[key]));

    let service = '';
    const serviceField = form.elements && form.elements.service;
    if (serviceField) service = String(serviceField.value || '');

    try {
      window.sessionStorage.setItem(PENDING_KEY, JSON.stringify({
        lead_id: leadId,
        service: service,
        submitted_at: submittedAt,
        attribution_model: 'first_and_submit_touch_v2'
      }));
    } catch (_) {}

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = 'Sending enquiry…';
    }
    resultStatus.textContent = 'Sending your enquiry…';

    try {
      const payload = Object.fromEntries(new FormData(form).entries());
      // redirect is for the non-JavaScript HTML fallback only. Including it
      // in an AJAX request may produce a 303/CORS redirect instead of JSON.
      delete payload.redirect;
      const response = await window.fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok || !data || data.success !== true) {
        throw new Error('The form provider did not confirm the enquiry');
      }

      resultStatus.textContent = 'Enquiry received. Opening confirmation…';
      // The conversion event is emitted only by the existing one-shot thank-you bridge.
      window.location.assign('https://sixthvision.com.au/thank-you.html');
    } catch (_) {
      // Never let a failed submission be counted via a stale pending lead ID.
      try {
        const saved = JSON.parse(window.sessionStorage.getItem(PENDING_KEY) || 'null');
        if (saved && saved.lead_id === leadId) {
          window.sessionStorage.removeItem(PENDING_KEY);
        }
      } catch (_) {}
      resultStatus.textContent = 'Your enquiry was not confirmed. Please call 0474 126 276 or email sixthvision.mel@gmail.com, or try again.';
      emit('form_submit_failed', { form_name: 'residential_enquiry' });
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
      }
      sending = false;
    }
  });
})();
