from pathlib import Path

VERSION = "res-v1"
CACHE_VERSION = "20260823a"

INDEX = Path("index.html")
THANK_YOU = Path("thank-you.html")
GP_JS = Path("assets/js/growthproof.js")
GP_TY_JS = Path("assets/js/growthproof-thankyou.js")

INDEX_MARKER = '<script src="assets/js/main.min.js?v=20260730b" defer></script>'
INDEX_TAG = f'<script src="assets/js/growthproof.js?v={CACHE_VERSION}" defer></script>'
THANK_YOU_TAG = f'<script src="assets/js/growthproof-thankyou.js?v={CACHE_VERSION}" defer></script>'

GROWTHPROOF_JS = r'''(() => {
  'use strict';

  const VERSION = 'res-v1';
  const ATTR_KEY = 'svr_gp_first_touch_v1';
  const PENDING_KEY = 'svr_gp_pending_lead_v1';
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

  function loadFirstTouch() {
    try {
      const existing = window.localStorage.getItem(ATTR_KEY);
      if (existing) return JSON.parse(existing);
    } catch (_) {}

    const q = new URLSearchParams(window.location.search);
    const record = {
      landing_path: window.location.pathname || '/',
      referrer_path: safePath(document.referrer),
      captured_at: new Date().toISOString()
    };
    UTM_KEYS.forEach((key) => { record[key] = q.get(key) || ''; });

    try { window.localStorage.setItem(ATTR_KEY, JSON.stringify(record)); } catch (_) {}
    return record;
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
    const fields = Object.assign({}, firstTouch, {
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
        submitted_at: submittedAt
      }));
    } catch (_) {}
  });
})();
'''

GROWTHPROOF_THANK_YOU_JS = r'''(() => {
  'use strict';

  const VERSION = 'res-v1';
  const PENDING_KEY = 'svr_gp_pending_lead_v1';

  let pending;
  try { pending = JSON.parse(window.sessionStorage.getItem(PENDING_KEY) || 'null'); } catch (_) { pending = null; }
  if (!pending || !pending.lead_id) return;

  const sentKey = 'svr_gp_sent_' + pending.lead_id;
  try { if (window.sessionStorage.getItem(sentKey)) return; } catch (_) {}

  if (typeof window.gtag !== 'function') return;
  window.gtag('event', 'generate_lead', {
    measurement_version: VERSION,
    lead_id: pending.lead_id,
    lead_type: 'residential_enquiry',
    service: pending.service || ''
  });

  try {
    window.sessionStorage.setItem(sentKey, '1');
    window.sessionStorage.removeItem(PENDING_KEY);
  } catch (_) {}
})();
'''


def patch_index(text: str) -> str:
    if INDEX_TAG in text:
        return text
    if INDEX_MARKER not in text:
        raise SystemExit(f"Expected index marker missing: {INDEX_MARKER}")
    return text.replace(INDEX_MARKER, INDEX_MARKER + "\n" + INDEX_TAG, 1)


def patch_thank_you(text: str) -> str:
    if THANK_YOU_TAG in text:
        return text
    marker = "</body>"
    if marker not in text:
        raise SystemExit("Expected </body> marker missing from thank-you.html")
    return text.replace(marker, THANK_YOU_TAG + "\n" + marker, 1)


def main() -> None:
    INDEX.write_text(patch_index(INDEX.read_text(encoding="utf-8")), encoding="utf-8")
    THANK_YOU.write_text(patch_thank_you(THANK_YOU.read_text(encoding="utf-8")), encoding="utf-8")
    GP_JS.parent.mkdir(parents=True, exist_ok=True)
    GP_JS.write_text(GROWTHPROOF_JS, encoding="utf-8")
    GP_TY_JS.write_text(GROWTHPROOF_THANK_YOU_JS, encoding="utf-8")


if __name__ == "__main__":
    main()
