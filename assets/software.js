// Посадочная программы: кадр первого экрана проявляется линией сканирования, вырезки в «Как работает»
// выплывают при прокрутке, подпись к кадру появляется последней.
(() => {
  const hero = document.querySelector('.sw-hero');
  if (hero) requestAnimationFrame(() => requestAnimationFrame(() => hero.classList.add('go')));

  const steps = document.querySelectorAll('.sw-how .st, .sw-best .best-row');
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) {
    steps.forEach((s) => s.classList.add('in'));
    return;
  }
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in');
    io.unobserve(e.target);
  }), { rootMargin: '0px 0px -15% 0px', threshold: 0.2 });
  steps.forEach((s) => io.observe(s));
})();
