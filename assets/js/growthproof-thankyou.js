(() => {
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
