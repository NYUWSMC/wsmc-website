/**
 * Theme. Runs early to avoid flash; persisted in localStorage.
 * Default is light unless the visitor has chosen otherwise.
 * Re-applies on Astro view-transition swaps so theme does not flash.
 */
(function () {
  function applyTheme() {
    const root = document.documentElement;
    const stored = localStorage.getItem('wsmc-theme');
    const theme = stored === 'dark' ? 'dark' : 'light';
    root.setAttribute('data-theme', theme);
  }

  applyTheme();
  document.addEventListener('astro:after-swap', applyTheme);
})();
