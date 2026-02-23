(() => {
  const toggle = document.querySelector(".nav__toggle");
  const panel = document.querySelector(".nav__panel");
  if (toggle && panel) {
    const close = () => { panel.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); };
    toggle.addEventListener("click", () => {
      const open = panel.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    panel.addEventListener("click", (e) => { if (e.target.closest("a")) close(); });
    document.addEventListener("click", (e) => { if (!panel.contains(e.target) && !toggle.contains(e.target)) close(); });
  }

  // cinematic
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

  // contact -> mailto
  const form = document.querySelector("#contactForm");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const type = (fd.get("type") || "").toString().trim();
      const msg = (fd.get("message") || "").toString().trim();
      if (!type || !msg) { alert("必須項目を入力してください"); return; }
      const subject = encodeURIComponent(`【ルミライズ相談】${type}`);
      const body = encodeURIComponent(`相談内容：${type}\n\nお問い合わせ内容：\n${msg}\n`);
      location.href = `mailto:info@lumirize.com?subject=${subject}&body=${body}`;
    });
  }
})();
