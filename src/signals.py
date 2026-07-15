"""
signals.py — Từ điển tín hiệu tài chính dùng chung cho evidence_extractor và
forecast_model (trước đây mỗi file giữ một danh sách riêng, dễ lệch nhau).

Mở rộng các nhóm signal phổ biến (beat earnings, buyback, acquisition, SEC
investigation, layoffs, guidance cut...) để mỗi bài báo bắt được NHIỀU evidence
hơn thay vì chỉ "profit"/"grow".

Cơ chế khớp: quét cụm DÀI trước và "chiếm span" (span-consuming) để cụm dài,
đặc thù thắng cụm ngắn — nhờ đó "debt increase" (tiêu cực) không bị tính nhầm
thành "increase" (tích cực), "guidance cut" không thành "guidance", v.v.
Vẫn dùng so khớp chuỗi con (không ràng biên từ) để "grow" bắt được "growth",
"investigat" bắt "investigation", "recall" bắt "recalls" — giữ tương thích ngược.
"""
from __future__ import annotations

# --------------------------------------------------------------------------- #
# Danh mục tín hiệu (đã gộp bộ cũ + các nhóm signal phổ biến mới)
# --------------------------------------------------------------------------- #
POSITIVE_SIGNALS = [
    # cụm nhiều từ / đặc thù (khớp trước)
    "beat earnings", "earnings beat", "record revenue", "raised guidance",
    "dividend increase", "share buyback", "analyst upgrade",
    "strategic partnership", "new contract", "fda approval",
    "production increase",
    # đơn từ / rút gọn
    "buyback", "acquisition", "partnership", "contract", "upgrade",
    "expansion", "approval", "dividend",
    "profit", "growth", "grow", "strong", "increase", "surge", "beat",
    "exceed", "gain", "expand", "record", "win",
]

NEGATIVE_SIGNALS = [
    # cụm nhiều từ / đặc thù (khớp trước)
    "earnings miss", "missed earnings", "guidance cut", "lowered guidance",
    "analyst downgrade", "sec investigation", "accounting fraud",
    "debt increase", "ceo resign", "production delay", "job cuts",
    "steps down",
    # đơn từ / rút gọn
    "downgrade", "investigation", "investigat", "probe", "fraud", "lawsuit",
    "bankruptcy", "recall", "layoffs", "layoff", "resignation", "resign",
    "weak", "decline", "drop", "miss", "loss", "fall", "decrease", "strike",
    "delay", "disrupt", "fine", "face",
]

POSITIVE_SET = {s.lower() for s in POSITIVE_SIGNALS}
NEGATIVE_SET = {s.lower() for s in NEGATIVE_SIGNALS}

# (phrase, polarity) sắp theo độ dài giảm dần -> cụm dài khớp & chiếm span trước
_ALL_SORTED = sorted(
    [(s.lower(), 1) for s in POSITIVE_SIGNALS]
    + [(s.lower(), -1) for s in NEGATIVE_SIGNALS],
    key=lambda x: -len(x[0]),
)


def _dedup(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def extract_signals(text: str) -> tuple[list[str], list[str]]:
    """Trả về (pro, con): các cụm tín hiệu tích cực / tiêu cực xuất hiện trong text.

    Không trùng lặp, không chồng span (cụm dài thắng cụm ngắn), sắp theo vị trí
    xuất hiện để evidence dễ đọc.
    """
    t = str(text).lower()
    taken = [False] * (len(t) + 1)
    hits: list[tuple[int, str, int]] = []

    for phrase, pol in _ALL_SORTED:
        start = t.find(phrase)
        while start != -1:
            end = start + len(phrase)
            if not any(taken[start:end]):
                for i in range(start, end):
                    taken[i] = True
                hits.append((start, phrase, pol))
            start = t.find(phrase, start + 1)

    hits.sort(key=lambda x: x[0])
    pro = _dedup([p for _, p, pol in hits if pol == 1])
    con = _dedup([p for _, p, pol in hits if pol == -1])
    return pro, con
