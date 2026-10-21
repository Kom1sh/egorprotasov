"""Чертежи программ для посадочных: «машина» каждой программы в духе патентного листа.

Линии с классом ln прорисовываются по очереди (--d от 0 до 5), выноски 1–6 совпадают с легендой
на странице. Миниатюра (thumb) — тот же чертёж без выносок и без движения: для главной,
комплекта листов и превью в соцсетях.
"""
import math
import random

VIEW = "0 0 640 560"


class _Pen:
    """Собирает SVG одного чертежа. motion=False убирает движущиеся детали, calls=False — выноски."""

    def __init__(self, slug, *, motion=True, calls=True):
        self.slug, self.motion, self.calls = slug, motion, calls
        self.out, self.defs = [], []

    def ln(self, d, n, cls=""):
        c = "ln" + (f" {cls}" if cls else "")
        self.out.append(f'<path class="{c}" style="--d:{n}" pathLength="1" d="{d}"/>')

    def ring(self, cx, cy, r, n, cls="thin"):
        self.ln(f"M{cx - r} {cy}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0", n, cls)

    def raw(self, s):
        self.out.append(s)

    def moving(self, s):
        """Деталь, которая живёт только на странице: в миниатюре её нет."""
        if self.motion:
            self.out.append(s)

    def text(self, x, y, s, cls="eng", extra=""):
        self.out.append(f'<text class="{cls}" x="{x}" y="{y}"{extra}>{s}</text>')

    def call(self, n, x1, y1, bx, by, d):
        """Выноска: линия от детали к кружку с номером. Линия обрывается на краю кружка."""
        if not self.calls:
            return
        r = 12
        dx, dy = bx - x1, by - y1
        k = math.hypot(dx, dy) or 1
        ex, ey = bx - dx / k * r, by - dy / k * r
        self.out.append(
            f'<g class="call" data-n="{n}">'
            f'<path class="ln thin" style="--d:{d}" pathLength="1" d="M{x1} {y1}L{ex:.1f} {ey:.1f}"/>'
            f'<path class="ln thin" style="--d:{d}" pathLength="1" d="M{bx - r} {by}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0"/>'
            f'<text class="num" style="--d:{d}" x="{bx}" y="{by}">{n}</text></g>')

    def svg(self, label):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg class="machine m-{self.slug}" viewBox="{VIEW}" role="img" aria-label="{label}">'
                f'{defs}{"".join(self.out)}</svg>')


def _ground(p, x0, x1, y, n):
    p.ln(f"M{x0} {y}H{x1}", n)
    p.ln("".join(f"M{x} {y}l-10 12" for x in range(x0 + 8, x1 + 1, 20)), n, "hatch")


# ——— EMD Finder: воронка, два сита, фокус, табличка домена, карта страниц ———

