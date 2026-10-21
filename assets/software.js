// Посадочная программы: прорисовка листа и блок «Как работает» — камера едет по настоящему кадру,
// потом рисуется выноска. На широком экране блок держится на месте и шаги меняет прокрутка,
// на узком каждая фигура проигрывается, когда появляется на экране.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const sheet = document.querySelector('.sw-sheet');
  if (sheet) {
    requestAnimationFrame(() => requestAnimationFrame(() => sheet.classList.add('go')));
    if (!reduce) {
      let ticking = false;
      addEventListener('scroll', () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
          const r = sheet.getBoundingClientRect();
          sheet.style.setProperty('--p', Math.min(1, Math.max(0, -r.top / Math.max(1, r.height))).toFixed(3));
          ticking = false;
        });
      }, { passive: true });
    }
  }

  const how = document.querySelector('.sw-how');
  if (!how) return;
  const track = how.querySelector('.how-track');
  const items = [...how.querySelectorAll('.how-item')];
  const figs = items.map((it) => it.querySelector('.how-fig'));
  const timers = new Map();

  // камера въезжает с общего или чуть более широкого плана, когда встала — рисуется выноска
  const play = (fig) => {
    (timers.get(fig) || []).forEach(clearTimeout);
    if (reduce) { fig.classList.add('marked'); return; }
    const wide = fig.classList.contains('wide');
    fig.classList.remove('marked');
    fig.classList.add('enter');
    void fig.offsetWidth;
    timers.set(fig, [
      setTimeout(() => fig.classList.remove('enter'), wide ? 900 : 260),
      setTimeout(() => fig.classList.add('marked'), wide ? 2650 : 1950),
    ]);
  };
  const park = (fig) => {
    (timers.get(fig) || []).forEach(clearTimeout);
    fig.classList.remove('marked');
    if (!reduce) fig.classList.add('enter');
  };

  let cur = null;
  const show = (i, run) => {
    if (cur === i) return;
    cur = i;
    items.forEach((it, j) => it.classList.toggle('on', j === (i < 0 ? 0 : i)));
    if (i < 0) { figs.forEach(park); return; }
    if (run) play(figs[i]);
  };
  const onScroll = () => {
    const r = track.getBoundingClientRect();
    if (r.top > innerHeight * 0.25) { show(-1, false); return; }
    const p = Math.min(0.9999, Math.max(0, -r.top / Math.max(1, r.height - innerHeight)));
    show(Math.floor(p * items.length), true);
  };

  const desk = matchMedia('(min-width: 961px)');
  let io = null;
  const setMode = () => {
    removeEventListener('scroll', onScroll);
    if (io) { io.disconnect(); io = null; }
    cur = null;
    if (desk.matches) {
      how.classList.add('pinned');
      addEventListener('scroll', onScroll, { passive: true });
      onScroll();
      return;
    }
    how.classList.remove('pinned');
    items.forEach((it) => it.classList.remove('on'));
    if (reduce || !('IntersectionObserver' in window)) { figs.forEach((f) => f.classList.add('marked')); return; }
    figs.forEach(park);
    io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (!e.isIntersecting) return;
      play(e.target);
      io.unobserve(e.target);
    }), { threshold: 0.45 });
    figs.forEach((f) => io.observe(f));
  };
  desk.addEventListener('change', setMode);
  setMode();
})();
