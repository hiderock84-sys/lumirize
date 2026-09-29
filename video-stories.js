(() => {
  'use strict';
  const section = document.querySelector('[data-video-stories]');
  const modal = document.querySelector('[data-story-player]');
  if (!section || !modal || typeof modal.showModal !== 'function') return;
  const films = [...section.querySelectorAll('[data-film]')];
  const choices = section.querySelector('.story-choices');
  const selectors = [...section.querySelectorAll('[data-story-select]')];
  const smallScreen = window.matchMedia('(max-width: 760px)');
  const player = modal.querySelector('video');
  const title = modal.querySelector('#story-player-title');
  const description = modal.querySelector('[data-player-description]');
  const direct = modal.querySelector('[data-player-direct]');
  const error = modal.querySelector('.story-player__error');
  const subtitleControls = modal.querySelector('[data-player-subtitles]');
  let activeFilm = null;
  let playbackRevision = 0;
  let selected = films[0].dataset.film;
  let opener = null;
  let savedY = null;
  const play = () => {
    const revision = playbackRevision;
    player.play().catch(reason => {
      if (modal.open && revision === playbackRevision && reason.name !== 'AbortError') error.hidden = false;
    });
  };
  const updateSubtitles = (film, language, switchVideo = false) => {
    if (!film.dataset.subtitlesEn || !['ja', 'en'].includes(language)) return;
    const changed = film.dataset.subtitleLanguage !== language;
    film.dataset.subtitleLanguage = language;
    const url = language === 'en' ? film.dataset.subtitlesEn : film.dataset.subtitlesJa;
    film.querySelectorAll('[data-story-play]').forEach(link => { link.href = url; });
    film.querySelectorAll('[data-subtitle-language]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.subtitleLanguage === language));
    });
    if (activeFilm !== film) return;
    subtitleControls.querySelectorAll('[data-subtitle-language]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.subtitleLanguage === language));
    });
    direct.href = url;
    if (!switchVideo || !changed) return;
    const time = player.currentTime || 0;
    const resume = !player.paused;
    const revision = ++playbackRevision;
    player.pause();
    player.src = url;
    error.hidden = true;
    player.addEventListener('loadedmetadata', () => {
      if (revision === playbackRevision && modal.open) player.currentTime = Math.min(time, Math.max(0, player.duration - .05));
    }, {once: true});
    player.load();
    if (resume) play();
  };
  films.forEach(film => updateSubtitles(film, document.documentElement.lang === 'en' ? 'en' : 'ja'));
  subtitleControls.addEventListener('click', event => {
    const button = event.target.closest('button[data-subtitle-language]');
    if (button && activeFilm) updateSubtitles(activeFilm, button.dataset.subtitleLanguage, true);
  });
  const updateSelection = () => {
    choices.hidden = !smallScreen.matches;
    films.forEach(film => { film.hidden = smallScreen.matches && film.dataset.film !== selected; });
    selectors.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.storySelect === selected)));
  };
  selectors.forEach(button => button.addEventListener('click', () => {
    selected = button.dataset.storySelect;
    updateSelection();
  }));
  smallScreen.addEventListener('change', updateSelection);
  updateSelection();

  section.addEventListener('click', event => {
    const subtitleButton = event.target.closest('button[data-subtitle-language]');
    if (subtitleButton) {
      updateSubtitles(subtitleButton.closest('[data-film]'), subtitleButton.dataset.subtitleLanguage);
      return;
    }
    const link = event.target.closest('[data-story-play]');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const film = link.closest('[data-film]');
    activeFilm = film;
    playbackRevision++;
    subtitleControls.hidden = !film.dataset.subtitlesEn;
    updateSubtitles(film, film.dataset.subtitleLanguage || 'ja');
    modal.classList.toggle('story-player--landscape', film.dataset.orientation === 'landscape');
    opener = link;
    title.textContent = film.dataset.title;
    description.textContent = film.dataset.description;
    direct.href = link.href;
    player.poster = film.querySelector('img').src;
    player.muted = link.dataset.muted === 'true';
    player.src = link.href;
    error.hidden = true;
    savedY = window.scrollY;
    document.body.style.setProperty('--story-scroll-offset', `-${savedY}px`);
    document.documentElement.classList.add('story-player-open');
    document.body.classList.add('story-player-open');
    modal.showModal();
    play();
  });
  modal.querySelector('[data-story-close]').addEventListener('click', () => modal.close());
  modal.addEventListener('click', event => {
    const rect = modal.getBoundingClientRect();
    if (event.target === modal && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) modal.close();
  });
  modal.addEventListener('close', () => {
    playbackRevision++;
    activeFilm = null;
    player.pause();
    player.removeAttribute('src');
    player.load();
    document.body.classList.remove('story-player-open');
    document.body.style.removeProperty('--story-scroll-offset');
    if (savedY !== null) window.scrollTo({left: 0, top: savedY, behavior: 'instant'});
    savedY = null;
    document.documentElement.classList.remove('story-player-open');
    opener?.focus({preventScroll: true});
  });
  player.addEventListener('error', () => { if (modal.open) error.hidden = false; });
  document.addEventListener('visibilitychange', () => { if (document.hidden) player.pause(); });
})();