def emd_finder(motion=True, calls=True):
    p = _Pen("emd-finder", motion=motion, calls=calls)
    # станина и основание
    p.ln("M118 58V528M482 58V528", 0)
    p.ln("M110 58H126M474 58H490", 0, "thin")
    _ground(p, 88, 552, 528, 0)
    # 1 воронка с темой
    p.ln("M170 74A130 18 0 0 1 430 74A130 18 0 0 1 170 74Z", 0)
    p.ln("M170 74L272 170M430 74L328 170", 0)
    p.ln("M412 86L330 164M396 90L332 152M380 92L336 140", 1, "hatch")
    p.ln("M272 170A28 5 0 0 0 328 170M272 170V194M328 170V194M272 194A28 5 0 0 0 328 194", 1)
    p.ln("M126 74H170M430 74H474", 1, "thin")
    # 2 первое сито: спрос
    p.ln("M150 236A150 20 0 0 1 450 236A150 20 0 0 1 150 236Z", 1)
    p.ln("M150 236V252M450 236V252M150 252A150 20 0 0 0 450 252", 1)
    p.ln("M126 244H150M450 244H474", 2, "thin")
    holes = [(196, 232), (226, 228), (256, 226), (286, 225), (316, 225), (346, 226), (376, 228), (406, 232),
             (210, 242), (240, 245), (270, 246), (300, 246), (330, 246), (360, 245), (390, 242)]
    p.ln("".join(f"M{x} {y}a4 1.6 0 1 0 8 0a4 1.6 0 1 0 -8 0" for x, y in holes), 2, "thin")
    # 3 второе сито: чистка
    p.ln("M180 314A120 16 0 0 1 420 314A120 16 0 0 1 180 314Z", 2)
    p.ln("M180 314V328M420 314V328M180 328A120 16 0 0 0 420 328", 2)
    p.ln("M126 320H180M420 320H474", 3, "thin")
    holes2 = [(240, 311), (290, 308), (340, 309), (268, 320), (318, 321), (366, 318)]
    p.ln("".join(f"M{x} {y}a3 1.2 0 1 0 6 0a3 1.2 0 1 0 -6 0" for x, y in holes2), 3, "thin")
    # 4 фокус: один сильный запрос
    p.ln("M270 396a30 30 0 1 0 60 0a30 30 0 1 0 -60 0M282 396a18 18 0 1 0 36 0a18 18 0 1 0 -36 0", 3)
    p.ln("M300 360V374M300 418V432M264 396H278M322 396H336", 3, "thin")
    p.ln("M126 396H270M330 396H474", 4, "thin")
    # 5 табличка домена
    p.raw('<rect class="tint" x="206" y="452" width="188" height="40" rx="4"/>')
    p.ln("M210 452H390a4 4 0 0 1 4 4V488a4 4 0 0 1 -4 4H210a4 4 0 0 1 -4 -4V456a4 4 0 0 1 4 -4Z", 4)
    p.ln("M216 458a2 2 0 1 0 4 0a2 2 0 1 0 -4 0M380 458a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"
         "M216 486a2 2 0 1 0 4 0a2 2 0 1 0 -4 0M380 486a2 2 0 1 0 4 0a2 2 0 1 0 -4 0", 4, "thin")
    p.text(300, 476, "КЛЮЧ.COM", extra=' text-anchor="middle"')
    p.ln("M300 432V452", 4, "thin")
    # 6 карта страниц
    p.ln("M394 472H516M516 400V508M516 400H530M516 436H530M516 472H530M516 508H530", 5)
    p.ln("M530 392h56v16h-56ZM530 428h56v16h-56ZM530 464h56v16h-56ZM530 500h56v16h-56Z", 5)
    p.ln("M538 400h32M538 436h26M538 472h36M538 508h22", 5, "hatch")
    # размер: один прогон
    p.ln("M60 74V472M54 74H66M54 472H66M60 74l-4 10M60 74l4 10M60 472l-4 -10M60 472l4 -10", 5, "thin")
    p.text(50, 273, "один прогон", cls="dim", extra=' transform="rotate(-90 50 273)" text-anchor="middle"')
    # запросы: кипят в воронке, сыплются сквозь сита, один остаётся в фокусе
    jig = [(210, 60, 0), (236, 52, .3), (262, 64, .7), (290, 50, .2), (318, 62, .9), (346, 54, .5),
           (372, 62, 1.1), (398, 58, .4), (250, 96, .8), (300, 108, .1), (342, 98, .6), (296, 140, 1)]
    for x, y, dl in jig:
        p.raw(f'<circle class="pt{" jig" if motion else ""}" cx="{x}" cy="{y}" r="3" style="animation-delay:{dl}s"/>')
    for x, y, dl in [(240, 276, 0), (300, 270, .9), (356, 278, 1.7), (276, 282, 1.3), (300, 350, .5)]:
        p.moving(f'<circle class="pt fall" cx="{x}" cy="{y}" r="3" style="animation-delay:{dl}s"/>')
    p.raw('<circle class="pt key" cx="300" cy="396" r="5"/>')
    # выноски
    p.call(1, 184, 70, 96, 28, 0)
    p.call(2, 440, 240, 572, 200, 1)
    p.call(3, 412, 318, 572, 284, 2)
    p.call(4, 326, 384, 572, 346, 3)
    p.call(5, 208, 488, 88, 514, 4)
    p.call(6, 586, 396, 620, 370, 5)
    return p.svg("Чертёж EMD Finder: тема входит в воронку, два сита оставляют спрос нужной ниши, "
                 "фокус выделяет один сильный запрос, на выходе табличка с доменом и карта страниц")


