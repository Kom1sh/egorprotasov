// Курсор для графиков: вертикальная линия и значения всех линий за выбранный день.
// Работает и мышью, и касанием. Данные лежат в <script type="application/json"> рядом с графиком.
(() => {
  const fmt = (v, kind) => {
    if (v === null || v === undefined) return '—';
    if (kind === 'pos') return v.toFixed(1).replace('.', ',');
    return Math.round(v).toLocaleString('ru-RU');
  };
  document.querySelectorAll('figure.chart').forEach((fig) => {
    const data = JSON.parse(fig.querySelector('.chart-data').textContent);
    const tip = fig.querySelector('.chart-tip');
    const plot = fig.querySelector('.chart-plot');
    const total = data.labels.length;
    fig.querySelectorAll('svg').forEach((svg) => {
      const x0 = +svg.dataset.x0, x1 = +svg.dataset.x1, w = +svg.dataset.w;
      const cursor = svg.querySelector('.cursor');
      // у мобильной версии может быть обрезано начало: считаем смещение по числу точек
      const offset = svg.classList.contains('mob') ? total - (+svg.dataset.n || total) : 0;
      const n = total - offset;
      const hide = () => { cursor.style.opacity = 0; tip.hidden = true; };
      const move = (e) => {
        const r = svg.getBoundingClientRect();
        const x = (e.clientX - r.left) * w / r.width;
        if (x < x0 - 4 || x > x1 + 4) { hide(); return; }
        const i = Math.max(0, Math.min(n - 1, Math.round((x - x0) / (x1 - x0) * (n - 1))));
        const px = x0 + (x1 - x0) * i / (n - 1);
        cursor.setAttribute('x1', px); cursor.setAttribute('x2', px); cursor.style.opacity = 1;
        const k = i + offset;
        tip.innerHTML = `<b>${data.labels[k]}</b>` + data.series.map((s) =>
          `<span><i style="background:${s.color}"></i>${s.name} ${fmt(s.values[k], data.kind)}</span>`).join('');
        tip.hidden = false;
        const left = px * r.width / w + (r.left - plot.getBoundingClientRect().left);
        const tw = tip.offsetWidth;
        tip.style.left = `${Math.min(Math.max(0, left + 14), plot.clientWidth - tw)}px`;
      };
      svg.addEventListener('pointermove', move);
      svg.addEventListener('pointerdown', move);
      svg.addEventListener('pointerleave', hide);
    });
  });
})();
