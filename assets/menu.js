// Липкая шапка появляется после первого экрана; круглая кнопка открывает разделы.
// На посадочных программ (body.sw) шапка видна сразу.
(() => {
  const bar = document.getElementById('bar');
  const btn = bar && bar.querySelector('.index');
  const menu = document.getElementById('index-menu');
  if (!bar || !btn || !menu) return;

  const always = document.body.classList.contains('sw');
  const onScroll = () => bar.classList.toggle('show', always || scrollY > innerHeight * 0.65);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // шапка остаётся над меню: её кнопка и открывает, и закрывает
  const setOpen = (open, fromKeyboard = false) => {
    menu.hidden = !open;
    btn.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
    if (open && fromKeyboard) menu.querySelector('a').focus();
  };
  // detail === 0 — нажали Enter или пробел: фокус в меню; при касании рамки фокуса не нужно
  btn.addEventListener('click', (e) => setOpen(menu.hidden, e.detail === 0));
  menu.addEventListener('click', (e) => { if (e.target.closest('a') || e.target === menu) setOpen(false); });
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && !menu.hidden) { setOpen(false); btn.focus(); } });
})();