# ——— strata: буровая над доменом, керн со слоями по годам, опасный слой, вердикт, цена ———

def _wave(y, a, x0=40, x1=380, seed=0):
    r = random.Random(seed)
    pts = [(x0, y + r.uniform(-a, a))]
    for i in range(1, 5):
        pts.append((x0 + (x1 - x0) * i / 4, y + r.uniform(-a, a)))
    d = f"M{pts[0][0]} {pts[0][1]:.1f}"
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        mx = (xa + xb) / 2
        d += f"C{mx:.1f} {ya:.1f} {mx:.1f} {yb:.1f} {xb} {yb:.1f}"
    return d, pts


def _hatch(kind, x0, x1, y0, y1, seed, skip=None, step=None):
    """Штриховка слоя внутри прямоугольника: точки, косые, крест, черта."""
    r = random.Random(seed)
    out = []
    x = x0 + 6
    while x < x1 - 6:
        y = y0 + 6 + r.uniform(0, 8)
        while y < y1 - 6:
            if not (skip and skip[0] - 6 < x < skip[1] + 6):
                if kind == "dot":
                    out.append(f"M{x:.0f} {y:.0f}h0.6")
                elif kind == "slash":
                    out.append(f"M{x:.0f} {y + 3:.0f}l6 -6")
                elif kind == "back":
                    out.append(f"M{x:.0f} {y - 3:.0f}l6 6")
                elif kind == "cross":
                    out.append(f"M{x - 3:.0f} {y - 3:.0f}l6 6M{x + 3:.0f} {y - 3:.0f}l-6 6")
                elif kind == "dash":
                    out.append(f"M{x - 4:.0f} {y:.0f}h8")
            y += (step or 13) + r.uniform(0, 5)
        x += (step or 15) + r.uniform(0, 6)
    return "".join(out)


