"""Графики в духе телеметрии: тонкие линии, едва заметная сетка, значения на концах.

Правила взяты из скилла dataviz: одна ось, линии 2px, подписи цветом текста
(цвет несёт только сама линия), у каждой линии подпись на конце и легенда,
курсор со значениями при наведении, прорисовка один раз при загрузке.
"""
import datetime as dt
import json
import math

from .text import esc, num

MONTHS = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август",
          "сентябрь", "октябрь", "ноябрь", "декабрь"]
MONTHS_SHORT = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]


def nice_step(vmax, n):
    raw = vmax / n
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def ticks(vmax, n=None):
    """Деления оси: из 2–4 интервалов берём тот вариант, где верх шкалы ближе всего к максимуму."""
    best = None
    for k in ((n,) if n else (2, 3, 4)):
        step = nice_step(vmax, k)
        top = step * math.ceil(vmax / step)
        if best is None or top < best[1] - 1e-9:
            best = (step, top)
    step, top = best
    return [step * i for i in range(int(round(top / step)) + 1)], top


def _fmt(v, kind):
    if v is None:
        return "—"
    if kind == "pos":
        return f"{v:.1f}".replace(".", ",")
    return num(v)


def _path(points):
    """points: list of (x, y) or None; None разрывает линию."""
    out, pen = [], False
    for p in points:
        if p is None:
            pen = False
            continue
        x, y = p
        out.append(f"{'L' if pen else 'M'}{x:.1f},{y:.1f}")
        pen = True
    return " ".join(out)


def _month_ticks(d0, d1, short):
    first = dt.date(d0.year, d0.month, 1)
    if first < d0:
        first = dt.date(d0.year + (d0.month == 12), d0.month % 12 + 1, 1)
    out, d = [], first
    while d <= d1:
        out.append(d)
        d = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    labels = []
    for i, m in enumerate(out):
        if short:
            # на длинной оси январь подписываем годом, остальные месяцы коротко
            lab = str(m.year) if m.month == 1 else MONTHS_SHORT[m.month - 1]
        else:
            lab = MONTHS[m.month - 1]
        labels.append((m, lab))
    return labels


def _svg(cls, *, W, H, X0, X1, Y0, Y1, dates, series, kind, invert, yt, top, ymin,
         annotations, bands, month_every, short_months, fs, end_fs, name_fs, label_mode):
    n = len(dates)
    d0, d1 = dates[0], dates[-1]

    def X(i):
        return X0 + (X1 - X0) * i / (n - 1)

    def Y(v):
        if invert:
            return Y1 + (Y0 - Y1) * (v - ymin) / (top - ymin)
        return Y0 - (Y0 - Y1) * v / top

    idx = {d: i for i, d in enumerate(dates)}
    parts = []
    for b0, b1, _ in bands:
        if b0 in idx and b1 in idx:
            parts.append(f'<rect x="{X(idx[b0]):.1f}" y="{Y1}" width="{max(3, X(idx[b1]) - X(idx[b0])):.1f}" '
                         f'height="{Y0 - Y1}" class="band"/>')
    for t in yt:
        y = Y(t)
        lab = _fmt(t, kind) if kind != "pos" else f"{t:g}"
        parts.append(f'<line x1="{X0}" x2="{X1}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>'
                     f'<text x="{X0 - 10}" y="{y + fs * 0.34:.1f}" class="axis" text-anchor="end" '
                     f'style="font-size:{fs}px">{lab}</text>')
    for i, (m, lab) in enumerate(_month_ticks(d0, d1, short_months)):
        if i % month_every:
            continue
        x = X((m - d0).days) if (m - d0).days < n else X1
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{Y0}" y2="{Y0 + 5}" class="tick"/>'
                     f'<text x="{x + 5:.1f}" y="{Y0 + fs + 8:.1f}" class="axis" style="font-size:{fs}px">{esc(lab)}</text>')
    for a in annotations:
        if a["date"] not in idx:
            continue
        x = X(idx[a["date"]])
        lines = a.get("mobile" if label_mode == "mobile" else "label", a["label"])
        lines = lines if isinstance(lines, list) else [lines]
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{Y1 + 6}" y2="{Y0}" class="ann"/>')
        for k, line in enumerate(lines):
            parts.append(f'<text x="{x + 7:.1f}" y="{Y1 + 14 + k * (fs + 4):.1f}" class="ann-t" '
                         f'style="font-size:{fs}px">{esc(line)}</text>')
    for b0, b1, lab in bands:
        if lab and b0 in idx:
            lines = lab if isinstance(lab, list) else [lab]
            x = X(idx[b0])
            for k, line in enumerate(lines if label_mode != "mobile" else lines[:1]):
                parts.append(f'<text x="{x - 7:.1f}" y="{Y1 + 14 + k * (fs + 4):.1f}" class="ann-t" '
                             f'text-anchor="end" style="font-size:{fs}px">{esc(line)}</text>')

    ends = []
    for k, s in enumerate(series):
        pts = [None if v is None else (X(i), Y(v)) for i, v in enumerate(s["values"])]
        delay = f"animation-delay:{0.2 * k:.2f}s;" if k else ""
        parts.append(f'<path d="{_path(pts)}" class="trace" pathLength="1" style="stroke:{s["color"]};{delay}"/>')
        last = max((i for i, v in enumerate(s["values"]) if v is not None), default=None)
        if last is not None:
            ends.append([X(last), Y(s["values"][last]), s, s["values"][last]])

    # Подписи на концах линий не должны наезжать друг на друга.
    ends.sort(key=lambda e: e[1])
    gap = end_fs + name_fs + 8
    label_y = [e[1] for e in ends]
    for i in range(1, len(ends)):
        if label_y[i] - label_y[i - 1] < gap:
            label_y[i] = label_y[i - 1] + gap
    for (x, y, s, v), ly in zip(ends, label_y):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" class="end-dot" style="fill:{s["color"]}"/>')
        if abs(ly - y) > 6:
            parts.append(f'<line x1="{x + 6:.1f}" y1="{y:.1f}" x2="{x + 12:.1f}" y2="{ly:.1f}" class="leader"/>')
        parts.append(f'<text x="{x + 14:.1f}" y="{ly + end_fs * 0.35:.1f}" class="end-v" '
                     f'style="font-size:{end_fs}px">{_fmt(v, kind)}</text>'
                     f'<text x="{x + 14:.1f}" y="{ly + end_fs * 0.35 + name_fs + 3:.1f}" class="end-n" '
                     f'style="font-size:{name_fs}px">{esc(s["name"])}</text>')
    parts.append(f'<line x1="0" x2="0" y1="{Y1}" y2="{Y0}" class="cursor"/>')
    return (f'<svg class="{cls}" viewBox="0 0 {W} {H}" data-x0="{X0}" data-x1="{X1}" data-w="{W}" data-n="{n}" '
            f'aria-hidden="true" focusable="false">{"".join(parts)}</svg>')


