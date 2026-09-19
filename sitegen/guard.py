"""Проверки собранных страниц перед публикацией.

1. Запрещённые слова: названия и домены клиентов, название агентства.
   Хранятся только как хеши, чтобы сам список не лежал в публичном репозитории.
   Сборка падает, если любое из них попало на страницу, в разметку или в адрес.
2. Приметы сгенерированного текста — предупреждения, сборка не падает.
"""
import hashlib
import re
import unicodedata

FORBIDDEN = {
    "9330fb0c11545854834a", "e3047de4d2c7e8815a19", "e0db2613f6ecb45eb186", "d6c5d918a71e220aab2d",
    "767dc0af7f4dfd538433", "0e4844880fd1feedb209", "0432189cbb39433a976e", "ddc40da959bba51a31df",
    "1b20f962d306a9b4a214", "4eb1067f7b4d79db3066", "b2cbf0043185db6f483d", "a251539c5620d3e6f85b",
    "17fad16ba442c7a79d0a", "29025b8eb6c80dbd25a6", "8a0b8066c1bf0f90dfa9", "76aab67479836266ef9e",
    "cda3bb739812b2cb4c05", "1a1e190f0f2d95c53b80", "13eda1044c1331f4cd96", "132c3ec6df653c586778",
    "217eb3136cba5c9cae51", "f6065ad0f9014e1b82ba", "d827decbfc2af1aacd11", "0b01abf394b05df33d12",
    "87335cfe8e103ce80b5b", "36bbaeb6c70f55d6e8af", "1da6d946a0e473acdf33", "65fde40c223eca0f3497",
    "4aae142e1e9c14e31dd6",
}

_TOKEN = re.compile(r"[a-z0-9а-я]+")
_TAGS = re.compile(r"<[^>]+>")
_SCRIPT = re.compile(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>", re.S)

STYLE_RULES = [
    ("разделитель «·»", re.compile("·")),
    ("стрелка в тексте", re.compile("[→↗←]")),
    ("конструкция «не …, а …»", re.compile(r"(?<![\wЀ-ӿ])не [^,.;:!?]{1,40}, а (?!также)", re.I)),
    ("конструкция «…, а не …»", re.compile(r", а не ", re.I)),
    ("усилитель «ровно»", re.compile(r"(?<![\wЀ-ӿ])ровно(?![\wЀ-ӿ])", re.I)),
]


def _h(s):
    return hashlib.sha256(s.encode()).hexdigest()[:20]


def _norm(s):
    return unicodedata.normalize("NFKC", s).lower().replace("ё", "е")


def forbidden_hits(text):
    toks = _TOKEN.findall(_norm(text))
    hits = set()
    for i, t in enumerate(toks):
        if _h(t) in FORBIDDEN:
            hits.add(t)
        if i + 1 < len(toks) and _h(f"{t} {toks[i + 1]}") in FORBIDDEN:
            hits.add(f"{t} {toks[i + 1]}")
    return sorted(hits)


def style_warnings(html):
    text = _TAGS.sub(" ", _SCRIPT.sub(" ", html))
    out = []
    for name, rx in STYLE_RULES:
        for m in rx.finditer(text):
            a, b = max(0, m.start() - 30), min(len(text), m.end() + 30)
            out.append(f"{name}: …{' '.join(text[a:b].split())}…")
    return out
