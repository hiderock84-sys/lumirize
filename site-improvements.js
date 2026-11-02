(() => {
  const bar = document.querySelector('.mobile-cta');
  if (!bar || typeof ResizeObserver !== 'function') return;
  new ResizeObserver(entries => {
    const height = entries[0].target.getBoundingClientRect().height;
    if (height > 0) document.documentElement.style.setProperty('--consultation-bar-height', `${Math.ceil(height)}px`);
  }).observe(bar);
})();