def strata(motion=True, calls=True):
    p = _Pen("strata", motion=motion, calls=calls)
    # разрез: поверхность, границы слоёв, правый срез и дно
    p.ln("M24 150H396", 0)
    p.ln("".join(f"M{x} 150l-6 -8" for x in range(30, 396, 14)), 0, "hatch")
    p.ln("M380 150V500M40 500H380", 0)
    bounds = [(205, 6, 1), (262, 6, 2), (312, 6, 3), (358, 5, 4), (420, 6, 5)]
    waves = []
    for y, a, s in bounds:
        d, pts = _wave(y, a, seed=s)
        waves.append((d, pts))
        p.ln(d, 1)
    # опасный слой: подкрашен цветом программы
    top, bot = waves[2][1], waves[3][1]
    poly = "M" + " L".join(f"{x} {y:.1f}" for x, y in top) + " L" + " L".join(f"{x} {y:.1f}" for x, y in reversed(bot)) + "Z"
    p.raw(f'<path class="tint" d="{poly}"/>')
    layers = [(150, 205, "dot"), (205, 262, "slash"), (262, 312, "dash"), (312, 358, "cross"), (358, 420, "dot"), (420, 500, "back")]
    for i, (y0, y1, kind) in enumerate(layers):
        p.ln(_hatch(kind, 40, 380, y0, y1, seed=10 + i, skip=(170, 190), step=17), 2, "hatch")
    # буровая
    p.ln("M140 150L180 40L220 150M128 150H232", 0)
    p.ln("M156 104H204M146 128H214M166 76H194", 1, "thin")
    p.ln("M156 104L214 128M204 104L146 128M166 76L204 104M194 76L156 104", 1, "thin")
    p.ln("M172 32h16v8h-16Z", 1)
    # скважина и бур
    p.ln("M174 150V470M186 150V470", 2)
    p.ln("M174 470L180 488L186 470", 2)
    p.raw(f'<path class="mv drill{" flow" if motion else ""}" d="M180 40V470"/>')
    # извлечённый керн
    p.ln("M196 34C300 -4 420 28 458 96", 2, "thin dash")
    sec = lambda y: 110 + (y - 150) * 360 / 350
    p.ln("M430 110A30 8 0 0 1 490 110A30 8 0 0 1 430 110ZM430 110V470M490 110V470M430 470A30 8 0 0 0 490 470", 3)
    p.raw(f'<path class="tint" d="M430 {sec(312):.0f}A30 8 0 0 0 490 {sec(312):.0f}V{sec(358):.0f}A30 8 0 0 1 430 {sec(358):.0f}Z"/>')
    p.ln("".join(f"M430 {sec(y):.0f}A30 8 0 0 0 490 {sec(y):.0f}" for y, _, _ in bounds), 3, "thin")
    for i, (y0, y1, kind) in enumerate(layers):
        p.ln(_hatch(kind, 430, 490, sec(y0) + 4, sec(y1), seed=30 + i, step=13), 3, "hatch")
    years = ["2026", "2021", "2017", "2014", "2011", "2008", "2004"]
    for yv, y in zip(years, [150] + [b[0] for b in bounds] + [500]):
        cy = sec(y)
        p.ln(f"M492 {cy:.0f}h8", 3, "thin")
        p.text(504, f"{cy + 3:.0f}", yv, cls="yr")
    # лупа на опасном слое
    lens = f"lens-{'p' if motion else 't'}"
    p.defs.append(f'<clipPath id="{lens}"><circle cx="574" cy="300" r="29"/></clipPath>')
    p.raw(f'<g clip-path="url(#{lens})"><circle class="tint" cx="574" cy="300" r="29"/>'
          f'<path class="ln hatch" style="--d:4" pathLength="1" d="{_hatch("cross", 542, 606, 268, 332, seed=7, step=11)}"/></g>')
    p.ring(574, 300, 30, 4, "")
    p.ln("M595 321L622 348M591 325L618 352", 4)
    p.ln("M544 300H536M500 300H492", 4, "thin")
    # вердикт: переключатель «берём / не берём»
    p.ln("M420 494h180a4 4 0 0 1 4 4v20a4 4 0 0 1 -4 4h-180a4 4 0 0 1 -4 -4v-20a4 4 0 0 1 4 -4Z", 5)
    p.ln("M510 494V522", 5, "thin")
    p.text(463, 512, "БЕРЁМ", extra=' text-anchor="middle"')
    p.text(557, 512, "НЕ БЕРЁМ", cls="eng on", extra=' text-anchor="middle"')
    p.ln("M551 528l6 -6l6 6", 5)
    p.ln("M460 470V494", 5, "thin")
    # цена: бирка, сумма закрыта
    p.ln("M60 526l12 -12h70v24h-70Z", 5)
    p.ring(76, 526, 3, 5)
    p.ln("M76 523C64 512 52 506 44 500", 5, "thin")
    p.text(92, 530, "$", cls="eng")
    p.raw('<rect class="rx" x="102" y="521" width="34" height="10" rx="2"/>')
    # выноски
    p.call(1, 70, 150, 26, 116, 0)
    p.call(2, 206, 96, 252, 60, 1)
    p.call(3, 300, 186, 300, 120, 2)
    p.call(4, 596, 278, 622, 240, 3)
    p.call(5, 604, 506, 626, 470, 4)
    p.call(6, 140, 538, 190, 546, 5)
    return p.svg("Чертёж strata: буровая над доменом, керн с историей по годам, лупа на опасном слое, "
                 "переключатель вердикта и бирка с ценой")


# ——— Site Audit: адрес, лента страниц, досмотровая рамка, три лотка, отчёт, ТЗ ———

def _page(x, y, w=26, h=34):
    f = 8
    return (f"M{x} {y}h{w - f}l{f} {f}v{h - f}h{-w}Z M{x + w - f} {y}v{f}h{f}"
            f"M{x + 5} {y + 14}h{w - 10}M{x + 5} {y + 20}h{w - 13}M{x + 5} {y + 26}h{w - 10}")


