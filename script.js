(() => {
  const header = document.getElementById("site-header");
  const menuToggle = document.getElementById("menu-toggle");
  const globalNav = document.getElementById("global-nav");
  const navLinks = globalNav ? globalNav.querySelectorAll("a") : [];
  const navPrimaryLinks = globalNav ? globalNav.querySelectorAll("ul a") : [];
  const backToTop = document.getElementById("back-to-top");
  const mobileConsult = document.querySelector(".mobile-consult");
  const navLabelMap = {
    "index.html": { jp: "トップ", en: "HOME" },
    "about.html": { jp: "私たちについて", en: "ABOUT" },
    "stats.html": { jp: "支援実績", en: "IMPACT" },
    "services.html": { jp: "サービス", en: "SERVICES" },
    "support.html": { jp: "支援内容", en: "SUPPORT" },
    "process.html": { jp: "入居までの流れ", en: "PROCESS" },
    "faq.html": { jp: "FAQ", en: "FAQ" },
    "contact.html": { jp: "お問い合わせ", en: "CONTACT" }
  };

  const currentPath = (() => {
    try {
      const path = window.location.pathname.split("/").pop();
      return path && path.length ? path : "index.html";
    } catch {
      return "index.html";
    }
  })();

  navPrimaryLinks.forEach((link) => {
    try {
      const linkPath = new URL(link.href, window.location.href).pathname.split("/").pop() || "index.html";
      const labels = navLabelMap[linkPath];
      if (labels && !link.querySelector(".nav-label-jp")) {
        link.innerHTML = `<span class="nav-label-jp">${labels.jp}</span><span class="nav-label-en">${labels.en}</span>`;
      }
      if (linkPath === currentPath) {
        link.setAttribute("aria-current", "page");
      }
    } catch {
      // Ignore malformed URLs.
    }
  });

  if (globalNav && !globalNav.querySelector(".mobile-nav-cta")) {
    const consultButton = globalNav.querySelector(".btn-nav");
    if (consultButton) {
      const ctaWrap = document.createElement("div");
      ctaWrap.className = "mobile-nav-cta";

      const telButton = document.createElement("a");
      telButton.href = "tel:0427048308";
      telButton.className = "btn btn-secondary btn-nav-tel";
      telButton.setAttribute("aria-label", "電話で相談する 042-704-8308");
      telButton.textContent = "TEL 042-704-8308";

      ctaWrap.append(consultButton, telButton);
      globalNav.append(ctaWrap);
    }
  }

  const updateHeaderState = () => {
    if (!header || !backToTop) return;
    const scrolled = window.scrollY > 24;
    header.classList.toggle("scrolled", scrolled);
    backToTop.classList.toggle("visible", window.scrollY > 500);

    if (mobileConsult) {
      const isMobileViewport = window.innerWidth <= 767;
      const menuOpen = globalNav ? globalNav.classList.contains("open") : false;
      const showConsult = isMobileViewport && window.scrollY > 720 && !menuOpen;
      mobileConsult.classList.toggle("visible", showConsult);
    }
  };

  updateHeaderState();
  window.addEventListener("scroll", updateHeaderState, { passive: true });
  window.addEventListener("resize", updateHeaderState);

  if (menuToggle && globalNav) {
    const setMenuOpen = (isOpen) => {
      menuToggle.setAttribute("aria-expanded", String(isOpen));
      menuToggle.setAttribute("aria-label", isOpen ? "メニューを閉じる" : "メニューを開く");
      globalNav.classList.toggle("open", isOpen);
      document.body.classList.toggle("menu-open", isOpen);
      updateHeaderState();
    };

    menuToggle.addEventListener("click", () => {
      const expanded = menuToggle.getAttribute("aria-expanded") === "true";
      setMenuOpen(!expanded);
    });

    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        if (window.innerWidth <= 767) {
          setMenuOpen(false);
        }
      });
    });

    document.addEventListener("click", (event) => {
      const clickedInsideNav = globalNav.contains(event.target);
      const clickedToggle = menuToggle.contains(event.target);
      if (!clickedInsideNav && !clickedToggle && globalNav.classList.contains("open")) {
        setMenuOpen(false);
      }
    });

    globalNav.addEventListener("click", (event) => {
      if (window.innerWidth > 767 || !globalNav.classList.contains("open")) return;
      const tappedLink = event.target.closest("a");
      if (tappedLink) {
        setMenuOpen(false);
        return;
      }
      const tappedContentArea = event.target.closest("ul, .mobile-nav-cta");
      if (!tappedContentArea) {
        setMenuOpen(false);
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && globalNav.classList.contains("open")) {
        setMenuOpen(false);
        menuToggle.focus();
      }
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 767 && globalNav.classList.contains("open")) {
        setMenuOpen(false);
      }
    });
  }

  const revealNodes = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.16 }
    );
    revealNodes.forEach((node) => observer.observe(node));
  } else {
    revealNodes.forEach((node) => node.classList.add("is-visible"));
  }

  const faqItems = document.querySelectorAll(".faq-item");
  faqItems.forEach((item, index) => {
    const button = item.querySelector(".faq-question");
    const answer = item.querySelector(".faq-answer");
    if (!button || !answer) return;

    const answerId = `faq-answer-${index + 1}`;
    answer.id = answerId;
    button.setAttribute("aria-controls", answerId);

    button.addEventListener("click", () => {
      const currentlyOpen = item.classList.contains("active");

      faqItems.forEach((otherItem) => {
        const otherButton = otherItem.querySelector(".faq-question");
        const otherAnswer = otherItem.querySelector(".faq-answer");
        if (!otherButton || !otherAnswer) return;

        otherItem.classList.remove("active");
        otherButton.setAttribute("aria-expanded", "false");
        otherAnswer.style.maxHeight = null;
      });

      if (!currentlyOpen) {
        item.classList.add("active");
        button.setAttribute("aria-expanded", "true");
        answer.style.maxHeight = `${answer.scrollHeight}px`;
      }
    });
  });

  const form = document.getElementById("contact-form");
  const formStatus = document.getElementById("form-status");
  if (form && formStatus) {
    const requiredFields = [
      form.querySelector("#name"),
      form.querySelector("#email"),
      form.querySelector("#topic"),
      form.querySelector("#message"),
      form.querySelector("#privacy")
    ].filter(Boolean);

    const resetFieldError = (field) => {
      field.classList.remove("invalid");
      if (field.type === "checkbox") {
        field.parentElement?.classList.remove("invalid");
      }
    };

    const markFieldError = (field) => {
      field.classList.add("invalid");
      if (field.type === "checkbox") {
        field.parentElement?.classList.add("invalid");
      }
    };

    requiredFields.forEach((field) => {
      field.addEventListener("input", () => resetFieldError(field));
      field.addEventListener("change", () => resetFieldError(field));
    });

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      formStatus.textContent = "";
      formStatus.className = "form-status";

      let firstInvalid = null;
      requiredFields.forEach((field) => {
        resetFieldError(field);
      });

      requiredFields.forEach((field) => {
        const isCheckbox = field.type === "checkbox";
        const valid = isCheckbox ? field.checked : field.value.trim().length > 0;

        if (!valid) {
          markFieldError(field);
          if (!firstInvalid) firstInvalid = field;
          return;
        }

        if (field.type === "email" && !field.checkValidity()) {
          markFieldError(field);
          if (!firstInvalid) firstInvalid = field;
        }
      });

      if (firstInvalid) {
        formStatus.textContent = "入力内容をご確認ください。必須項目の未入力、または形式に誤りがあります。";
        formStatus.classList.add("error");
        firstInvalid.focus();
        return;
      }

      const submitButton = form.querySelector("button[type='submit']");
      if (submitButton) submitButton.disabled = true;

      window.setTimeout(() => {
        form.reset();
        if (submitButton) submitButton.disabled = false;
        formStatus.textContent =
          "お問い合わせありがとうございます。担当者より2営業日以内にご連絡いたします。";
        formStatus.classList.add("success");
      }, 700);
    });
  }
})();