def line_chart(cid, *, title, dates, series, source, kind="int", invert=False,
               annotations=(), bands=(), mobile_from=None, summary):
    """HTML-фигура с десктопной и мобильной версией графика и данными для курсора.

    dates: список dt.date подряд; series: [{name, color, values}] той же длины.
    kind: "int" — количества, "pos" — средняя позиция (ось перевёрнута).
    summary: одна фраза для экранного диктора: что показывает график.
    """
    allv = [v for s in series for v in s["values"] if v is not None]
    if invert:
        step = nice_step(max(allv) - 1, 3)
        top = step * math.ceil(max(allv) / step)
        yt = [1] + [step * i for i in range(1, int(round(top / step)) + 1)]
        ymin = 1
    else:
        yt, top = ticks(max(allv))
        ymin = 0
    widest = max(len(_fmt(t, kind) if kind != "pos" else f"{t:g}") for t in yt)
    span_days = (dates[-1] - dates[0]).days
    short = span_days > 200

    desk = _svg("desk", W=1120, H=300, X0=18 + widest * 8, X1=930, Y0=266, Y1=18,
                dates=dates, series=series, kind=kind, invert=invert, yt=yt, top=top, ymin=ymin,
                annotations=annotations, bands=bands, month_every=1, short_months=short,
                fs=12, end_fs=20, name_fs=13, label_mode="desktop")

    m_dates, m_series, m_ann, m_bands = dates, series, annotations, bands
    if mobile_from and mobile_from in dates:
        i0 = dates.index(mobile_from)
        m_dates = dates[i0:]
        m_series = [dict(s, values=s["values"][i0:]) for s in series]
        m_ann = [a for a in annotations if a["date"] >= mobile_from]
        m_bands = [b for b in bands if b[0] >= mobile_from]
    m_span = (m_dates[-1] - m_dates[0]).days
    mob = _svg("mob", W=360, H=250, X0=14 + widest * 7, X1=270, Y0=206, Y1=14,
               dates=m_dates, series=m_series, kind=kind, invert=invert, yt=yt, top=top, ymin=ymin,
               annotations=m_ann, bands=m_bands,
               month_every=1 if m_span < 130 else (2 if m_span < 300 else 3),
               short_months=m_span > 130, fs=11, end_fs=17, name_fs=11, label_mode="mobile")

    data = {
        "kind": kind,
        "labels": [d.strftime("%d.%m.%Y") for d in dates],
        "series": [{"name": s["name"], "color": s["color"],
                    "values": [None if v is None else round(v, 1 if kind == "pos" else 0) for v in s["values"]]}
                   for s in series],
    }
    legend = "".join(f'<span><i style="background:{s["color"]}"></i>{esc(s["name"])}</span>' for s in series)
    legend_html = f'<span class="chart-legend">{legend}</span>' if len(series) > 1 else ""
    return f"""<figure class="chart" id="{esc(cid)}">
  <figcaption class="chart-head"><span class="chart-title">{esc(title)}</span>{legend_html}</figcaption>
  <p class="sr-only">{esc(summary)}</p>
  <div class="chart-plot">{desk}{mob}<div class="chart-tip" hidden></div></div>
  <script type="application/json" class="chart-data">{json.dumps(data, ensure_ascii=False)}</script>
  <p class="chart-src">{esc(source)}</p>
</figure>"""


def sparkline(values, color, label):
    v = [x for x in values if x is not None]
    if len(v) < 2:
        return ""
    mx = max(v) or 1
    n = len(v)
    pts = " ".join(f"{'M' if i == 0 else 'L'}{2 + 76 * i / (n - 1):.1f},{22 - 20 * x / mx:.1f}" for i, x in enumerate(v))
    return (f'<svg class="spark" viewBox="0 0 80 24" role="img" aria-label="{esc(label)}">'
            f'<path d="{pts}" style="stroke:{color}"/></svg>')


def moving_average(values, window=7):
    out = []
    for i, x in enumerate(values):
        if x is None:
            out.append(None)
            continue
        win = [y for y in values[max(0, i - window + 1):i + 1] if y is not None]
        out.append(sum(win) / len(win))
    return out
