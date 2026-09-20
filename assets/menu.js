// Липкая шапка появляется после первого экрана; круглая кнопка открывает разделы.
(() => {
  const bar = document.getElementById('bar');
  const btn = bar && bar.querySelector('.index');
  const menu = document.getElementById('index-menu');
  if (!bar || !btn || !menu) return;

  const onScroll = () => bar.classList.toggle('show', scrollY > innerHeight * 0.65);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  const setOpen = (open) => {
    menu.hidden = !open;
    btn.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) menu.querySelector('a').focus();
  };
  btn.addEventListener('click', () => setOpen(menu.hidden));
  menu.addEventListener('click', (e) => { if (e.target.closest('a') || e.target === menu) setOpen(false); });
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && !menu.hidden) { setOpen(false); btn.focus(); } });
})();
