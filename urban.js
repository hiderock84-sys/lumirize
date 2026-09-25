(() => {
  "use strict";
  const menu = document.getElementById("mobileMenu");
  const toggle = document.querySelector(".menu-toggle");
  const closeButton = document.querySelector(".menu-close");
  const closeMenu = () => {
    if (menu.open) menu.close();
  };
  toggle?.addEventListener("click", () => {
    menu.showModal();
    toggle.setAttribute("aria-expanded", "true");
    document.body.classList.add("menu-open");
    closeButton.focus();
  });
  closeButton?.addEventListener("click", closeMenu);
  menu?.addEventListener("close", () => {
    toggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("menu-open");
  });
  menu?.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener("click", () => {
      closeMenu();
      const target = document.getElementById(link.hash.slice(1));
      if (target) {
        target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
        target.addEventListener("blur", () => target.removeAttribute("tabindex"), { once: true });
      }
    });
  });
  const desktop = window.matchMedia("(min-width: 901px)");
  desktop.addEventListener("change", event => { if (event.matches) closeMenu(); });

  const form = document.getElementById("contactForm");
  document.querySelectorAll("[data-topic]").forEach(link => {
    link.addEventListener("click", () => {
      if (form) form.elements.type.value = link.dataset.topic;
      else link.href = "contact.html?topic=" + encodeURIComponent(link.dataset.topic);
    });
  });
  form?.addEventListener("submit", event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const value = key => String(data.get(key) || "").trim();
    const message = value("message");
    if (!message) {
      form.elements.message.setCustomValidity("ご相談内容をご記入ください。");
      form.elements.message.reportValidity();
      return;
    }
    const subject = "【ルミライズ相談】" + value("type");
    const body = [
      "相談内容：" + value("type"),
      "お名前：" + (value("name") || "（未記入）"),
      "メール：" + (value("email") || "（未記入）"),
      "電話：" + (value("tel") || "（未記入）"),
      "", "お問い合わせ内容：", message
    ].join("\n");
    const mailto = "mailto:info@lumirize.com?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    document.getElementById("formStatus").textContent =
      "メールアプリで内容を確認し、送信してください。開かない場合は、info@lumirize.com 宛に直接お送りください。この画面からはまだ送信されていません。";
    window.location.href = mailto;
  });
  form?.elements.message.addEventListener("input", () => form.elements.message.setCustomValidity(""));
  form?.addEventListener("focusin", () => document.body.classList.add("editing-form"));
  form?.addEventListener("focusout", () => {
    requestAnimationFrame(() => {
      if (!form.contains(document.activeElement)) document.body.classList.remove("editing-form");
    });
  });
  const currentForm = document.getElementById("contact-form");
  if (currentForm) {
    const topic = new URLSearchParams(window.location.search).get("topic");
    if (topic && [...currentForm.elements.topic.options].some(option => option.value === topic)) currentForm.elements.topic.value = topic;
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
  document.querySelectorAll(".glass-button").forEach(button => {
    const moveHighlight = event => {
      if (reducedMotion.matches) return;
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
  if (document.body.classList.contains("inner-page")) {
    const floatingButtons = [...document.querySelectorAll(".mobile-cta .glass-button")];
    const darkSurfaces = [...document.querySelectorAll(".header, .footer, .contact-emergency, .leader-profile img")];
    let toneFrame = 0;
    const updateGlassTone = () => {
      toneFrame = 0;
      const surfaces = darkSurfaces.map(surface => surface.getBoundingClientRect());
      floatingButtons.forEach(button => {
        const box = button.getBoundingClientRect();
        if (!box.width || !box.height) return;
        const x = box.left + box.width / 2;
        const y = box.top + box.height / 2;
        const dark = surfaces.some(rect => x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom);
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
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