def site_audit(motion=True, calls=True):
    p = _Pen("site-audit", motion=motion, calls=calls)
    _ground(p, 40, 600, 524, 0)
    # 1 адрес сайта и загрузочный жёлоб
    p.ln("M40 64h168a5 5 0 0 1 5 5v30a5 5 0 0 1 -5 5h-168a5 5 0 0 1 -5 -5v-30a5 5 0 0 1 5 -5Z", 0)
    p.ring(60, 84, 9, 0)
    p.ln("M51 84h18M60 75c-5 6 -5 12 0 18M60 75c5 6 5 12 0 18", 0, "thin")
    p.text(78, 88, "АДРЕС САЙТА")
    p.ln("M96 104V196M120 104V196M84 196H132L116 240H100Z", 1)
    # 2 лента с роликами и опорами
    p.ln("M70 300H470A15 15 0 0 1 470 330H70A15 15 0 0 1 70 300Z", 1)
    p.ln("".join(f"M{x - 9} 315a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" for x in range(90, 461, 46)), 1, "thin")
    p.ln("M110 330V524M300 330V524M440 330V524M110 424H440", 2, "thin")
    clip = f"belt-{'p' if motion else 't'}"
    p.defs.append(f'<clipPath id="{clip}"><rect x="58" y="240" width="424" height="61"/></clipPath>')
    pages = "".join(_page(x, 266) for x in range(46, 470, 60))
    cls = "ln slide" if motion else "ln"
    p.raw(f'<g clip-path="url(#{clip})"><path class="{cls} thin" style="--d:2" pathLength="1" d="{pages}"/></g>')
    # 3 досмотровая рамка
    p.raw('<path class="tint" d="M262 330V206Q262 192 276 192H324Q338 192 338 206V330Z"/>')
    p.ln("M250 330V200Q250 180 270 180H330Q350 180 350 200V330M262 330V206Q262 192 276 192H324Q338 192 338 206V330", 2)
    p.ring(300, 166, 10, 3)
    p.ring(300, 166, 4, 3)
    p.ln("M300 176V180", 3, "thin")
    p.moving('<path class="mv scan" d="M266 214H334"/>')
    p.ln("M266 240H334M266 266H334", 3, "thin dash")
    # 4 сортировщик и три лотка
    p.ln("M482 318L520 352", 3)
    p.ln("M490 334L474 440M500 340L536 440M512 344L600 440", 3, "thin")
    for i, (x, label) in enumerate([(448, "ИСПРАВИТЬ"), (512, "ПРОВЕРИТЬ"), (576, "МЕЛОЧИ")]):
        p.ln(f"M{x} 440V476H{x + 52}V440", 4)
        p.text(x + 26, 492, label, cls="eng sm", extra=' text-anchor="middle"')
        for j in range([4, 3, 6][i]):
            p.raw(f'<circle class="pt" cx="{x + 10 + (j % 4) * 10}" cy="{470 - (j // 4) * 9}" r="3"/>')
    # 5 отчёт клиенту
    p.ln("M300 156V128H462", 4, "thin dash")
    p.ln("M470 74h70v86h-70Z", 4)
    p.ln("M476 68h70v86M482 62h70v86", 4, "thin")
    p.ln("M478 86h40M478 100h54M478 110h46M478 120h54M478 130h36M478 140h50", 5, "hatch")
    p.text(505, 176, "ОТЧЁТ", extra=' text-anchor="middle"')
    # 6 ТЗ на новые страницы
    p.ln("M552 104H570", 5, "thin")
    p.ln("M574 84h40l10 10v66h-50Z M614 84v10h10", 5)
    p.ln("M580 104h18v14h-18ZM602 104h16v14h-16ZM580 124h38v10h-38ZM580 140h26v12h-26Z", 5, "thin")
    p.text(599, 176, "ТЗ", extra=' text-anchor="middle"')
    # выноски
    p.call(1, 40, 70, 22, 36, 0)
    p.call(2, 186, 332, 206, 392, 1)
    p.call(3, 350, 226, 390, 196, 2)
    p.call(4, 628, 446, 628, 410, 3)
    p.call(5, 520, 62, 538, 30, 4)
    p.call(6, 610, 84, 618, 46, 5)
    return p.svg("Чертёж Site Audit: адрес сайта, лента со страницами, досмотровая рамка, "
                 "сортировщик на три лотка, отчёт клиенту и ТЗ на новые страницы")


DRAWINGS = {"emd-finder": emd_finder, "strata": strata, "site-audit": site_audit}


def thumb(slug):
    """Тот же чертёж без выносок и без движения."""
    return DRAWINGS[slug](motion=False, calls=False)
