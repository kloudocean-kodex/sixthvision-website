from pathlib import Path

INDEX = Path('index.html').read_text(encoding='utf-8')
THANK_YOU = Path('thank-you.html').read_text(encoding='utf-8')
HEADERS = Path('_headers').read_text(encoding='utf-8')
GP = Path('assets/js/growthproof.js').read_text(encoding='utf-8')
GP_TY = Path('assets/js/growthproof-thankyou.js').read_text(encoding='utf-8')


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# Production identity / analytics must remain unchanged.
require('https://sixthvision.com.au/' in INDEX, 'Canonical production URL missing')
require("gtag('config', 'G-M6TSWTEBM9')" in INDEX, 'Residential GA4 Measurement ID changed/missing in index')
require("gtag('config', 'G-M6TSWTEBM9')" in THANK_YOU, 'Residential GA4 Measurement ID changed/missing in thank-you')
require('https://api.web3forms.com/submit' in INDEX, 'Web3Forms endpoint missing')
require('0199e0dd-f927-4e59-be72-0d81767878f0' in INDEX, 'Web3Forms access key changed/missing')
require('https://sixthvision.com.au/thank-you.html' in INDEX, 'Web3Forms success redirect changed/missing')

# GrowthProof scripts must be wired once with the current immutable cache version.
require(INDEX.count('assets/js/growthproof.js?v=20260824b') == 1, 'GrowthProof index v2 script missing/duplicated')
require(THANK_YOU.count('assets/js/growthproof-thankyou.js?v=20260824b') == 1, 'GrowthProof thank-you v2 script missing/duplicated')
require('growthproof.js?v=20260823a' not in INDEX, 'Stale GrowthProof index cache version remains')
require('growthproof-thankyou.js?v=20260823a' not in THANK_YOU, 'Stale GrowthProof thank-you cache version remains')
require("const VERSION = 'res-v2'" in GP and "const VERSION = 'res-v2'" in GP_TY, 'Residential measurement version is not res-v2')

# Expected funnel/intent telemetry.
for event in ['phone_click', 'email_click', 'whatsapp_click', 'book_shoot_click', 'package_view', 'form_start']:
    require(event in GP, f'Missing event: {event}')
require('generate_lead' not in GP, 'generate_lead must not fire before Web3Forms success redirect')
require("gtag('event', 'generate_lead'" in GP_TY, 'generate_lead missing from successful thank-you flow')
require("lead_type: 'residential_enquiry'" in GP_TY, 'Residential lead type missing')
require("send_to: DESTINATION" in GP_TY and "const DESTINATION = 'G-M6TSWTEBM9'" in GP_TY, 'Lead event is not pinned to the Residential GA4 destination')
require('window.setTimeout(() => send(attempt + 1), 100)' in GP_TY, 'Lead-event gtag readiness retry missing')

# First-touch attribution remains immutable and submit-touch is captured separately.
for field in ['landing_path', 'referrer_path', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'msclkid', 'captured_at']:
    require(field in GP, f'Missing first-touch attribution field: {field}')
for field in ['submit_path', 'submit_referrer_path', 'submit_touch_at', 'submit_utm_source', 'submit_utm_medium', 'submit_utm_campaign', 'submit_utm_term', 'submit_utm_content', 'submit_gclid', 'submit_msclkid']:
    require(field in GP, f'Missing submit-touch attribution field: {field}')
for field in ['attribution_model', 'growthproof_measurement_version', 'lead_id', 'submitted_at']:
    require(field in GP, f'Missing GrowthProof evidence field: {field}')
require("attribution_model: 'first_and_submit_touch_v2'" in GP, 'Dual-touch attribution model marker missing')

# Privacy guard: GrowthProof telemetry must not read/send user-entered PII fields.
for forbidden in ['elements.name', 'elements.email', 'elements.phone', 'elements.agency', "getElementById('f-name')", "getElementById('f-email')", "getElementById('f-phone')", "getElementById('f-agency')", "getElementById('f-msg')"]:
    require(forbidden not in GP and forbidden not in GP_TY, f'PII access pattern forbidden: {forbidden}')

# Lead event must be one-shot and support in-flight v1 submissions during deployment.
require('svr_gp_pending_lead_v2' in GP and 'svr_gp_pending_lead_v2' in GP_TY, 'v2 pending lead bridge missing')
require('svr_gp_pending_lead_v1' in GP_TY, 'v1 in-flight pending lead compatibility missing')
require('svr_gp_sent_' in GP_TY, 'Duplicate lead-event guard missing')
require('PENDING_KEYS.forEach' in GP_TY, 'Pending lead cleanup missing')

# Attribution storage is limited to explicit campaign identifiers and safe paths.
require("const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'msclkid']" in GP, 'Known attribution allow-list changed')
require('document.referrer' in GP and 'return u.pathname' in GP, 'Referrer must be reduced to path, not stored wholesale')
require("const ATTR_KEY = 'svr_gp_first_touch_v1'" in GP, 'First-touch continuity key changed unexpectedly')

# Google Tag collection endpoints used by the current GA4 bootstrap must be allowed by CSP.
require('connect-src' in HEADERS, 'CSP connect-src directive missing')
require('https://stats.g.doubleclick.net' in HEADERS, 'Google Tag stats.g.doubleclick.net endpoint missing from CSP connect-src')

print('GrowthProof residential regression gates passed')
