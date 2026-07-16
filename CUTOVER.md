# Sixth Vision — Go-Live / Cutover Plan

Static site in this folder → live at **https://sixthvision.com.au**. Written 2026-07-16.
Do the steps top-to-bottom. Nothing here needs code skills beyond copy-paste.

---

## 0. Readiness verdict — YES, you can cut over

Technically production-ready: semantic HTML, one `<h1>`, full meta + OpenGraph + LocalBusiness JSON-LD,
canonical tag, WebP + lazy + sized images (no layout shift), self-hosted preloaded fonts, minified +
cache-busted CSS/JS, working form/lightbox/sliders, mobile-clean, no console errors, robots.txt +
sitemap.xml + 404.html now included.

**Optional finalizations (polish, NOT blockers) — decide before or soon after launch:**
- [ ] **Hero image** is a chosen stock interior (`hero-placeholder-*`). His own twilight-exterior craft is
      ready as `hero-twilight-*` — swap the 3 filenames in the hero `<picture>` + the 2 `<link rel=preload>`
      lines if you'd rather open on real work (recommended for a photographer, but your call).
- [ ] **Craft before/after** slider uses a *simulated* grade. Swap `placeholder-before/after-1600.webp`
      for a real raw+edited pair when you have one.
- [ ] **Confirm pricing** ($650, was $1,250) still current.
- [ ] **Confirm YouTube URL** — currently `https://www.youtube.com/@sixthvision86` (used in footer + contact).
- [ ] **Woodards** shows as a text wordmark in the logo marquee (no logo file was supplied). Drop a PNG/SVG
      into `assets/img/logos/` and swap it in when you have it.

---

## 1. Put the code on GitHub (source of truth)

1. Create a free GitHub account (if none) → **New repository** → name `sixthvision-site`, **Private**, no README.
2. Upload this whole `sixthvision-final` folder's **contents** (not the folder itself):
   - Easiest: on the empty repo page click **"uploading an existing file"**, drag in everything inside
     `sixthvision-final` (index.html, 404.html, robots.txt, sitemap.xml, assets/, etc.), Commit.
   - Do NOT upload `readme.md`/`CUTOVER.md` publicly if you prefer — harmless either way (not linked).
   - The `.min.css`/`.min.js` files ARE needed (the HTML links them). Keep both source and min.

That's it — GitHub now holds the site. Every future edit = re-upload/commit the changed file.

---

## 2. Deploy — pick ONE host

