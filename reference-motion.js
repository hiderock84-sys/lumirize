(() => {
  "use strict";
  const media = window.matchMedia("(prefers-reduced-motion: reduce)");
  const desktop = window.matchMedia("(min-width: 761px)");
  let readingMode = false;
  try {
    readingMode = localStorage.getItem("lumirize-reading-mode") === "static";
  } catch {
    /* Private browsing can restrict preference storage. */
  }
  const motionPaused = () => media.matches || readingMode;
  const motionButtons = [...document.querySelectorAll("[data-motion-toggle]")];
  const reveals = [...document.querySelectorAll("[data-reveal]")];
  let observer;
  if (!motionPaused() && "IntersectionObserver" in window) {
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: "0px 0px -20px 0px" }
    );
    reveals.forEach((el) => {
      el.classList.add("reveal-ready");
      observer.observe(el);
    });
  }

  const story = document.querySelector("[data-story]");
  const stage = story?.querySelector(".v2-story-stage");
  const scenes = story ? [...story.querySelectorAll(".v2-scene")] : [];
  const dots = story ? [...story.querySelectorAll("[data-scene-go]")] : [];
  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
  const smooth = (start, end, value) => {
    const t = clamp((value - start) / (end - start), 0, 1);
    return t * t * (3 - 2 * t);
  };
  const sceneParts = scenes.map((scene) => ({
    scene,
    photo: scene.querySelector("img"),
    backdrop: scene.querySelector(".v2-scene-backdrop"),
    copy: scene.querySelector(".v2-scene-copy"),
    track: scene.querySelector(".v2-scene-text-window"),
    trackHeight: 0,
    copyHeight: 0,
  }));
  let frame = 0;
  let headerHeight = 0;
  function syncDimensions() {
    headerHeight = 0;
    sceneParts.forEach((part) => {
      part.trackHeight = part.track.clientHeight;
      part.copyHeight = part.copy.offsetHeight;
    });
    requestMotion();
  }
  function drawStory() {
    frame = 0;
    if (document.body.classList.contains("menu-open")) {
      return;
    }
    if (!story || !stage || motionPaused()) {
      return;
    }
    const rect = story.getBoundingClientRect();
    const distance = Math.max(1, story.offsetHeight - stage.offsetHeight);
    const progress = clamp((headerHeight - rect.top) / distance, 0, 1);
    const pos = progress * 3;
    const cross1 = smooth(0.84, 1.16, pos);
    const cross2 = smooth(1.84, 2.16, pos);
    // Let the morning scene open into light at the same pace as its crossfade.
    stage.style.setProperty("--story-shade-opacity", (1 - 0.78 * cross2).toFixed(3));
    const weights = [1, cross1, cross2];
    const current = pos < 1 ? 0 : pos < 2 ? 1 : 2;
    sceneParts.forEach((part, i) => {
      const local = clamp(pos - i, 0, 1);
      if (desktop.matches) {
        // Move one complete scene: photograph, backdrop and message stay together.
        // Adjacent panels share the same boundary, so they never ghost over each other.
        const enter = i === 0 ? 1 : smooth(i - 0.18, i + 0.18, pos);
        const exit = i === scenes.length - 1 ? 0 : smooth(i + 0.82, i + 1.18, pos);
        part.scene.style.transform = "translate3d(0," + ((1 - enter - exit) * 100).toFixed(4) + "%,0)";
        part.scene.style.opacity = "1";
        part.scene.style.zIndex = String(i + 1);
        part.photo.style.opacity = "1";
        part.photo.style.zIndex = "1";
        part.photo.style.transform = "scale(1.02)";
        if (part.backdrop) {
          part.backdrop.style.opacity = "1";
          part.backdrop.style.zIndex = "0";
        }
        part.copy.style.transform = "none";
        part.copy.style.opacity = "1";
      } else {
        // Preserve the phone story and clear desktop panel styles after resizing.
        part.scene.style.transform = "";
        part.scene.style.opacity = "";
        part.scene.style.zIndex = "";
        part.photo.style.opacity = weights[i].toFixed(3);
        part.photo.style.zIndex = String(i + 1);
        part.photo.style.transform =
          "translate3d(0," + ((0.5 - local) * 2.4).toFixed(3) + "%,0) scale(" + (1.055 - local * 0.02).toFixed(4) + ")";
        if (part.backdrop) {
          part.backdrop.style.opacity = "";
          part.backdrop.style.zIndex = "";
        }
        const start = part.trackHeight + 16;
        const end = -part.copyHeight - 16;
        part.copy.style.transform = "translate3d(0," + (start + (end - start) * local).toFixed(1) + "px,0)";
        part.copy.style.opacity = "1";
      }
    });
    dots.forEach((dot, i) => dot.setAttribute("aria-current", String(i === current)));
  }
  function requestMotion() {
    if (!frame && story && !motionPaused()) {
      frame = requestAnimationFrame(drawStory);
    }
  }
  function configureMotion() {
    document.documentElement.classList.toggle("motion-paused", motionPaused());
    motionButtons.forEach((button) => {
      button.hidden = false;
      button.disabled = media.matches;
      button.setAttribute("aria-pressed", String(motionPaused()));
      button.querySelector("[data-motion-label]").textContent = media.matches
        ? "端末設定で静止表示中"
        : readingMode
          ? "動きのある表示に戻す"
          : "静止して読む";
    });
    if (story) {
      story.classList.toggle("motion-enabled", !motionPaused());
      if (motionPaused()) {
        scenes.forEach((scene) => {
          scene.style.transform = "";
          scene.style.opacity = "";
          scene.style.zIndex = "";
          const backdrop = scene.querySelector(".v2-scene-backdrop");
          if (backdrop) {
            backdrop.style.opacity = "";
            backdrop.style.zIndex = "";
          }
          scene.querySelector("img").style.transform = "";
          scene.querySelector("img").style.opacity = "";
          scene.querySelector("img").style.zIndex = "";
          scene.querySelector(".v2-scene-copy").style.transform = "";
          scene.querySelector(".v2-scene-copy").style.opacity = "";
        });
      } else {
        syncDimensions();
      }
    }
    if (motionPaused()) {
      reveals.forEach((el) => el.classList.add("is-visible"));
    }
  }
  dots.forEach((dot) =>
    dot.addEventListener("click", () => {
      const i = Number(dot.dataset.sceneGo);
      const distance = Math.max(0, story.offsetHeight - stage.offsetHeight);
      const y =
        window.scrollY + story.getBoundingClientRect().top - headerHeight + distance * ((i + 0.5) / scenes.length);
      window.scrollTo({ top: y, behavior: motionPaused() ? "auto" : "smooth" });
    })
  );
  motionButtons.forEach((button) =>
    button.addEventListener("click", () => {
      readingMode = !readingMode;
      try {
        localStorage.setItem("lumirize-reading-mode", readingMode ? "static" : "motion");
      } catch {
        /* The choice still works for this page. */
      }
      configureMotion();
      if (button.closest(".v2-story-controls")) {
        motionButtons[0]?.focus({ preventScroll: true });
        document.querySelector(".v2-story-intro")?.scrollIntoView({ behavior: "instant", block: "start" });
      }
    })
  );
  configureMotion();
  window.addEventListener("scroll", requestMotion, { passive: true });
  window.addEventListener("resize", syncDimensions, { passive: true });
  window.addEventListener("pageshow", syncDimensions);
  document.fonts?.ready.then(syncDimensions);
  if (media.addEventListener) {
    media.addEventListener("change", configureMotion);
  } else {
    media.addListener(configureMotion);
  }

})();
