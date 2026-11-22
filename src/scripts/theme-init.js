/**
 * Theme. Runs early to avoid flash; persisted in localStorage.
 * Default is light unless the visitor has chosen otherwise.
 */
(function () {
  const root = document.documentElement;
  const stored = localStorage.getItem('wsmc-theme');
  const theme = stored === 'dark' ? 'dark' : 'light';
  root.setAttribute('data-theme', theme);
})();
