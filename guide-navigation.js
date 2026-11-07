(() => {
  "use strict";
  if (!document.body.classList.contains("guide-page")) return;

  const japanesePages = {
    top: "index.html",
    support: "services.html",
    facilities: "services.html#nightcare-photo",
    "housing-check": "services.html#housing-check",
    fees: "fees.html#house-fees",
    process: "process.html",
    faq: "faq.html",
    contact: "contact.html#languages"
  };
  const sections = [...document.querySelectorAll(".translated-guide > section[id]")];
  const languageLinks = [...document.querySelectorAll(".home-languages a[lang], .menu-languages a[lang]")];
  const menu = document.getElementById("mobileMenu");
  const header = document.querySelector(".header");
  let currentSection = "top";
  let scrollFrame = 0;

  const updateLinks = section => {
    if (!Object.hasOwn(japanesePages, section)) return;
    currentSection = section;
    languageLinks.forEach(link => {
      const language = link.getAttribute("lang");
      if (language === "ja") link.setAttribute("href", japanesePages[section]);
      else if (["en", "ko", "tl", "th"].includes(language)) {
        link.setAttribute("href", `guide-${language}.html${section === "top" ? "" : "#" + section}`);
      }
    });
  };
  const updateFromPosition = () => {
    scrollFrame = 0;
    // The modal fixes the body; keep the last reading position while it is open.
    if (menu?.open) return;
    const readingLine = Math.max(0, header?.getBoundingClientRect().bottom || 0) + 32;
    let section = "top";
    for (const element of sections) {
      if (element.getBoundingClientRect().top <= readingLine) section = element.id;
      else break;
    }
    if (section !== currentSection) updateLinks(section);
  };
  const updateFromHash = () => {
    const section = window.location.hash.slice(1);
    if (Object.hasOwn(japanesePages, section)) updateLinks(section);
  };
  updateLinks("top");
  updateFromHash();
  window.addEventListener("hashchange", updateFromHash);
  window.addEventListener("scroll", () => {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateFromPosition);
  }, { passive: true });
  window.addEventListener("pageshow", () => requestAnimationFrame(updateFromPosition));
  window.addEventListener("resize", () => requestAnimationFrame(updateFromPosition));
})();
