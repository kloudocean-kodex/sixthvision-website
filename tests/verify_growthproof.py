from pathlib import Path

INDEX = Path('index.html').read_text(encoding='utf-8')
THANK_YOU = Path('thank-you.html').read_text(encoding='utf-8')
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

# GrowthProof scripts must be wired once.
require(INDEX.count('assets/js/growthproof.js?v=20260823a') == 1, 'GrowthProof index script missing/duplicated')
require(THANK_YOU.count('assets/js/growthproof-thankyou.js?v=20260823a') == 1, 'GrowthProof thank-you script missing/duplicated')

# Expected funnel/intent telemetry.
for event in ['phone_click', 'email_click', 'whatsapp_click', 'book_shoot_click', 'package_view', 'form_start']:
    require(event in GP, f'Missing event: {event}')
require('generate_lead' not in GP, 'generate_lead must not fire before Web3Forms success redirect')
require("gtag('event', 'generate_lead'" in GP_TY, 'generate_lead missing from successful thank-you flow')
require("lead_type: 'residential_enquiry'" in GP_TY, 'Residential lead type missing')

# Attribution evidence expected in the Web3Forms email.
for field in ['landing_path', 'referrer_path', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'msclkid', 'captured_at', 'growthproof_measurement_version', 'lead_id', 'submitted_at']:
    require(field in GP, f'Missing attribution field: {field}')

# Privacy guard: GrowthProof telemetry must not read/send user-entered PII fields.
for forbidden in ['elements.name', 'elements.email', 'elements.phone', 'elements.agency', "getElementById('f-name')", "getElementById('f-email')", "getElementById('f-phone')", "getElementById('f-agency')", "getElementById('f-msg')"]:
    require(forbidden not in GP and forbidden not in GP_TY, f'PII access pattern forbidden: {forbidden}')

# Lead event must be one-shot and backed by a pending lead created before submit navigation.
require('svr_gp_pending_lead_v1' in GP and 'svr_gp_pending_lead_v1' in GP_TY, 'Pending lead bridge missing')
require('svr_gp_sent_' in GP_TY, 'Duplicate lead-event guard missing')
require('sessionStorage.removeItem(PENDING_KEY)' in GP_TY, 'Pending lead cleanup missing')

# First-touch storage only records explicit campaign identifiers + safe paths.
require("const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'msclkid']" in GP, 'Known attribution allow-list changed')
require('document.referrer' in GP and 'return u.pathname' in GP, 'Referrer must be reduced to path, not stored wholesale')

print('GrowthProof residential regression gates passed')
