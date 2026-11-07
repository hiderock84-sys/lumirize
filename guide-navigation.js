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
  const languageLinks = [...document.querySelectorAll(".home-languages a[lang], .menu-languages a[lang]")];

  const updateLinks = section => {
    if (!Object.hasOwn(japanesePages, section)) return;
    languageLinks.forEach(link => {
      const language = link.getAttribute("lang");
      if (language === "ja") link.setAttribute("href", japanesePages[section]);
      else if (["en", "ko", "tl", "th"].includes(language)) {
        link.setAttribute("href", `guide-${language}.html${section === "top" ? "" : "#" + section}`);
      }
    });
  };
  const updateFromHash = () => {
    const section = window.location.hash.slice(1);
    updateLinks(Object.hasOwn(japanesePages, section) ? section : "top");
  };
  updateFromHash();
  window.addEventListener("hashchange", updateFromHash);
  window.addEventListener("pageshow", updateFromHash);
  // Keep the selected topic while the visitor scrolls back to the language
  // controls. Menu navigation uses replaceState, which does not emit hashchange.
  document.querySelectorAll('a[href*="#"]').forEach(link => {
    link.addEventListener("click", event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const destination = new URL(link.href, window.location.href);
      if (destination.origin === location.origin && destination.pathname === location.pathname &&
          destination.search === location.search) updateLinks(destination.hash.slice(1));
    });
  });
})();
