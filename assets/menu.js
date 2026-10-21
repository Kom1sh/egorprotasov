// Липкая шапка появляется после первого экрана; круглая кнопка открывает разделы.
// На посадочных программ (body.sw) шапка видна сразу, а над калькой перекрашивается.
(() => {
  const bar = document.getElementById('bar');
  const btn = bar && bar.querySelector('.index');
  const menu = document.getElementById('index-menu');
  if (!bar || !btn || !menu) return;

  const always = document.body.classList.contains('sw');
  const toned = [...document.querySelectorAll('[data-tone]')];
  const onScroll = () => {
    bar.classList.toggle('show', always || scrollY > innerHeight * 0.65);
    if (!toned.length) return;
    // тон того блока, что сейчас под шапкой
    const y = bar.offsetHeight / 2;
    const under = toned.find((s) => { const r = s.getBoundingClientRect(); return r.top <= y && r.bottom > y; });
    bar.classList.toggle('on-paper', !!under && under.dataset.tone === 'paper');
  };
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);
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
