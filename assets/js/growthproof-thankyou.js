(() => {
  'use strict';

  const VERSION = 'res-v2';
  const DESTINATION = 'G-M6TSWTEBM9';
  const PENDING_KEYS = ['svr_gp_pending_lead_v2', 'svr_gp_pending_lead_v1'];

  let pending = null;
  let pendingKey = '';
  for (const key of PENDING_KEYS) {
    try {
      const candidate = JSON.parse(window.sessionStorage.getItem(key) || 'null');
      if (candidate && candidate.lead_id) {
        pending = candidate;
        pendingKey = key;
        break;
      }
    } catch (_) {}
  }
  if (!pending || !pending.lead_id) return;

  const sentKey = 'svr_gp_sent_' + pending.lead_id;
  try { if (window.sessionStorage.getItem(sentKey)) return; } catch (_) {}

  function finalize() {
    try {
      window.sessionStorage.setItem(sentKey, '1');
      if (pendingKey) window.sessionStorage.removeItem(pendingKey);
      PENDING_KEYS.forEach((key) => window.sessionStorage.removeItem(key));
    } catch (_) {}
  }

  function send(attempt) {
    if (typeof window.gtag === 'function') {
      window.gtag('event', 'generate_lead', {
        send_to: DESTINATION,
        measurement_version: VERSION,
        lead_id: pending.lead_id,
        lead_type: 'residential_enquiry',
        service: pending.service || '',
        attribution_model: pending.attribution_model || 'legacy_first_touch_v1'
      });
      finalize();
      return;
    }
    if (attempt < 50) window.setTimeout(() => send(attempt + 1), 100);
  }

  send(0);
})();
