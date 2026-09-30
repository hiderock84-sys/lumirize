(() => {
  "use strict";
  const menu = document.getElementById("mobileMenu");
  const toggle = document.querySelector(".menu-toggle");
  const closeButton = document.querySelector(".menu-close");
  const root = document.documentElement;
  let menuScrollY = null;
  const unlockPage = () => {
    if (menuScrollY === null) return;
    const top = menuScrollY;
    menuScrollY = null;
    document.body.classList.remove("menu-open");
    document.body.style.removeProperty("--menu-scroll-offset");
    // The root keeps smooth scrolling disabled until the saved position is restored.
    window.scrollTo({ left: 0, top, behavior: "instant" });
    root.classList.remove("menu-open");
    toggle?.setAttribute("aria-expanded", "false");
    toggle?.focus({ preventScroll: true });
  };
  let menuClosing = false;
  const slideMenu = (opening) => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return null;
    return menu.animate([
      { transform: opening ? "translateX(100%)" : "translateX(0)" },
      { transform: opening ? "translateX(0)" : "translateX(100%)" }
    ], { duration: opening ? 300 : 220, easing: "cubic-bezier(.22,1,.36,1)" });
  };
  const closeMenu = async () => {
    if (!menu?.open || menuClosing) return;
    menuClosing = true;
    const animation = slideMenu(false);
    if (animation) await animation.finished.catch(() => {});
    menu.close();
    menuClosing = false;
    unlockPage();
  };
  toggle?.addEventListener("click", () => {
    if (!menu || menu.open) return;
    menuScrollY = Math.max(0, window.scrollY);
    document.body.style.setProperty("--menu-scroll-offset", -menuScrollY + "px");
    root.classList.add("menu-open");
    document.body.classList.add("menu-open");
    menu.showModal();
    slideMenu(true);
    toggle.setAttribute("aria-expanded", "true");
    closeButton.focus({ preventScroll: true });
  });
  closeButton?.addEventListener("click", closeMenu);
  menu?.addEventListener("click", event => {
    if (event.target !== menu) return;
    const box = menu.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right) closeMenu();
  });
  menu?.addEventListener("close", () => {
    unlockPage();
  });
  menu?.addEventListener("cancel", event => {
    event.preventDefault();
    closeMenu();
  });
  menu?.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener("click", async () => {
      await closeMenu();
      const target = document.getElementById(link.hash.slice(1));
      if (target) {
        target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
        target.addEventListener("blur", () => target.removeAttribute("tabindex"), { once: true });
      }
    });
  });


  document.querySelectorAll('[data-topic]').forEach(link => {
    const lang = document.body.dataset.homeLang;
    const translated = ['en','ko','tl','th'].includes(lang);
    link.href = 'contact.html?topic=' + encodeURIComponent(link.dataset.topic) + (translated ? '&lang=' + lang + '#languages' : '#consultation-form');
  });
  const currentForm = document.getElementById("contact-form");
  if (currentForm) {
    const languageNames = {ja: '日本語', en: 'English', ko: '한국어', tl: 'Tagalog', th: 'ภาษาไทย'};
    const requestedLanguage = new URLSearchParams(window.location.search).get('lang');
    if (Object.hasOwn(languageNames, requestedLanguage)) {
      const guideLanguage = requestedLanguage === 'tl' ? 'fil' : requestedLanguage;
      const guide = document.querySelector('#languages summary[lang="' + guideLanguage + '"]');
      if (guide) guide.parentElement.open = true;
      const languageSelect = document.getElementById('language');
      if (languageSelect) languageSelect.value = languageNames[requestedLanguage];
    }
    const legacyTopics = {"住まい支援・入居相談": "住まい・入居の相談", "家賃補助・制度活用相談": "住まい・入居の相談", "就労支援接続相談": "住まい・入居の相談", "3か月・6か月・1年・2年の面談相談": "住まい・入居の相談", "依存症者向け住宅について": "住まい・入居の相談", "刑務所出所者向け住宅について": "住まい・入居の相談", "LGBTQ+向け住居支援について": "住まい・入居の相談", "DV被害者向け緊急シェルター支援について": "住まい・入居の相談", "DV被害者向け安全確保・一時居住の相談について": "住まい・入居の相談", "外国人労働者・移民向け住居支援について": "住まい・入居の相談", "外国人労働者・外国人住民向け住居支援について": "住まい・入居の相談", "ナイトケアハウスについて": "ナイトケアハウスの相談", "家族・オーナー・自治体向け連携相談": "家族・支援機関からの相談", "その他": "その他・選び方が分からない"};
    const requestedTopic = new URLSearchParams(window.location.search).get("topic");
    const topic = legacyTopics[requestedTopic] || requestedTopic;
    if (topic && [...currentForm.elements.topic.options].some(option => option.value === topic)) {
      currentForm.elements.topic.value = topic;
      currentForm.elements.topic.dispatchEvent(new Event("change", { bubbles: true }));
    }
    currentForm.addEventListener("focusin", () => document.body.classList.add("editing-form"));
    currentForm.addEventListener("focusout", () => requestAnimationFrame(() => {
      if (!currentForm.contains(document.activeElement)) document.body.classList.remove("editing-form");
    }));
  }
  const page = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll('.desktop-nav a, .mobile-menu nav a, .header__contact').forEach(link => {
    if (page !== "index.html" && link.getAttribute("href") === page) link.setAttribute("aria-current", "page");
  });
  // A local specular highlight follows a pointer without a rendering loop.
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const precisePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  document.querySelectorAll(".glass-button").forEach(button => {
    const moveHighlight = event => {
      if (reducedMotion.matches || !precisePointer.matches || event.pointerType === "touch") return;
      const rect = button.getBoundingClientRect();
      button.style.setProperty("--glass-x", ((event.clientX - rect.left) / rect.width * 100) + "%");
      button.style.setProperty("--glass-y", ((event.clientY - rect.top) / rect.height * 100) + "%");
    };
    const resetHighlight = () => {
      button.style.removeProperty("--glass-x");
      button.style.removeProperty("--glass-y");
    };
    button.addEventListener("pointermove", moveHighlight, { passive: true });
    button.addEventListener("pointerdown", moveHighlight, { passive: true });
    button.addEventListener("pointerleave", resetHighlight);
    button.addEventListener("pointerup", resetHighlight);
    button.addEventListener("pointercancel", resetHighlight);
  });
  // Inner pages use dark labels over the light reading surface, switching to
  // white when the floating controls pass over the portrait or dark sections.
  {
    const innerPage = document.body.classList.contains("inner-page");
    const floatingButtons = [...document.querySelectorAll(".mobile-cta .glass-button")];
    const darkSurfaces = [...document.querySelectorAll(".header, .footer, .contact-emergency, .leader-profile img")];
    const lightSurfaces = [...document.querySelectorAll(".light-section")];
    let toneFrame = 0;
    const updateGlassTone = () => {
      toneFrame = 0;
      const surfaces = (innerPage ? darkSurfaces : lightSurfaces).map(surface => surface.getBoundingClientRect());
      floatingButtons.forEach(button => {
        const box = button.getBoundingClientRect();
        if (!box.width || !box.height) return;
        const x = box.left + box.width / 2;
        const y = box.top + box.height / 2;
        const inside = surfaces.some(rect => x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom);
        const dark = innerPage ? inside : !inside;
        button.dataset.glassTone = dark ? "dark" : "light";
      });
    };
    const scheduleGlassTone = () => {
      if (!toneFrame) toneFrame = requestAnimationFrame(updateGlassTone);
    };
    window.addEventListener("scroll", scheduleGlassTone, { passive: true });
    window.addEventListener("resize", scheduleGlassTone, { passive: true });
    window.addEventListener("load", scheduleGlassTone, { once: true });
    updateGlassTone();
  }
  window.addEventListener('pageshow', () => { if (menu?.open) closeMenu(); });
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
