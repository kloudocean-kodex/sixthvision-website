# Sixth Vision — Phase Two demo homepage (sixthvision-final — CANONICAL)

This `sixthvision-final` folder is the **current, definitive build** (all earlier folders removed).
A self-contained static site. **Deploy:** drag this whole folder onto https://app.netlify.com/drop — done.
No build step, no dependencies. The enquiry form is Netlify-Forms-ready (submissions appear in the
Netlify dashboard under "Forms" once deployed; it posts to `/thank-you.html`).

## Final round (2026-07-16) — owner feedback applied
- **SEO**: "Real Estate Photography / Videography Melbourne" woven naturally ~34× across copy, alt
  text, captions and reviews.
- **Virtual Staging** section added — a second before/after drag slider (empty → digitally furnished),
  below the editing "craft" slider.
- **"Preston" removed** everywhere (topbar, hero, testimonial, contact, footer, JSON-LD) — Melbourne only.
- **Portfolio grid** rebuilt as a uniform 3:2 grid (12 images, 3 cols desktop / 2 mobile) — the old
  masonry's blank bottom-right corner is gone; it now tiles perfectly.
- **Mobile fixes**: review stars constrained to 16px (they were ballooning); the Book/Shoot/Deliver
  "how it works" steps now centre correctly (were left-aligned).
- **Email** `sixthvision.mel@gmail.com` added to the contact panel and footer (+ topbar/footer envelope
  icons now open mail).