### ⭐ Option A (recommended): GitHub → Cloudflare Pages  (fast global edge, free, HTTPS auto)
1. Free account at **dash.cloudflare.com** → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Authorize GitHub, pick `sixthvision-site`.
3. Build settings: **Framework preset = None**, **Build command = (blank)**, **Output directory = /** (root).
   (This is a plain static site — no build step.)
4. **Save and Deploy.** In ~1 min you get `https://sixthvision-site.pages.dev` — test it.
5. ⚠ **The contact form needs a service on Cloudflare** — see §3.

### Option B (simplest for the form): GitHub → Netlify  (form works with ZERO config)
1. Free account at **app.netlify.com** → **Add new site → Import from GitHub** → pick the repo.
2. Build command blank, publish directory `/`. Deploy → `https://<name>.netlify.app`.
3. The form already has `data-netlify="true"` → submissions appear under **Forms** in the Netlify dashboard.
   Add a notification email: Netlify → Forms → Settings → form notifications → your email. **Nothing else to do.**
4. Fastest to a working site+form. Cloudflare Pages (A) is a touch faster/CDN-nicer but needs §3.

> Quick-and-dirty test with no Git at all: drag the `sixthvision-final` folder onto **app.netlify.com/drop**
> — instant preview URL (form works). Good for showing the client; use A or B for the real domain.

---

## 3. Contact form on Cloudflare Pages (skip if you chose Netlify)

Netlify Forms only work on Netlify. On Cloudflare Pages, wire a free form service — **Web3Forms** is easiest:

1. Go to **web3forms.com** → enter `sixthvision.mel@gmail.com` → they email you an **Access Key** (no account).
2. In `index.html`, find `<form class="reveal" name="enquiry" ... data-netlify="true" ...>` and change it to:
   ```html
   <form class="reveal" action="https://api.web3forms.com/submit" method="POST">
     <input type="hidden" name="access_key" value="YOUR-ACCESS-KEY-HERE">
     <input type="hidden" name="subject" value="New enquiry — Sixth Vision">
     <input type="hidden" name="redirect" value="https://sixthvision.com.au/thank-you.html">
   ```
   (Delete the old `data-netlify`, `netlify-honeypot`, and the hidden `form-name` input. Keep the honeypot
   `company` field — Web3Forms uses a field named `botcheck`; you can rename the honeypot input to `botcheck`.)
3. Re-upload `index.html` to GitHub. Test: submit → email arrives → lands on thank-you page. Free tier = 250/mo.

(Alternatives: **Formspree.io** — similar; or Cloudflare Pages Functions if you want fully in-house.)

---

## 4. Point sixthvision.com.au at the new site

> ⚠ This REPLACES the current WordPress site on that domain. Make sure you (a) have DNS access for
> sixthvision.com.au, and (b) are OK taking the old WP site down. Given the GoDaddy account history,
> confirm you can log in to DNS management first. Keep the WP site/backup until the new one is verified.

**Best-practice route (Cloudflare Pages + Cloudflare DNS):**
1. In Cloudflare dashboard → **Add a site** → `sixthvision.com.au` → Free plan.
2. Cloudflare scans existing DNS records. **CRITICAL: check that all current records copy over** — especially
   any **MX** (email) and **TXT/SPF/DKIM** records, so email/verification don't break. Add any it missed.
3. Cloudflare gives you 2 **nameservers** → set them at your domain registrar (GoDaddy) replacing the current
   ones. Propagation ~1–24h.
4. Cloudflare → **Workers & Pages** → your Pages project → **Custom domains** → add `sixthvision.com.au`
   **and** `www.sixthvision.com.au` → it auto-creates the DNS + SSL. Set one to redirect to the other
   (use apex `sixthvision.com.au` as primary; redirect www → apex).
5. Wait for SSL "Active" (green). Visit `https://sixthvision.com.au` — you should see the new site with HTTPS.

**If you keep DNS at GoDaddy instead** (no nameserver change): in GoDaddy DNS, point the domain to Pages via
the CNAME/records Cloudflare Pages shows under Custom Domains (apex needs `CNAME flattening`/`ALIAS`, or use
Netlify which provides apex A-records). Nameserver route above is cleaner — do that.

**HTTPS:** automatic on both Cloudflare Pages and Netlify — no cert to buy. Force HTTPS (both have a toggle).

---

## 5. SEO essentials — already done vs. to verify

**Already in the build:** `<title>` + meta description, canonical, OpenGraph + Twitter card, LocalBusiness +
WebSite JSON-LD (schema.org), one H1, descriptive alt text, keyword phrasing, `robots.txt`, `sitemap.xml`,
`404.html`, `og.jpg` share image, `favicon.svg`, mobile viewport, fast Core Web Vitals.

**After the domain is live, verify/submit:**
- [ ] Open `https://sixthvision.com.au/robots.txt` and `/sitemap.xml` — both should load.
- [ ] **Rich Results Test** (search.google.com/test/rich-results) — paste the URL → LocalBusiness should validate.
- [ ] **Mobile-Friendly / PageSpeed Insights** (pagespeed.web.dev) — target 90+ mobile, 95+ desktop.
- [ ] (Nice-to-have) add `apple-touch-icon.png` (180×180) + `favicon.ico` for older browsers — optional.

---

## 6. Google Analytics 4 (GA4)

1. **analytics.google.com** → Admin → **Create** → Account → Property "Sixth Vision" → set **Australia /
   AUD / Australia timezone** → **Web** data stream for `https://sixthvision.com.au`.
2. Copy the **Measurement ID** (looks like `G-XXXXXXXXXX`).
3. Paste this **immediately before `</head>`** in `index.html`, `thank-you.html`, `404.html` (replace the ID):
   ```html
   <!-- Google Analytics 4 -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX');
   </script>
   ```
4. Re-upload the files to GitHub → auto-redeploys. Check GA4 → Reports → Realtime while you visit the site.
5. (Optional, recommended) mark the enquiry as a **conversion**: the form redirects to `/thank-you.html`, so in
   GA4 → Admin → Events → create event "generate_lead" when `page_location` contains `thank-you`, then mark it
   a Key Event. Now you can count enquiries.
6. (AU privacy) GA4 with IP-anonymisation is standard; a simple cookie/consent notice is good practice but not
   legally mandated for a small AU business site. Add one later if desired.

---

## 7. Google Search Console (free, essential for SEO)

1. **search.google.com/search-console** → Add property → **Domain** property `sixthvision.com.au`
   (verify via a **DNS TXT record** — easiest once you're on Cloudflare DNS; or use the GA4 verification if
   the URL-prefix property is chosen).
2. After verification → **Sitemaps** → submit `https://sixthvision.com.au/sitemap.xml`.
3. **URL Inspection** → enter the homepage → **Request indexing** (speeds up first crawl).
4. Check **Coverage/Pages** and **Core Web Vitals** over the following days.

---

## 8. Local SEO (big for "real estate photography Melbourne")

- [ ] **Google Business Profile** (business.google.com) — create/claim "Sixth Vision", category *Photographer*
      / *Commercial photographer*, service area **Melbourne**, add phone `0474 126 276`,
      `sixthvision.mel@gmail.com`, website, hours, and photos. This is the single biggest local-SEO lever and
      it feeds the "reviews" you already display. Ask happy agents (James & Co, Rutherfords) for Google reviews.
- [ ] Keep NAP (Name, Address/area, Phone) identical across the site, GBP, Instagram, Facebook.
- [ ] List on Bing Places too (bing.com/webmasters) — quick, submit the same sitemap.

---

## 9. Post-launch QA checklist

- [ ] Site loads on `https://sixthvision.com.au` (and `www` redirects to it) with a valid padlock.
- [ ] Submit the contact form for real → confirmation email arrives → thank-you page shows.
- [ ] Click WhatsApp float, phone, email, all socials — correct destinations.
- [ ] Lightbox opens/cycles; both before/after sliders drag; showreel video plays.
- [ ] Test on a real phone (iOS Safari + Android Chrome): stars small, "how it works" centred, no sideways scroll.
- [ ] PageSpeed Insights mobile ≥ 90; Rich Results LocalBusiness valid; GA4 Realtime shows your visit.
- [ ] Search `site:sixthvision.com.au` in Google after a few days — homepage indexed.

---

## 10. Making edits after launch (recap)

Edit `styles.css` / `main.js` (the readable sources) → run
`python C:\Users\gawar\Downloads\sixthvision-final-minify.py` → bump the `?v=` number in `index.html`,
`thank-you.html`, `404.html` → commit/upload to GitHub → Cloudflare/Netlify auto-redeploys in ~1 min.
Images: replace the WebP in `assets/img/` (same filename) → because of immutable caching, either use a fresh
deploy or hard-refresh to see changes.

---

**One-line recommendation:** GitHub → **Cloudflare Pages** + **Web3Forms** for the form + **Cloudflare DNS**
for the domain; then GA4 + Search Console + Google Business Profile. If you want the absolute least fuss and a
native form, use **Netlify** instead of Cloudflare Pages (steps in §2B) — everything else is identical.
