const animatedBars = document.querySelectorAll(".bar-fill");

const animateBar = (entry) => {
  const bar = entry.target;
  const width = bar.dataset.width;
  if (!width) return;
  bar.style.width = `${width}%`;
};

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateBar(entry);
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.35,
    },
  );

  animatedBars.forEach((bar) => observer.observe(bar));
} else {
  animatedBars.forEach((bar) => {
    const width = bar.dataset.width;
    if (width) bar.style.width = `${width}%`;
  });
}

document.querySelectorAll(".full-panel-actions .panel-jump").forEach((anchor) => {
  anchor.addEventListener("click", (event) => {
    const href = anchor.getAttribute("href");
    if (!href || !href.startsWith("#")) return;
    const panel = document.querySelector(href);
    if (!panel) return;
    panel.setAttribute("open", "open");
  });
});
