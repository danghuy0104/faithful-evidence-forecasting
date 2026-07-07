# Code giao diện Dashboard (Streamlit/Gradio/Dash)
from __future__ import annotations

import argparse
import os
import sys
from math import pi

# Console Windows mặc định cp1252 -> ép UTF-8 để in được tiếng Việt
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib

matplotlib.use("Agg")  # backend không cần màn hình -> export .png ổn định
import matplotlib.pyplot as plt
import pandas as pd


PRED_PATH = "outputs/prediction_results.csv"
FAITH_PATH = "outputs/faithfulness_results.csv"

PRED_COLS = [
    "ticker", "forecast_time", "news_time", "prediction", "confidence",
    "label", "evidence_text", "polarity", "expected_direction", "cited",
]
FAITH_COLS = [
    "ticker", "temporal_validity", "evidence_support", "confidence_drop",
    "confidence_original", "confidence_after_removal",
]

CLASSES = ["UP", "DOWN", "HOLD"]


# --------------------------------------------------------------------------- #
# Load
# --------------------------------------------------------------------------- #
def load_predictions(path: str = PRED_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _normalize_pred_schema(df)
    _check_cols(df, PRED_COLS, path)
    df["forecast_time"] = pd.to_datetime(df["forecast_time"])
    df["news_time"] = pd.to_datetime(df["news_time"])
    return df


def _normalize_pred_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hoá schema pipeline (forecast_model.py) về schema dashboard.

    Pipeline xuất `sentiment` và cặp `pro_evidence`/`counter_evidence`, còn
    dashboard (theo đề) mong đợi `polarity` và cờ boolean `cited`. Map lại tại
    đây để không phải sửa pipeline (nhiều module khác dùng chung CSV).
    """
    df = df.copy()

    # sentiment (negative/neutral/positive) <-> polarity
    if "polarity" not in df.columns and "sentiment" in df.columns:
        df["polarity"] = df["sentiment"]

    # cited = evidence được mô hình dùng để ra prediction, tức evidence có
    # expected_direction trùng với prediction cuối cùng (khớp dữ liệu demo).
    if "cited" not in df.columns and {"expected_direction", "prediction"} <= set(df.columns):
        df["cited"] = df["expected_direction"] == df["prediction"]

    return df


def load_faithfulness(path: str = FAITH_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _normalize_faith_schema(df)
    _check_cols(df, FAITH_COLS, path)
    return df


def _normalize_faith_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hoá schema faithfulness pipeline về schema dashboard.

    Pipeline xuất `confidence_before`/`confidence_after`, dashboard mong đợi
    `confidence_original`/`confidence_after_removal`.
    """
    df = df.copy()
    renames = {
        "confidence_before": "confidence_original",
        "confidence_after": "confidence_after_removal",
    }
    for src, dst in renames.items():
        if dst not in df.columns and src in df.columns:
            df[dst] = df[src]
    return df


def _check_cols(df: pd.DataFrame, required: list[str], path: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{path} thiếu cột: {missing}. Schema kỳ vọng: {required}")


# --------------------------------------------------------------------------- #
# Figure 1 — Prediction distribution
# --------------------------------------------------------------------------- #
def plot_prediction_distribution(pred: pd.DataFrame, outdir: str) -> str:
    # 1 dòng / 1 mẫu dự báo -> bỏ trùng theo (ticker, forecast_time)
    samples = pred.drop_duplicates(subset=["ticker", "forecast_time"])
    counts = samples["prediction"].value_counts().reindex(CLASSES, fill_value=0)

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = {"UP": "#2e7d32", "DOWN": "#c62828", "HOLD": "#757575"}
    ax.bar(counts.index, counts.values, color=[colors[c] for c in counts.index])
    for i, v in enumerate(counts.values):
        ax.text(i, v, str(int(v)), ha="center", va="bottom")
    ax.set_title("Prediction Distribution")
    ax.set_ylabel("Số mẫu")
    ax.set_xlabel("Dự báo")
    return _save(fig, outdir, "prediction_distribution.png")


# --------------------------------------------------------------------------- #
# Figure 2 — Confidence drop (gốc vs sau khi bỏ cited evidence)
# --------------------------------------------------------------------------- #
def plot_confidence_drop(faith: pd.DataFrame, outdir: str) -> str:
    df = faith.copy()
    labels = df["ticker"].astype(str).tolist()
    x = range(len(df))
    width = 0.38

    fig, ax = plt.subplots(figsize=(max(6, len(df) * 1.1), 4))
    ax.bar([i - width / 2 for i in x], df["confidence_original"],
           width, label="Gốc", color="#1565c0")
    ax.bar([i + width / 2 for i in x], df["confidence_after_removal"],
           width, label="Bỏ cited evidence", color="#ef6c00")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Confidence")
    ax.set_title("Confidence Drop khi bỏ cited evidence")
    ax.legend()
    return _save(fig, outdir, "confidence_drop.png")


# --------------------------------------------------------------------------- #
# Figure 3 — Temporal leakage warning
# --------------------------------------------------------------------------- #
def detect_leakage(pred: pd.DataFrame) -> pd.DataFrame:
    """Tin có news_time > forecast_time = lỗi dùng thông tin tương lai (mục 2.3)."""
    out = pred.copy()
    out["is_leakage"] = out["news_time"] > out["forecast_time"]
    return out


def plot_temporal_leakage_warning(pred: pd.DataFrame, outdir: str) -> str:
    flagged = detect_leakage(pred)
    n_leak = int(flagged["is_leakage"].sum())
    n_ok = int((~flagged["is_leakage"]).sum())

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(["Hợp lệ", "Leakage (tương lai)"], [n_ok, n_leak],
                  color=["#2e7d32", "#c62828"])
    for b, v in zip(bars, [n_ok, n_leak]):
        ax.text(b.get_x() + b.get_width() / 2, v, str(v), ha="center", va="bottom")
    title = "Temporal Leakage Warning"
    if n_leak:
        title += f"  ⚠ {n_leak} tin dùng thông tin tương lai"
    ax.set_title(title)
    ax.set_ylabel("Số tin")
    return _save(fig, outdir, "temporal_leakage_warning.png")


# --------------------------------------------------------------------------- #
# Figure 4 — Faithfulness radar
# --------------------------------------------------------------------------- #
def plot_faithfulness_radar(faith: pd.DataFrame, outdir: str) -> str:
    axes_labels = ["temporal_validity", "evidence_support", "confidence_drop"]
    means = [faith[a].mean() for a in axes_labels]

    angles = [n / float(len(axes_labels)) * 2 * pi for n in range(len(axes_labels))]
    means += means[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, means, color="#6a1b9a", linewidth=2)
    ax.fill(angles, means, color="#6a1b9a", alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes_labels)
    ax.set_ylim(0, 1)
    ax.set_title("Faithfulness (trung bình)", y=1.08)
    return _save(fig, outdir, "faithfulness_radar.png")


# --------------------------------------------------------------------------- #
# Bảng evidence + mô phỏng "Remove cited evidence" (kịch bản demo, mục 11)
# --------------------------------------------------------------------------- #
def evidence_table(pred: pd.DataFrame) -> pd.DataFrame:
    cols = ["ticker", "prediction", "confidence", "evidence_text",
            "polarity", "expected_direction", "cited"]
    return pred[cols].copy()


def simulate_remove_cited(faith: pd.DataFrame, threshold: float = 0.1) -> pd.DataFrame:
    """So sánh confidence trước/sau khi bỏ cited evidence cho từng ticker.

    threshold: ngưỡng confidence_drop để coi evidence là faithful (mặc định 0.1).
    """
    out = faith[["ticker", "confidence_original",
                 "confidence_after_removal", "confidence_drop"]].copy()
    out["faithful_signal"] = out["confidence_drop"] >= threshold
    return out


# --------------------------------------------------------------------------- #
# Gộp evidence nhiều tin -> 1 dự báo (dùng cho kịch bản demo 5 phút, mục 11.1)
# --------------------------------------------------------------------------- #
def compute_forecast(rows: pd.DataFrame) -> dict:
    """Gộp các tin (mỗi tin 1 dòng) thành một dự báo UP/DOWN/HOLD duy nhất.

    Bỏ phiếu theo trọng số confidence của prediction từng tin. Trả về nhãn
    thắng, confidence (tỷ lệ phiếu của nhãn thắng) và phân bố phiếu đầy đủ để
    tra confidence cho một nhãn bất kỳ (phục vụ so sánh trước/sau remove).
    """
    weights: dict[str, float] = {}
    for _, r in rows.iterrows():
        pred = str(r["prediction"])
        weights[pred] = weights.get(pred, 0.0) + float(r["confidence"])

    total = sum(weights.values())
    if total <= 0:
        return {"prediction": "HOLD", "confidence": 0.0, "weights": {}, "total": 0.0}

    prediction = max(weights, key=weights.get)
    return {
        "prediction": prediction,
        "confidence": round(weights[prediction] / total, 2),
        "weights": weights,
        "total": total,
    }


def confidence_for(forecast: dict, label: str) -> float:
    """Confidence mà forecast (từ compute_forecast) gán cho một nhãn cụ thể."""
    if forecast["total"] <= 0:
        return 0.0
    return round(forecast["weights"].get(label, 0.0) / forecast["total"], 2)


def build_rationale(forecast: dict, valid_news: pd.DataFrame) -> str:
    """Câu giải thích ngắn: vì sao mô hình chốt hướng dự báo này."""
    pred = forecast["prediction"]
    support = valid_news[valid_news["prediction"] == pred]
    against = valid_news[valid_news["prediction"] != pred]
    evs = [str(e).strip() for e in support["evidence_text"].tolist()
           if str(e).strip() and str(e).strip().lower() != "nan"]
    ev_txt = "; ".join(dict.fromkeys(evs)) if evs else "tín hiệu sentiment tổng thể"
    if pred == "HOLD":
        return (f"Tín hiệu trái chiều/cân bằng ({len(support)} tin ủng hộ, "
                f"{len(against)} tin ngược) → giữ **HOLD**.")
    return (f"**{len(support)}/{len(valid_news)}** tin ủng hộ hướng **{pred}** "
            f"(bằng chứng: _{ev_txt}_), lấn át {len(against)} tin còn lại → "
            f"chốt **{pred}** với confidence **{forecast['confidence']:.0%}**.")


# --------------------------------------------------------------------------- #
# Helpers + main
# --------------------------------------------------------------------------- #
def _save(fig, outdir: str, name: str) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def _demo_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Dữ liệu PLACEHOLDER chỉ để chạy thử dashboard. KHÔNG phải dataset của nhóm."""
    pred = pd.DataFrame([
        ["AAPL", "2025-03-12 09:00", "2025-03-11 08:30", "DOWN", 0.72, "DOWN",
         "weak iPhone sales in China", "negative", "DOWN", True],
        ["AAPL", "2025-03-12 09:00", "2025-03-12 15:30", "DOWN", 0.72, "DOWN",
         "Apple afternoon press release", "neutral", "HOLD", False],  # leakage
        ["TSLA", "2025-03-12 09:00", "2025-03-11 10:00", "DOWN", 0.81, "DOWN",
         "Tesla recalls vehicles over software", "negative", "DOWN", True],
        ["NVDA", "2025-03-12 09:00", "2025-03-11 12:00", "UP", 0.88, "UP",
         "NVIDIA unveils new AI chip", "positive", "UP", True],
    ], columns=PRED_COLS)
    faith = pd.DataFrame([
        ["AAPL", 1.0, 1.0, 0.21, 0.72, 0.51],
        ["TSLA", 1.0, 1.0, 0.26, 0.81, 0.55],
        ["NVDA", 1.0, 0.5, 0.02, 0.88, 0.86],
    ], columns=FAITH_COLS)
    return pred, faith


def build_all(pred: pd.DataFrame, faith: pd.DataFrame, outdir: str) -> list[str]:
    paths = [
        plot_prediction_distribution(pred, outdir),
        plot_confidence_drop(faith, outdir),
        plot_temporal_leakage_warning(pred, outdir),
        plot_faithfulness_radar(faith, outdir),
    ]
    return paths


def main() -> None:
    ap = argparse.ArgumentParser(description="Faithfulness visualization dashboard")
    ap.add_argument("--demo", action="store_true",
                    help="Chạy với dữ liệu placeholder (không cần CSV)")
    ap.add_argument("--outdir", default="figures", help="Thư mục lưu .png")
    ap.add_argument("--pred", default=PRED_PATH)
    ap.add_argument("--faith", default=FAITH_PATH)
    args = ap.parse_args()

    if args.demo:
        pred, faith = _demo_frames()
        print("[demo] Dùng dữ liệu placeholder, không phải dataset chính thức.")
    else:
        pred, faith = load_predictions(args.pred), load_faithfulness(args.faith)

    paths = build_all(pred, faith, args.outdir)
    print("Đã xuất:")
    for p in paths:
        print("  -", p)

    print("\n--- Mô phỏng Remove cited evidence ---")
    print(simulate_remove_cited(faith).to_string(index=False))


# --------------------------------------------------------------------------- #
# Streamlit UI (giao diện tương tác) — chạy bằng: streamlit run src/dashboard.py
# --------------------------------------------------------------------------- #
def _in_streamlit() -> bool:
    """True nếu module đang được chạy bởi Streamlit runtime (không phải test/CLI).

    suppress_warning=True để không in cảnh báo "missing ScriptRunContext" khi
    import module ngoài Streamlit (chạy test hoặc `python src/dashboard.py`).
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx(suppress_warning=True) is not None
    except Exception:
        return False


_DIR_COLOR = {"UP": "#2e7d32", "DOWN": "#c62828", "HOLD": "#f9a825"}
_DIR_ICON = {"UP": "▲", "DOWN": "▼", "HOLD": "＝"}


def _color_direction(val: str) -> str:
    return f"color:{_DIR_COLOR.get(str(val), '#757575')};font-weight:600"


# --------------------------------------------------------------------------- #
# CSS + HTML snippets cho giao diện demo
# --------------------------------------------------------------------------- #
_CSS = """
<style>
  .block-container {padding-top: 2.2rem; max-width: 1200px;}
  .hero {padding: 20px 26px; border-radius: 18px; margin-bottom: 6px;
    background: linear-gradient(120deg,#1565c0 0%,#6a1b9a 100%); color:#fff;}
  .hero h1 {margin:0; font-size: 1.7rem; font-weight: 800;}
  .hero p  {margin:.35rem 0 0; opacity:.9; font-size:.95rem;}
  .demo-step {display:flex; align-items:center; gap:12px; margin:1.6rem 0 .6rem;
    font-size:1.15rem; font-weight:700; color:#e8eaf0;}
  .demo-step .num {display:inline-flex; align-items:center; justify-content:center;
    min-width:30px; height:30px; border-radius:50%; background:#1565c0; color:#fff;
    font-size:.9rem; font-weight:700;}
  .badge {display:flex; align-items:center; gap:18px; padding:20px 26px;
    border-radius:16px; border:1px solid var(--c)55;
    background:linear-gradient(135deg,var(--c)26,var(--c)08);}
  .badge .dir {font-size:2.6rem; font-weight:800; color:var(--c); line-height:1;}
  .badge .conf {margin-left:auto; text-align:right;}
  .badge .conf .lab {font-size:.7rem; letter-spacing:1.5px; text-transform:uppercase; opacity:.7;}
  .badge .conf .val {font-size:2rem; font-weight:700; color:var(--c);}
  .pill {display:inline-block; padding:2px 10px; border-radius:999px;
    font-size:.78rem; font-weight:700; color:#fff;}
</style>
"""


def _badge_html(prediction: str, confidence: float) -> str:
    c = _DIR_COLOR.get(prediction, "#757575")
    icon = _DIR_ICON.get(prediction, "•")
    return (
        f'<div class="badge" style="--c:{c};">'
        f'<div class="dir">{icon} {prediction}</div>'
        f'<div class="conf"><div class="lab">Confidence</div>'
        f'<div class="val">{confidence:.0%}</div></div></div>'
    )


def _pill(direction: str) -> str:
    c = _DIR_COLOR.get(str(direction), "#757575")
    return f'<span class="pill" style="background:{c}">{direction}</span>'


def run_streamlit_app() -> None:
    """Giao diện dashboard theo kịch bản demo 5 phút (đề, mục 11.1)."""
    import tempfile

    import streamlit as st

    st.set_page_config(page_title="Faithful Forecasting Dashboard",
                       page_icon="📈", layout="wide")
    st.markdown(_CSS, unsafe_allow_html=True)

    def step(n: int, title: str) -> None:
        st.markdown(f'<div class="demo-step"><span class="num">{n}</span>{title}</div>',
                    unsafe_allow_html=True)

    # ---------- 1. Mở dashboard ---------- #
    st.markdown(
        '<div class="hero"><h1>📈 Faithful Evidence-Centric Financial News Forecasting</h1>'
        '<p>Kiểm chứng dự báo có thật sự <b>dựa trên bằng chứng</b> hay không — '
        'kịch bản demo 5 phút · Sinh viên 3 (Visualization & QA)</p></div>',
        unsafe_allow_html=True)

    # --- Sidebar: nguồn dữ liệu + bộ lọc --- #
    st.sidebar.header("⚙️ Cấu hình")
    mode = st.sidebar.radio(
        "Nguồn dữ liệu",
        ["outputs/*.csv (thật)", "Demo (placeholder)"],
        help="Chạy `python src/pipeline.py` để sinh outputs/*.csv thật.",
    )

    if mode.startswith("Demo"):
        pred, faith = _demo_frames()
        pred["forecast_time"] = pd.to_datetime(pred["forecast_time"])
        pred["news_time"] = pd.to_datetime(pred["news_time"])
        st.sidebar.info("Đang dùng dữ liệu placeholder (không phải dataset chính thức).")
    else:
        try:
            pred = load_predictions()
            faith = load_faithfulness()
        except FileNotFoundError:
            st.error("Chưa có `outputs/*.csv`. Hãy chạy `python src/pipeline.py` "
                     "trước, hoặc chọn chế độ **Demo** ở sidebar.")
            st.stop()
        except ValueError as e:
            st.error(f"Sai schema dữ liệu: {e}")
            st.stop()

    # ---------- 2. Chọn ticker + 3. Chọn forecast date ---------- #
    tickers = sorted(pred["ticker"].unique())
    ticker = st.sidebar.selectbox("2️⃣ Chọn ticker", tickers,
                                  index=tickers.index("AAPL") if "AAPL" in tickers else 0)

    dates = sorted(pred.loc[pred["ticker"] == ticker, "forecast_time"].unique())
    date_labels = [pd.Timestamp(d).strftime("%Y-%m-%d %H:%M") for d in dates]
    date_sel = st.sidebar.selectbox("3️⃣ Chọn thời điểm dự báo (forecast date)", date_labels)
    forecast_time = pd.Timestamp(dates[date_labels.index(date_sel)])

    threshold = st.sidebar.slider(
        "Ngưỡng faithful (confidence drop ≥)", 0.0, 1.0, 0.10, 0.01,
        help="Confidence giảm ≥ ngưỡng khi bỏ cited evidence → coi là faithful.",
    )
    st.sidebar.divider()
    st.sidebar.caption("Kịch bản demo chạy tuần tự các bước 1→10 ở khung chính.")

    # Toàn bộ tin của ticker tại forecast date đã chọn
    scope = pred[(pred["ticker"] == ticker) &
                 (pred["forecast_time"] == forecast_time)].copy()
    scope = detect_leakage(scope)
    valid_news = scope[~scope["is_leakage"]].copy()   # tin hợp lệ (đúng temporal)
    leaked_news = scope[scope["is_leakage"]].copy()   # tin dùng thông tin tương lai

    # ---------- 4. Hiển thị các tin hợp lệ trước thời điểm dự báo ---------- #
    step(4, f"Tin hợp lệ trước {date_sel} — {ticker}")
    if leaked_news.empty:
        st.success(f"✅ Không có temporal leakage: cả {len(valid_news)} tin đều "
                   f"có `news_time ≤ forecast_time`.")
    else:
        st.warning(f"⚠️ Loại **{len(leaked_news)}** tin có `news_time > forecast_time` "
                   f"(thông tin tương lai) — không đưa vào dự báo.")
    # news_text có ở dữ liệu thật; demo frames chỉ có evidence_text -> fallback
    text_col = "news_text" if "news_text" in valid_news.columns else "evidence_text"
    news_view = valid_news.assign(
        news_time=valid_news["news_time"].dt.strftime("%Y-%m-%d %H:%M"),
    )[["news_time", text_col, "polarity"]].rename(
        columns={"news_time": "Thời điểm tin", text_col: "Tin tức", "polarity": "Sentiment"})
    st.dataframe(news_view, width="stretch", hide_index=True)

    if valid_news.empty:
        st.info("Không còn tin hợp lệ nào để dự báo cho lựa chọn này.")
        st.stop()

    # ---------- 5. Hệ thống dự báo UP/DOWN/HOLD ---------- #
    forecast = compute_forecast(valid_news)
    prediction = forecast["prediction"]
    conf_before = forecast["confidence"]
    label = str(valid_news["label"].mode().iloc[0]) if "label" in valid_news else "—"

    step(5, "Dự báo của hệ thống")
    b1, b2 = st.columns([2, 1])
    with b1:
        st.markdown(_badge_html(prediction, conf_before), unsafe_allow_html=True)
    b2.metric("Nhãn thực tế (label)", label,
              delta="khớp" if prediction == label else "lệch",
              delta_color="normal" if prediction == label else "inverse")

    # ---------- 6. Hiển thị evidence và rationale ---------- #
    step(6, "Bằng chứng (evidence) & rationale")
    st.markdown(f"🧠 **Rationale:** {build_rationale(forecast, valid_news)}",
                unsafe_allow_html=True)

    valid_news["cited"] = valid_news["prediction"] == prediction
    etable = valid_news.assign(
        news_time=valid_news["news_time"].dt.strftime("%Y-%m-%d %H:%M"))[
        ["news_time", "evidence_text", "polarity", "expected_direction",
         "prediction", "confidence", "cited"]].rename(columns={
            "news_time": "Thời điểm", "evidence_text": "Evidence",
            "polarity": "Sentiment", "expected_direction": "Hướng tin",
            "prediction": "Dự báo tin", "confidence": "Conf.", "cited": "Cited"})
    st.dataframe(
        etable.style.map(_color_direction, subset=["Hướng tin", "Dự báo tin"]),
        width="stretch", hide_index=True)
    st.caption("`Cited = True`: bằng chứng ủng hộ hướng dự báo cuối (pro evidence). "
               "Các tin ngược chiều là counter-evidence.")

    # ---------- 7. Remove cited evidence + 8. So sánh confidence ---------- #
    step(7, "Kiểm chứng faithful — “Remove cited evidence”")
    remove = st.toggle("🔬 Bỏ cited evidence rồi dự báo lại", value=False,
                       help="Bỏ các tin đang chống lưng cho dự báo, xem confidence "
                            "còn giữ được hay sụp đổ.")

    remaining = valid_news[~valid_news["cited"]]
    forecast_after = compute_forecast(remaining)
    conf_after = confidence_for(forecast_after, prediction)   # confidence còn lại cho nhãn gốc
    conf_drop = round(conf_before - conf_after, 2)

    step(8, "So sánh confidence trước / sau")
    d1, d2, d3 = st.columns(3)
    d1.metric("Confidence gốc", f"{conf_before:.0%}")
    d2.metric("Sau khi bỏ cited", f"{conf_after:.0%}",
              delta=f"-{conf_drop:.0%}", delta_color="inverse")
    d3.metric("Confidence Drop", f"{conf_drop:.2f}")
    st.progress(conf_before, text=f"Trước: giữ **{prediction}** ở {conf_before:.0%}")
    if remove:
        new_dir = forecast_after["prediction"] if not remaining.empty else "—"
        st.progress(conf_after,
                    text=f"Sau: {prediction} chỉ còn {conf_after:.0%} "
                         f"→ hệ thống nghiêng về **{new_dir}**")

    # ---------- 9. Kết luận faithful hay không ---------- #
    step(9, "Kết luận: evidence có faithful không?")
    if conf_drop >= threshold:
        st.success(f"🟢 **FAITHFUL** — bỏ cited evidence làm confidence sụt "
                   f"{conf_drop:.2f} (≥ ngưỡng {threshold:.2f}). Dự báo **{prediction}** "
                   f"thật sự dựa trên bằng chứng, không phải rationale trang trí.")
    else:
        st.error(f"🔴 **CHƯA FAITHFUL** — confidence chỉ giảm {conf_drop:.2f} "
                 f"(< ngưỡng {threshold:.2f}). Mô hình vẫn tự tin dù mất bằng chứng "
                 f"→ evidence có thể chỉ là lời giải thích gán thêm.")

    # ---------- 10. Một limitation quan trọng ---------- #
    step(10, "Limitation quan trọng")
    st.warning(
        "**Bằng chứng dựa trên từ khóa (keyword-based).** Evidence được rút bằng "
        "danh sách từ khóa cảm xúc cố định, nên mô hình *faithful theo thiết kế* "
        "(bỏ từ khóa là confidence mất) nhưng **chưa hiểu ngữ cảnh/mỉa mai** và có "
        "thể **bỏ sót bằng chứng diễn đạt gián tiếp**. Với LLM hộp đen, faithful "
        "không còn được bảo đảm — đó chính là lúc bài kiểm tra *remove cited evidence* "
        "này trở nên thiết yếu.")

    # ---------- Phụ lục: biểu đồ tổng hợp toàn bộ mẫu ---------- #
    with st.expander("📊 Phụ lục — 4 biểu đồ tổng hợp toàn bộ mẫu"):
        with tempfile.TemporaryDirectory() as tmp:
            p1 = plot_prediction_distribution(pred, tmp)
            p2 = plot_confidence_drop(faith, tmp)
            p3 = plot_temporal_leakage_warning(pred, tmp)
            p4 = plot_faithfulness_radar(faith, tmp)
            g1, g2 = st.columns(2)
            g1.image(p1, caption="Prediction Distribution", width="stretch")
            g2.image(p2, caption="Confidence Drop", width="stretch")
            g3, g4 = st.columns(2)
            g3.image(p3, caption="Temporal Leakage Warning", width="stretch")
            g4.image(p4, caption="Faithfulness Radar", width="stretch")

    st.divider()
    st.caption("Chỉ phục vụ học tập.")


if _in_streamlit():
    run_streamlit_app()
elif __name__ == "__main__":
    main()
