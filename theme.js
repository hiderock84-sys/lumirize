(function () {
  var KEY = "lumirize-layout";
  var THEMES = ["1", "2", "3", "4", "5"];

  function readTheme() {
    var match = window.location.search.match(/[?&]v=([1-5])/);
    if (match) return match[1];
    try {
      var stored = window.localStorage.getItem(KEY);
      if (THEMES.indexOf(stored) !== -1) return stored;
    } catch (err) {
      /* ignore */
    }
    return "1";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", "v" + theme);
    try {
      window.localStorage.setItem(KEY, theme);
    } catch (err) {
      /* ignore */
    }
    document.querySelectorAll(".theme-dock a[data-theme]").forEach(function (link) {
      if (link.getAttribute("data-theme") === theme) link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
    });
  }

  function withTheme(url, theme) {
    try {
      var parsed = new URL(url, window.location.href);
      if (parsed.origin !== window.location.origin) return url;
      var path = parsed.pathname;
      if (!/\.html?$/.test(path) && path.slice(-1) !== "/") return url;
      parsed.searchParams.set("v", theme);
      return parsed.pathname + parsed.search + parsed.hash;
    } catch (err) {
      return url;
    }
  }

  var theme = readTheme();
  applyTheme(theme);

  document.querySelectorAll('a[href^="./"], a[href$=".html"]').forEach(function (link) {
    var href = link.getAttribute("href");
    if (!href || link.closest(".theme-dock")) return;
    link.setAttribute("href", withTheme(href, theme));
  });

  document.querySelectorAll(".theme-dock a[data-theme]").forEach(function (link) {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      var next = link.getAttribute("data-theme");
      var url = new URL(window.location.href);
      url.searchParams.set("v", next);
      window.location.replace(url.pathname + url.search + url.hash);
    });
  });
})();
