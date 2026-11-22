function initThemeToggle() {
  document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const root = document.documentElement;
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('wsmc-theme', next);
    });
  });
}

function initMenu() {
  const header = document.querySelector('[data-site-header]');
  const toggle = document.querySelector('[data-menu-toggle]');
  if (!header || !toggle) return;

  toggle.addEventListener('click', () => {
    const open = header.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.textContent = open ? 'Close' : 'Menu';
  });

  header.querySelectorAll('.site-nav a').forEach((link) => {
    link.addEventListener('click', () => {
      header.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.textContent = 'Menu';
    });
  });
}

function staggerAndReveal(nodes, observer) {
  const byParent = new Map();
  for (const el of nodes) {
    const parent = el.parentElement ?? document.body;
    if (!byParent.has(parent)) byParent.set(parent, []);
    byParent.get(parent).push(el);
  }

  for (const group of byParent.values()) {
    group.sort((a, b) => a.offsetTop - b.offsetTop || a.offsetLeft - b.offsetLeft);

    /** @type {Element[][]} */
    const rows = [];
    for (const el of group) {
      const last = rows[rows.length - 1];
      if (last && Math.abs(last[0].offsetTop - el.offsetTop) < 4) {
        last.push(el);
      } else {
        rows.push([el]);
      }
    }

    rows.forEach((row, rowIndex) => {
      row.forEach((el, colIndex) => {
        const delay =
          row.length > 1 ? colIndex * 90 : rows.length > 1 ? rowIndex * 75 : colIndex * 90;
        el.style.setProperty('--reveal-delay', `${delay}ms`);
        el.classList.add('is-visible');
        if (observer) observer.unobserve(el);
      });
    });
  }
}

function initScrollReveal() {
  const nodes = [...document.querySelectorAll('[data-reveal]')].filter(
    (el) => !el.classList.contains('is-visible'),
  );
  if (!nodes.length) return;

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) {
    nodes.forEach((el) => el.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      const toReveal = entries.filter((entry) => entry.isIntersecting).map((entry) => entry.target);
      if (!toReveal.length) return;
      staggerAndReveal(toReveal, observer);
    },
    { rootMargin: '0px 0px -10% 0px', threshold: 0.12 },
  );

  nodes.forEach((el) => observer.observe(el));
}

function markProseReveals() {
  document.querySelectorAll('[data-reveal-group]').forEach((group) => {
    group.querySelectorAll(':scope > *').forEach((child) => {
      if (!child.hasAttribute('data-reveal')) {
        child.setAttribute('data-reveal', '');
      }
    });
  });
}

function initUi() {
  markProseReveals();
  initThemeToggle();
  initMenu();
  initScrollReveal();
}

document.addEventListener('astro:page-load', initUi);
