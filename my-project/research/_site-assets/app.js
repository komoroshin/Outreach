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
