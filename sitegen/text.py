"""Русская типографика и строчная разметка контента.

Контент в TOML пишется обычным текстом. Поддерживаются только ссылки
в виде [текст](адрес) и **выделение**. Всё остальное экранируется.
"""
import html
import re

NBSP = " "

# Слова, которые не должны оставаться в конце строки: предлоги, союзы, частицы.
_BIND_NEXT = (
    "а без в во для до за и из или к ко как на над не ни но о об от по под при про с со у что это"
).split()
_BIND_NEXT_RE = re.compile(
    r"(?<![\wЀ-ӿ-])(" + "|".join(_BIND_NEXT) + r") (?=\S)", re.IGNORECASE
)
# Число не отрывается от следующего слова, знака или единицы: «228 визитов», «10 языков».
_NUM_WORD_RE = re.compile(r"(\d) (?=[\wЀ-ӿ%×₽$]|\d)")
# Тире не начинает строку.
_DASH_RE = re.compile(r" —")
# Слова через дефис не рвутся: «SEO-агентство», «трек-день».
_HYPHEN_WORD_RE = re.compile(r"(?<![\wЀ-ӿ])([\wЀ-ӿ.]{1,14}-[\wЀ-ӿ]{1,16})(?![\wЀ-ӿ-])")

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")


def esc(s):
    return html.escape(str(s), quote=True)


def typo_plain(s):
    """Неразрывные пробелы в обычном тексте, без HTML внутри."""
    s = _BIND_NEXT_RE.sub(lambda m: m.group(1) + NBSP, s)
    s = _BIND_NEXT_RE.sub(lambda m: m.group(1) + NBSP, s)  # второй проход для «и в»
    s = _NUM_WORD_RE.sub(lambda m: m.group(1) + NBSP, s)
    s = _DASH_RE.sub(NBSP + "—", s)
    return s


def _segment(s):
    out = esc(typo_plain(s))
    out = _HYPHEN_WORD_RE.sub(r'<span class="nw">\1</span>', out)
    return _STRONG_RE.sub(r"<strong>\1</strong>", out)


def inline(s):
    """Строка контента → безопасный HTML со ссылками и типографикой."""
    parts, pos = [], 0
    for m in _LINK_RE.finditer(s):
        parts.append(_segment(s[pos:m.start()]))
        href = m.group(2)
        ext = href.startswith("http")
        rel = ' rel="noopener"' if ext else ""
        parts.append(f'<a href="{esc(href)}"{rel}>{_segment(m.group(1))}</a>')
        pos = m.end()
    parts.append(_segment(s[pos:]))
    return "".join(parts)


def plain(s):
    """Строка контента → чистый текст без разметки (для title, alt, meta)."""
    s = _LINK_RE.sub(r"\1", s)
    return _STRONG_RE.sub(r"\1", s)


def num(n, digits=0):
    """Число с неразрывным пробелом между разрядами: 111511 → «111 511»."""
    if digits:
        s = f"{n:,.{digits}f}".replace(",", NBSP).replace(".", ",")
    else:
        s = f"{round(n):,}".replace(",", NBSP)
    return s
