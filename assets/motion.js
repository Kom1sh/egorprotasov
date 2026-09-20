// Движение: чертёж на первом экране живёт от прокрутки, секции проявляются при входе в экран.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hero = document.querySelector('.hero');

  if (hero && !reduce) {
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const r = hero.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, -r.top / Math.max(1, r.height * 0.9)));
        hero.style.setProperty('--p', p.toFixed(4));
        ticking = false;
      });
    };
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
    onScroll();
  }

  const targets = document.querySelectorAll('.proj, .chart, .c-list li, .p-list li, .life-row > *, .bio > *');
  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach((el) => el.classList.add('in'));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      io.unobserve(e.target);
    });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
  targets.forEach((el, i) => { el.classList.add('rv'); el.style.setProperty('--d', `${(i % 4) * 60}ms`); io.observe(el); });
})();
