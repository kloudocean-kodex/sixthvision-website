# Changelog — 30 July 2026

Full reasoning for every item is in `AUDIT-2026-07-30.md`.

## Added — client request (Ankkush)
- **Price card now lists the four services**: Photography · Floor plan · Drone · Cinematic video.
  Rendered as a 2×2 grid of gold line-icons under an `Included` micro-label, between the `$650`
  and the Google rating. Icons are drawn at the same 24-unit viewBox / 1.4 stroke as every other
  glyph on the page; labels use the existing `Jost 500 / uppercase / wide-tracking` utility
  register already used by `.eyebrow` and `.lightbox-caption`. No new tokens, no new typeface,
  no new colour. Collapses to a single column below 400 px.

## Fixed — correctness
- `_redirects`: 22 rules pointed at `/#light`, `/#measure`, `/#close` — none of which exist.
  Rewritten to 49 rules; every `/#` target now machine-verified against the ids in `index.html`.
- `robots.txt`: removed `Disallow` on pages that also carry `noindex` (the two cancel out).
- `design-system.html`: added `noindex, nofollow` — it was publicly reachable and unmarked.
- `<img class="lightbox-img" src="">`: empty `src` removed; intrinsic `1200×800` added.
- Cache-bust versions unified across all pages at `?v=20260730`.
- `sitemap.xml`: `lastmod` refreshed.

## Fixed — performance
- Scroll handling rewritten: one shared rAF batch, self-retiring jobs, listener removed when
  the queue empties. Was: `getBoundingClientRect()` on ~50 elements per scroll event, forever.
- `body::after` paper grain: dropped full-viewport `mix-blend-mode` compositing.
- Trust marquee: infinite animation now pauses while off screen.
- `will-change` on the drone band applied only while it is being parallaxed.
- Removed `text-rendering: optimizeLegibility`.
- Header `is-solid` class write guarded by state comparison.
- **60 AVIF variants generated** — content images 4,724 KB → 2,566 KB (−45.7 %).
- **New 800 w mobile hero** — LCP image 124.5 KB → 51.7 KB (−58 %).
- `<link rel=preload>` for the hero now carries `type="image/avif"`.
- Metric-matched fallback faces for Cormorant and Jost, measured from the shipped woff2 files.
- Removed Playfair Display + Marcellus (never rendered): fonts 322 KB → 216 KB.
- GA deferred on `404.html` and `thank-you.html` to match `index.html`.

## Fixed — accessibility
- Focus trap + `inert` background for the lightbox; Escape already worked, now scoped correctly.
- Mobile drawer: Escape to close, focus trap, focus returned to the toggle, and recovery when
  the viewport crosses the 881 px breakpoint while open.
- Visible focus ring on the before/after slider handles (the range input is `opacity: 0`).
- Focus moved to the `<video>` when the showreel play button is removed.
- `aria-live="polite"` on the lightbox counter.
- `overscroll-behavior: contain` on the lightbox.

## Added — structured data & meta
- `makesOffer` for the $650 package (price, currency, availability, the four services).
- `VideoObject` for the showreel.
- `theme-color`, `og:image:alt`, `color-scheme: light only`.
- `frame-ancestors 'self'`, `Cross-Origin-Opener-Policy`, `X-DNS-Prefetch-Control` in `_headers`.
- SHA-256 hash of the inline GA script documented in `_headers` as a *commented* CSP upgrade.

## Removed
- `assets/fonts/playfairdisplay-{400,500,400-italic}.woff2`, `assets/fonts/marcellus-400.woff2`
- Two re-encoded video attempts — both were worse than the original. See audit §4.

## Not done, on purpose
Critical-CSS inlining · `aggregateRating` schema · `FAQPage` schema · live hashed CSP ·
AVIF for the alpha logos. Each is explained in audit §5 — these are decisions, not omissions.

---

## Review pass before push — corrections to the above

Three items listed above were not actually delivered by the shipped files and are now fixed.
Full detail and measurements in `AUDIT-2026-07-30.md` §9.

### Fixed — defects in this bundle
- **Lightbox was unusable when open.** `inert` was applied to `#main`, which *contained*
  `#lightbox`, so the dialog inerted itself: the close button could not take focus and clicks on
  it landed on the header behind. Escape was the only way out — nothing at all on touch.
  The dialog is now a sibling of header/main/footer; `inert` goes on every body-level sibling
  (six elements — the hand-listed pair missed the skip link, `.topbar` and `.wa-float`); and the
  `visibility` transition, a discrete property that flipped at 50% and left the dialog hidden for
  200 ms, now flips immediately on open and defers only on close.
- **AVIF was never served.** 21 of 28 `<source type="image/avif">` had `.webp`-only srcsets, so
  only 10 of the 62 encodes were reachable. Repointed against files verified on disk —
  now 50 of 62 reachable, 26 images confirmed rendering AVIF in-browser.
- **Hero LCP was a regression.** A `<picture>` nested inside a `<picture>` orphaned both mobile
  `media` rules; mobile served `1600.webp` (177 KB) plus a discarded 51 KB AVIF preload, against
  124 KB on live. Un-nested — mobile now serves `hero-placeholder-800.avif` at **51 KB**, which is
  the −58 % the audit claimed.

### Fixed — follow-on
- **Cache-bust bumped to `?v=20260730b`.** Both minified assets changed but every page was left on
  `?v=20260730`, the same token the previous CSS/JS shipped under. Under
  `/assets/* immutable, max-age=31536000` returning visitors would have kept the old files —
  including the old lightbox JS — for a year.
- `readme.md`: the note claiming the Playfair/Marcellus files "remain for the specimen page" was
  stale once they were deleted; rewritten, and the metric-matched fallbacks documented.
- `design-system.html`: the Playfair Display and Marcellus type specimens were removed. Their
  `.woff2` files are gone, so both blocks had silently been rendering in a fallback serif while
  labelled as those faces.

### Recorded — an improvement this bundle made without noting it
- `cormorantgaramond-400-italic.woff2` had been shipping in the repo with **no `@font-face`
  declaring it**. Every italic serif — `.hero h1 em` and the testimonial pull-quotes — was
  rendering in Georgia italic at full size, ~27 % wider than intended. This pass added the missing
  declaration. That is the only reason the diff moves any layout: testimonials are 71 px shorter
  because a quote wraps one line fewer, and the page is 70 px shorter. Every other section
  measured pixel-identical to live, and nothing is clipped.

### Corrected in the audit text
- The claim that `design-system.html` had "no robots directive at all" and now carries
  `noindex, nofollow` was wrong on both counts: it already had `noindex`, it still has exactly
  that, and the file was not modified. See §2 of the audit, corrected in place.

### Line endings
The repo is CRLF throughout. The delivered bundle was LF, which would have rewritten every line
of every text file and destroyed `git blame`. Re-normalised to CRLF so this commit contains only
real content changes.
