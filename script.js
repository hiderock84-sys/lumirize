(() => {
  // Mobile nav
  const toggle = document.querySelector(".nav__toggle");
  const panel = document.querySelector(".nav__panel");
  if (toggle && panel) {
    const close = () => {
      panel.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    };
    toggle.addEventListener("click", () => {
      const open = panel.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    panel.addEventListener("click", (e) => {
      const a = e.target.closest("a");
      if (a) close();
    });
    document.addEventListener("click", (e) => {
      if (!panel.contains(e.target) && !toggle.contains(e.target)) close();
    });
  }

  // Smooth scroll for same-page anchors
  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const id = a.getAttribute("href");
    if (!id || id === "#") return;
    const el = document.querySelector(id);
    if (!el) return;
    e.preventDefault();
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  // Reveal on scroll
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) en.target.classList.add("is-in");
    });
  }, { threshold: 0.12 });

  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

  // Cinematic scene switch
  const story = document.querySelector("#story");
  if (story) {
    const imgs = story.querySelectorAll(".cinematic__img");
    const blocks = story.querySelectorAll(".cinematic__block");

    const setScene = (n) => {
      imgs.forEach(i => i.classList.toggle("is-active", i.dataset.scene === String(n)));
      blocks.forEach(b => b.classList.toggle("is-active", b.dataset.scene === String(n)));
    };

    const onScroll = () => {
      const rect = story.getBoundingClientRect();
      const vh = window.innerHeight;
      const progress = Math.min(1, Math.max(0, (vh - rect.top) / (vh + rect.height)));
      setScene(progress < 0.55 ? 1 : 2);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Contact form -> open mail client
  const form = document.querySelector("#contactForm");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const name = (fd.get("name") || "").toString().trim();
      const email = (fd.get("email") || "").toString().trim();
      const tel = (fd.get("tel") || "").toString().trim();
      const type = (fd.get("type") || "").toString().trim();
      const msg = (fd.get("message") || "").toString().trim();

      if (!type || !msg) {
        alert("「相談内容」と「お問い合わせ内容」は必須です。");
        return;
      }

      const subject = encodeURIComponent(`【ルミライズ相談】${type}${name ? " / " + name : ""}`);
      const body = encodeURIComponent(
`相談内容：${type}
お名前：${name || "（未記入）"}
メール：${email || "（未記入）"}
電話：${tel || "（未記入）"}

お問い合わせ内容：
${msg}
`
      );

      location.href = `mailto:info@lumirize.com?subject=${subject}&body=${body}`;
    });
  }

  // toTop button
  const toTop = document.querySelector(".toTop");
  if (toTop) {
    const on = () => {
      if (window.scrollY > 600) toTop.classList.add("is-show");
      else toTop.classList.remove("is-show");
    };
    window.addEventListener("scroll", on, { passive: true });
    on();
    toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }
})();
