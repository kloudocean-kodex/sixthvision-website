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

  form.addEventListener('submit', () => {
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
  });
})();
