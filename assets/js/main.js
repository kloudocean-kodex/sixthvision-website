/* Sixth Vision — interactions. Quiet, physics-eased, reduced-motion aware.
   Rev 2026-09-03. Scroll work is rAF-batched and self-retiring; modal surfaces
   trap focus. Business facts remain stable in the DOM for search/AI extraction. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* One rAF loop for every scroll-driven job, instead of one listener each.
     A job returns true when it is finished and wants to be dropped. */
  var jobs = [], ticking = false;
  function onFrame() {
    ticking = false;
    for (var i = jobs.length - 1; i >= 0; i--) {
      if (jobs[i]() === true) jobs.splice(i, 1);
    }
    if (!jobs.length) window.removeEventListener('scroll', request);
  }
  function request() {
    if (!ticking && jobs.length) { ticking = true; requestAnimationFrame(onFrame); }
  }
  function addJob(fn) {
    jobs.push(fn);
    window.addEventListener('scroll', request, { passive: true });
    request();
  }
  window.addEventListener('resize', request, { passive: true });

  /* ---- Header: solid after leaving the hero ----
     The class write is guarded: toggling a class on every scroll tick
     invalidates style on the sticky header ~60x/sec for no visual change. */
  var header = document.querySelector('.site-header');
  if (header) {
    var isSolid = null;
    addJob(function () {
      var solid = window.scrollY > 40;
      if (solid !== isSolid) { isSolid = solid; header.classList.toggle('is-solid', solid); }
    });
  }

  /* ---- Focus trap, shared by the drawer and the lightbox ---- */
  var FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';
  function trap(container, e) {
    if (e.key !== 'Tab') return;
    var f = [].slice.call(container.querySelectorAll(FOCUSABLE)).filter(function (el) {
      return el.offsetWidth || el.offsetHeight || el.getClientRects().length;
    });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  /* ---- Mobile nav ---- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    var setNav = function (open) {
      nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      document.body.style.overflow = open ? 'hidden' : '';
      if (open) { var f = nav.querySelector(FOCUSABLE); if (f) f.focus(); }
      else toggle.focus();
    };
    toggle.addEventListener('click', function () { setNav(!nav.classList.contains('is-open')); });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A' && nav.classList.contains('is-open')) setNav(false);
    });
    document.addEventListener('keydown', function (e) {
      if (!nav.classList.contains('is-open')) return;
      if (e.key === 'Escape') setNav(false); else trap(nav, e);
    });
    /* rotating past the breakpoint must not strand a hidden drawer holding
       the body scroll-lock */
    var wide = window.matchMedia('(min-width: 881px)');
    var onWide = function (m) { if (m.matches && nav.classList.contains('is-open')) setNav(false); };
    if (wide.addEventListener) wide.addEventListener('change', onWide);
    else if (wide.addListener) wide.addListener(onWide);
  }

  /* ---- Scroll reveal + semantic stat integrity ---------------------------
     The original count-up animation temporarily replaced real business facts
     such as 50,000 with 0 while the animation ran. Rendered-page extractors can
     snapshot during that interval, so search/AI systems were receiving facts
     that contradicted the static HTML. The final facts now remain in the DOM at
     all times. Motion belongs to the containing reveal, not to the meaning. */
  var revealEls = [].slice.call(document.querySelectorAll('.reveal'));
  var counters = [].slice.call(document.querySelectorAll('[data-count]'));

  function fmt(n) { try { return n.toLocaleString('en-AU'); } catch (e) { return String(n); } }
  function revealNow(el) { el.classList.add('is-in'); }

  counters.forEach(function (el) {
    var target = parseInt(el.getAttribute('data-count'), 10);
    if (!isNaN(target)) el.textContent = fmt(target);
    el.setAttribute('data-counted', '1');
  });

  if (reduceMotion) {
    revealEls.forEach(revealNow);
  } else if ('IntersectionObserver' in window) {
    var revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { revealNow(e.target); revealIO.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { revealIO.observe(el); });
  } else {
    var pendingR = revealEls.slice();
    addJob(function () {
      var vh = window.innerHeight || document.documentElement.clientHeight;
      pendingR = pendingR.filter(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < vh - 40 && r.bottom > 0) { revealNow(el); return false; }
        return true;
      });
      return !pendingR.length;   /* retire when done */
    });
    window.addEventListener('load', request, { passive: true, once: true });
  }

  /* ---- Trust marquee: an infinite 52s animation should not run off screen ---- */
  var marquee = document.querySelector('.marquee');
  if (marquee && 'IntersectionObserver' in window) {
    marquee.classList.add('is-idle');
    new IntersectionObserver(function (entries) {
      marquee.classList.toggle('is-idle', !entries[0].isIntersecting);
    }, { rootMargin: '120px 0px' }).observe(marquee);
  }

  /* ---- Before / after sliders (craft + virtual staging) ---- */
  [].forEach.call(document.querySelectorAll('.ba'), function (ba) {
    var range = ba.querySelector('input[type="range"]');
    if (!range) return;
    function setPos(v) { ba.style.setProperty('--ba-pos', v + '%'); }
    range.addEventListener('input', function () { setPos(range.value); });
    setPos(range.value);
  });

  /* ---- Showreel: load the film only on demand ---- */
  var playBtn = document.getElementById('play-showreel');
  if (playBtn) {
    playBtn.addEventListener('click', function () {
      var frame = document.getElementById('showreel-frame');
      var poster = frame.querySelector('img');
      var video = document.createElement('video');
      video.src = 'assets/video/showreel.mp4?v=2';
      /* the poster keeps the frame filled during the first buffer instead of
         flashing black; nothing was fetched before this click */
      if (poster) video.poster = poster.currentSrc || poster.src;
      video.controls = true;
      video.autoplay = true;
      video.playsInline = true;
      video.setAttribute('aria-label', 'Sixth Vision showreel');
      frame.appendChild(video);
      playBtn.remove();
      video.focus({ preventScroll: true });   /* the button that held focus is gone */
      video.play().catch(function () { /* controls remain for manual play */ });
    });
  }

  /* ---- Drone band: gentle parallax ---- */
  var parallaxImg = document.querySelector('[data-parallax]');
  if (parallaxImg && !reduceMotion && 'IntersectionObserver' in window) {
    var band = parallaxImg.closest('.drone-band');
    var active = false;
    new IntersectionObserver(function (entries) {
      active = entries[0].isIntersecting;
      band.classList.toggle('is-parallaxing', active);   /* promote only while moving */
      if (active) request();
    }).observe(band);
    addJob(function () {
      if (!active) return;
      var rect = band.getBoundingClientRect();
      var vh = window.innerHeight;
      var progress = (rect.top + rect.height / 2 - vh / 2) / (vh / 2 + rect.height / 2);
      var shift = Math.max(-1, Math.min(1, progress)) * -5;   /* ±5% drift */
      parallaxImg.style.transform = 'translateY(' + shift.toFixed(2) + '%)';
    });
  }

  /* ---- Lightbox: full-size portfolio viewer ---- */
  var lightbox = document.getElementById('lightbox');
  var triggers = [].slice.call(document.querySelectorAll('.work-trigger'));
  if (lightbox && triggers.length) {
    var lbImg = lightbox.querySelector('.lightbox-img');
    var lbCaption = lightbox.querySelector('.lightbox-caption');
    var lbCount = lightbox.querySelector('.lightbox-count');
    var btnClose = lightbox.querySelector('.lightbox-close');
    var btnPrev = lightbox.querySelector('.lightbox-prev');
    var btnNext = lightbox.querySelector('.lightbox-next');
    var current = 0, lastFocus = null, inerted = [];

    lbCount.setAttribute('aria-live', 'polite');

    function show(i) {
      current = (i + triggers.length) % triggers.length;
      var t = triggers[current];
      lbImg.src = t.getAttribute('data-lightbox-src');
      var cap = t.getAttribute('data-lightbox-caption') || '';
      lbImg.alt = cap;
      lbCaption.textContent = cap;
      lbCount.textContent = (current + 1) + ' / ' + triggers.length;
    }
    function background(hidden) {
      /* inert removes the page behind the dialog from focus AND from the
         accessibility tree, which aria-modal alone does not reliably do.
         Applied to every body-level sibling rather than a hand-listed set:
         the skip link and the topbar also sit at body level, and naming
         elements individually means anything added later silently stays
         reachable behind the open dialog. Only what we set is cleared. */
      if (hidden) {
        inerted = [].filter.call(document.body.children, function (el) {
          return el !== lightbox && !el.hasAttribute('inert') &&
                 el.tagName !== 'SCRIPT' && el.tagName !== 'NOSCRIPT';
        });
        inerted.forEach(function (el) { el.setAttribute('inert', ''); });
      } else {
        inerted.forEach(function (el) { el.removeAttribute('inert'); });
        inerted = [];
      }
    }
    function open(i) {
      lastFocus = document.activeElement;
      show(i);
      lightbox.classList.add('is-open');
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      background(true);
      btnClose.focus();
    }
    function close() {
      lightbox.classList.remove('is-open');
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      background(false);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    triggers.forEach(function (t, i) { t.addEventListener('click', function () { open(i); }); });
    btnClose.addEventListener('click', close);
    btnPrev.addEventListener('click', function () { show(current - 1); });
    btnNext.addEventListener('click', function () { show(current + 1); });
    lightbox.addEventListener('click', function (e) { if (e.target === lightbox) close(); });
    document.addEventListener('keydown', function (e) {
      if (!lightbox.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(current - 1);
      else if (e.key === 'ArrowRight') show(current + 1);
      else trap(lightbox, e);
    });
  }

  /* ---- Footer year ---- */
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
