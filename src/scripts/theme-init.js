/**
 * Theme + mobile nav. Runs early to avoid flash; persisted in localStorage.
 */
(function () {
  const root = document.documentElement;
  const stored = localStorage.getItem('wsmc-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = stored === 'light' || stored === 'dark' ? stored : prefersDark ? 'dark' : 'light';
  root.setAttribute('data-theme', theme);
})();
