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
  let selected = films[0].dataset.film;
  let opener = null;
  let savedY = null;
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
    const link = event.target.closest('[data-story-play]');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const film = link.closest('[data-film]');
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
    player.play().catch(() => { if (modal.open) error.hidden = false; });
  });
  modal.querySelector('[data-story-close]').addEventListener('click', () => modal.close());
  modal.addEventListener('click', event => {
    const rect = modal.getBoundingClientRect();
    if (event.target === modal && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) modal.close();
  });
  modal.addEventListener('close', () => {
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
