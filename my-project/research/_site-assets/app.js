// Mobile navigation sheet. Everything else on the site is static.
(function () {
  var burger = document.querySelector('#appbar .burger');
  var nav = document.querySelector('#appbar nav');
  if (!burger || !nav) return;

  function setOpen(open) {
    nav.dataset.open = open ? 'true' : 'false';
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.textContent = open ? 'Закрыть' : 'Разделы';
  }
  setOpen(false);

  burger.addEventListener('click', function () {
    setOpen(nav.dataset.open !== 'true');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setOpen(false);
  });
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) setOpen(false);
  });
})();

// Проявление секций при прокрутке — как на остальных страницах сайта.
(function () {
  var items = document.querySelectorAll('.reveal');
  if (!items.length) return;
  if (!('IntersectionObserver' in window) ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    items.forEach(function (el) { el.classList.add('on'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('on'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -12% 0px' });
  items.forEach(function (el) { io.observe(el); });
})();