- **Image replacements** (owner's picks): Twilight & Dusk service card → two-storey dusk (`451A4204`);
  gallery Bathroom → blue-mosaic ensuite (`Photos_40_sample/5.jpg`); gallery Dusk exterior → `80.JPG`;
  three fills added (skillion `6.jpg`, living `78.jpg`, Hamptons `451A6233`). Sources: `demo-assets\Photo`
  and `Photos_40_sample`; staging pair from `Downloads\Staging` (`1G3A0645` / `_final`).
- **Working lightbox** — the gallery's click-to-enlarge viewer (with prev/next + keyboard) was in the
  markup but had no JS; it now works.
- **Performance**: CSS & JS minified to `styles.min.css` / `main.min.js` (referenced by the HTML;
  edit the readable `styles.css` / `main.js` sources, then re-run the minify step). Cache-busted with
  `?v=`. Images already WebP + lazy + sized; fonts preloaded; JS deferred.

## Follow-up tweaks (2026-07-16, same day)
- **Videography card** → now the styled home-office / study (`Photos_40_sample\38.jpg`, the "Replace 1"
  you pointed to).
- **Twilight & Dusk card** → re-cropped less tight so the whole two-storey house reads (was `451A4204`,
  centred lower). Note: service cards are 3:4 portraits, so a wide house is always framed a little
  closely — the full-width house lives in the gallery/lightbox.
- **Virtual Staging** → swapped to the more elegant boucle-chair open-plan pair (`Staging\1G3A0657.jpg`
  / `_final`). Still his own work (not stock) — authentic for a photographer's staging service.
- **Testimonials enriched** → the reviews now sit in soft "glass" cards: warm gradient surface, a
  luminous gold hairline along the top, a ghosted oversized quote glyph, layered depth-shadow that lifts
  on hover, on a blush-tinted band. Quiet-luxury, on-theme.

## Notes for your review
- **Craft before/after** slider is unchanged (you loved it). It's still a *simulated* grade — swap in a
  real raw+edited pair before go-live if you have one.
- Assets use immutable caching (`_headers`). This build is normally deployed fresh (new Netlify URL), so
  visitors always get the latest. If you ever redeploy over the *same* domain, do a hard refresh to bust
  cached images.

## SESSION HANDOFF — everything needed to resume (read this first)

**Canonical build:** `C:\Users\gawar\Downloads\sixthvision-final\` (this folder). All older build folders
(`sixthvision-v2`, `sixthvision-v3-ENHANCED`, `sixthvision-demos`) were deleted. Left alone:
`sixthvision-backup` (679 MB, owner's safety net), `sixthvision-v2-ENHANCED` (20 MB, unknown, no index),
`sixthvision-website` (the separate live-WordPress repo).

**Preview locally:** `.claude/launch.json` (in Downloads) runs it on **port 8130**
(`python -m http.server 8130 --directory ...\sixthvision-final`). Deploy = drag the folder onto Netlify Drop.

**Editing CSS/JS:** the HTML links `assets/css/styles.min.css` + `assets/js/main.min.js`. Edit the readable
sources `styles.css` / `main.js`, then run `python C:\Users\gawar\Downloads\sixthvision-final-minify.py`
and bump the `?v=` version in `index.html` + `thank-you.html`. Current version: **`v=20260717a`**.

**Latest visual polish (v=…d):** the feature photos (intro interior, showreel, editing before/after,
virtual staging) now read as *framed gallery prints* — a soft warm radial halo behind each section, a fine
gold hairline frame on the sliders, a gold inner-ring on the intro photo, and a deeper "floating print"
shadow. Implemented purely in CSS via `:has()` (bottom of `styles.css`), no markup changes.

**Owner's source-asset folders (in Downloads):**
- `demo-assets\Photo\` — the original 109 pro photos, numbered (`80.JPG`, `9.jpg`, `12-1.jpg`…).
- `Photos_40_sample\` — 40 curated samples incl. the `451A*` hero shots. ⚠ Note `38.jpg` here is a STUDY
  (used for the videography card); `demo-assets\Photo\38.jpg` is a different FACADE.
- `Staging\` — virtual-staging before/after pairs (`NAME.jpg` empty + `NAME_final.JPEG/.jpg` staged):
  `1G3A0645`, `1G3A0657` (in use), `DSC_5054` (bedroom), `_DSC6677` (double-height).
- `Logo\` — agency logos. `SV Social media\Video\` — listing films. `reference-sites\` — Sawyer etc.
- `replacement_suggestions\` + `screenshots_replacement suggestions\` — the owner's WhatsApp replacement pics.

**Image → source map (what's live in `assets/img/`, and where it came from):**
| Slot | File(s) in assets/img | Source |
|---|---|---|
| Hero (active) | `hero-placeholder-*` | owner's chosen stock interior (real twilight kept as `hero-twilight-*` to swap) |
| Intro spread | `intro-photo-*` | owner's living-room (image #2 of taste paste) |
| Card · Photography | `card-photography-*` | `demo-assets\Photo\24.jpg` |
| Card · Videography | `card-video-*` | `Photos_40_sample\38.jpg` (study) |
| Card · Drone | `card-drone-*` | `demo-assets\Photo\5.jpg` (aerial) |
| Card · Twilight | `card-twilight-*` | `Photos_40_sample\451A4204.jpg` (two-storey dusk) |
| Card · Floor Plans | `card-floorplan-*` | `demo-assets\Floor Plan\Floor plan 02.jpg` |
| Card · Virtual Tours | `card-tour-*` | `demo-assets\Photo\39.jpg` |
| Gallery (12, 3:2) | `gal-{dusk,kitchen,facade,bedroom,dining,bath,stair,court,alfresco,skillion,living,hamptons}-*` | Photo: `80.JPG,9,29,12-1,70,81,65,44,6,78`; Sample: bath=`5.jpg`, hamptons=`451A6233.jpg` |
| Craft slider | `placeholder-before/after-1600` | simulated grade (needs a real raw+edited pair) |
| Staging slider | `staging-before/after-1600` | `Staging\1G3A0657.jpg` + `_final.JPEG` |
| Drone band | `drone-band-*` | `demo-assets\Photo\5.jpg` |
| Showreel poster | `showreel-*` | `demo-assets\Photo\34.jpg`; video `assets/video/showreel.mp4` = 63 French Rd Greenvale (17 MB) |
| Logos | `logos/logo-*` | normalised from `Downloads\Logo` (Ray White chroma-keyed; Woodards = text wordmark, still no file) |

**Environment quirk:** the in-app Browser preview pane's **screenshots + scrolling freeze** in these
sessions (verified this build via DOM/computed-style/functional JS tests instead — all passed). Not a site bug.

**Still pending / owner's call:** real raw+edited pair for the craft slider · confirm YouTube URL
(`@sixthvision86`) · Woodards logo file · verify `$650/$1,250` pricing · OG/JSON-LD point at
sixthvision.com.au (correct after cutover).

## Earlier round (2026-07-14)
- **Masthead**: brand left · **nav right-aligned** (mirrors the topbar cluster, Sawyer-style).
- **Warm espresso footer** — a deep, textured close that makes the gold wordmark + hairline sing.
  (Revert to the light textured footer via the token note atop `.site-footer` in `styles.css`.)
- **Gold top-border on the Guarantee cards** (mirrors the offer card) + they lift on hover.
- **24hr / 100% guarantee figures now count up** on scroll, like the stat band. The reveal +
  count-up code has a scroll/load/timeout fallback so nothing can stay hidden or stuck at zero.
- **Brand emblem** to the left of "Sixth Vision": a hairline-gold house mark (roof, chimney,
  mullioned window) echoing his real logo.
- **Editorial intro** is now a **full-width landscape photograph** (his chosen living room) with an
  italic serif caption — matching the drone-band treatment he liked.
- **Service cards**: translucent frosted labels (Sawyer-style), softer and more elegant.
- **Footer** now sits on a warm textured plaster (`footer-texture.webp`) with a gold hairline.
- **Twilight & Dusk card** re-cropped so the whole house reads (roof to garden).
- Sitewide **paper grain** so the ivory tints read as textured stock, not flat colour.
- Social icons (Instagram · YouTube · WhatsApp · Facebook) in the topbar and footer.

## What's inside

- `index.html` — the long-scroll homepage (one H1, OpenGraph, LocalBusiness JSON-LD).
- `thank-you.html` — form success page.
- `design-system.html` — internal style guide (noindex; the display-serif trial that picked Cormorant Garamond).
- `assets/img/` — all photography is the owner's real delivered work, optimised to WebP.
- `assets/img/logos/` — agency logos normalised from `Downloads\Logo` (Ray White's yellow tile was
  chroma-keyed to a wordmark; Harcourts & Professionals recoloured from white-only variants; Woodards
  had no file, so it runs as a styled text wordmark in the marquee).
- `assets/video/showreel.mp4` — 63 French Road Greenvale, transcoded 1080p H.264 (~17 MB) from the
  140 MB original (Netlify's limit is 100 MB/file). Loads only when the play button is clicked.
- `assets/fonts/` — self-hosted: Cormorant Garamond (display), Jost (body). Playfair/Marcellus files
  remain for the specimen page only; browsers never download unused faces.

## Before cutover to sixthvision.com.au

1. **Hero** is the owner's chosen editorial interior (`hero-placeholder-*.webp`). For a photographer's
   flagship I'd recommend opening on his OWN twilight-exterior craft — the real frame is already in the
   folder as `hero-twilight-*.webp`; switch by swapping `hero-placeholder` → `hero-twilight` in the three
   filenames in `index.html`'s hero `<picture>` (and the two `<link rel=preload>` lines in `<head>`).
2. Swap `assets/img/placeholder-before-1600.webp` / `placeholder-after-1600.webp` with a REAL
   raw+edited pair (the "before" is currently a simulated flat grade of the same finished frame).
3. Confirm the $650 / $1,250 package pricing (taken from the live site's updated banner).
4. Stats used: 50,000+ properties · 60+ agencies · 400+ agents · 500 shoots/month (owner-supplied).
5. OG image URL and JSON-LD point at `https://sixthvision.com.au/` — correct after cutover; link
   previews from a temporary Netlify URL will not resolve the OG image until then.
6. Woodards still needs a logo file (runs as a text wordmark in the marquee meanwhile).
