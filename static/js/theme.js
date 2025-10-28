// Manual theme toggle, saves preference to localStorage.
// Default: dark.

(function(){
  const html = document.getElementById('html-root') || document.documentElement;
  const btn = document.getElementById('themeToggle');

  // init from localStorage
  const saved = localStorage.getItem('site-theme');
  if (saved === 'light') {
    html.setAttribute('data-theme', 'light');
    if (btn) btn.textContent = '☾';
  } else {
    html.setAttribute('data-theme', 'dark');
    if (btn) btn.textContent = '☀';
  }

  if (!btn) return;
  btn.addEventListener('click', function(){
    const cur = html.getAttribute('data-theme') || 'dark';
    const next = cur === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('site-theme', next);
    btn.textContent = next === 'dark' ? '☀' : '☾';
  });
})();
