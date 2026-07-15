"""
run_pipeline.py — Agentic SDLC orchestrator (đề mục 10, AC-09).

Điều phối 4 "agent" chạy tuần tự; sau mỗi bước kiểm một Quality Gate và ghi lại
Agentic Trace (JSONL). Nếu một gate FAIL, pipeline dừng và chờ Human Review.

    Retriever → Extractor → Forecast → Faithfulness
       │gate       │gate      │gate        │gate
   no-leakage   schema    domain+range   metrics

Cách chạy:
    python src/run_pipeline.py            # chạy full pipeline, ghi outputs/agentic_trace.jsonl
    python src/run_pipeline.py --show     # in lại trace của lần chạy gần nhất
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Cho phép import các module anh em trong src/ dù chạy script hay bị import lại
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Console Windows mặc định cp1252 -> ép UTF-8 để in được tiếng Việt
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8")
        except Exception:
            pass

import pandas as pd

from agentic_trace import Tracer, load_trace
from retriever import TemporalRetriever
from evidence_extractor import EvidenceExtractor
from forecast_model import ForecastModel
from faithfulness_check import FaithfulnessCheck
from faithfulness_metrics import FaithfulnessEvaluator

DATA = "data/sample_news_price.csv"
VALID = "outputs/valid_news.csv"
INVALID = "outputs/invalid_future_news.csv"
EVID = "outputs/evidence_results.csv"
PRED = "outputs/prediction_results.csv"
CF = "outputs/faithfulness_check_results.csv"
FAITH = "outputs/faithfulness_results.csv"
TRACE = "outputs/agentic_trace.jsonl"

CLASSES = {"UP", "DOWN", "HOLD"}


def run(data: str = DATA, trace_path: str = TRACE, approver=None):
    """Chạy toàn bộ pipeline có kiểm gate. Trả về (ok, entries).

    approver: callable() -> bool cho bước Human Review (phê duyệt phát hành).
      - None (mặc định): chạy tự động, gate người = PENDING (chưa ai duyệt).
      - callable trả True/False: PASS (duyệt) / BLOCKED (từ chối).
    ok: True nếu KHÔNG có Quality Gate nào FAIL (tách bạch với việc người đã duyệt hay chưa).
    """
    tracer = Tracer(trace_path)
    ok = True

    # ---------- Agent 1: Temporal Retriever ---------- #
    retr = TemporalRetriever(data)
    valid, invalid = retr.export_results(VALID, INVALID)
    leak_in_valid = int(
        (pd.to_datetime(valid["news_time"]) > pd.to_datetime(valid["forecast_time"])).sum()
    )
    gate = leak_in_valid == 0
    ok &= gate
    tracer.log(
        "RetrieverAgent", "Lọc tin theo thời gian (temporal)",
        "PASS" if gate else "FAIL",
        {"total": len(valid) + len(invalid), "valid": len(valid),
         "leakage_removed": len(invalid), "leak_in_valid": leak_in_valid},
        "Quality Gate — No temporal leakage: mọi tin hợp lệ đều có news_time ≤ forecast_time."
        if gate else "Gate FAIL: còn tin rò rỉ thời gian trong tập valid.",
    )
    if not gate:
        return _finish(tracer, ok, approver)

    # ---------- Agent 2: Evidence Extractor ---------- #
    ev = EvidenceExtractor(VALID).export(EVID)
    need = {"evidence_text", "sentiment", "expected_direction"}
    gate = need.issubset(ev.columns)
    ok &= gate
    with_ev = int((ev["evidence_text"].astype(str).str.strip().str.len() > 0).sum())
    tracer.log(
        "ExtractorAgent", "Trích xuất & phân loại evidence",
        "PASS" if gate else "FAIL",
        {"rows": len(ev), "with_evidence": with_ev,
         "coverage": round(with_ev / max(len(ev), 1), 3)},
        "Quality Gate — Schema: đủ cột evidence_text/sentiment/expected_direction."
        if gate else "Gate FAIL: thiếu cột evidence.",
    )
    if not gate:
        return _finish(tracer, ok, approver)

    # ---------- Agent 3: Forecast Model ---------- #
    fm = ForecastModel(EVID)
    fm.run()
    accuracy, _cm = fm.evaluate()
    fm.export(PRED)
    pred = pd.read_csv(PRED)
    domain_ok = set(pred["prediction"].unique()).issubset(CLASSES)
    conf_ok = bool(pred["confidence"].between(0, 1).all())
    gate = domain_ok and conf_ok
    ok &= gate
    tracer.log(
        "ForecastAgent", "Dự báo UP/DOWN/HOLD + confidence",
        "PASS" if gate else "FAIL",
        {"n": len(pred), "accuracy": round(float(accuracy), 4),
         "pred_domain_ok": domain_ok, "confidence_in_range": conf_ok,
         "confidence_levels": sorted(pred["confidence"].round(2).unique().tolist())},
        "Quality Gate — Domain: prediction ∈ {UP,DOWN,HOLD} và confidence ∈ [0,1]."
        if gate else "Gate FAIL: prediction/confidence ngoài miền hợp lệ.",
    )
    if not gate:
        return _finish(tracer, ok, approver)

    # ---------- Agent 4: Faithfulness ---------- #
    FaithfulnessCheck(PRED, VALID).run_experiments(CF)
    fe = FaithfulnessEvaluator(PRED, CF)
    fe.evaluate()
    fe.export(FAITH)
    f = pd.read_csv(FAITH)
    need_m = {"evidence_support", "temporal_validity", "confidence_drop"}
    es = float(f["evidence_support"].mean())
    tv = float(f["temporal_validity"].mean())
    cd = float(f["confidence_drop"].mean())
    gate = need_m.issubset(f.columns) and 0 <= tv <= 1 and 0 <= es <= 1
    ok &= gate
    tracer.log(
        "FaithfulnessAgent", "Đánh giá faithfulness (remove cited evidence)",
        "PASS" if gate else "FAIL",
        {"evidence_support": round(es, 3), "temporal_validity": round(tv, 3),
         "confidence_drop": round(cd, 3),
         "faithful_ratio": round(float((f["confidence_drop"] >= 0.1).mean()), 3)},
        "Quality Gate — Metrics: tính đủ 3 chỉ số faithfulness trong [0,1]."
        if gate else "Gate FAIL: thiếu/sai chỉ số faithfulness.",
    )

    return _finish(tracer, ok, approver)


def _finish(tracer: Tracer, ok: bool, approver=None):
    passed = sum(1 for e in tracer.entries if e["status"] == "PASS")
    metrics = {"gates_passed": passed, "gates_total": len(tracer.entries)}

    if not ok:
        # Một Quality Gate đã FAIL -> chặn, cần con người xử lý
        status = "BLOCKED"
        reflection = "Có Quality Gate FAIL — chặn, cần con người xử lý trước khi tiếp tục."
    elif approver is None:
        # Chạy tự động: KHÔNG tự nhận là đã được duyệt (trung thực)
        status = "PENDING"
        reflection = ("Các Quality Gate đã xanh — ĐANG CHỜ người duyệt. "
                      "Chạy `--interactive` để phê duyệt thật (human-in-the-loop).")
    else:
        # Có con người phê duyệt (interactive): hiện tóm tắt gate trước khi hỏi
        print("\n" + "-" * 60)
        print("  CHỜ NGƯỜI DUYỆT — tóm tắt Quality Gate:")
        for e in tracer.entries:
            print(f"    {e['status']:>4} · {e['role']} — {e['task']}")
        print("-" * 60)
        approved = bool(approver())
        status = "PASS" if approved else "BLOCKED"
        reflection = ("Người duyệt đã PHÊ DUYỆT phát hành kết quả."
                      if approved else "Người duyệt TỪ CHỐI phát hành.")

    tracer.log("HumanReviewGate", "Cổng duyệt của con người (Human Review)",
               status, metrics, reflection)
    return ok, tracer.entries


# --------------------------------------------------------------------------- #
# In trace ra terminal (bảng gọn)
# --------------------------------------------------------------------------- #
def print_trace(entries: list[dict]) -> None:
    print("\n" + "=" * 74)
    print("  AGENTIC SDLC — TRACE")
    print("=" * 74)
    marks = {"PASS": "✅", "BLOCKED": "🔵", "PENDING": "⏳", "FAIL": "❌"}
    for e in entries:
        mark = marks.get(e["status"], "•")
        metrics = "  ".join(f"{k}={v}" for k, v in e["metrics"].items())
        print(f"{mark} [{e['step']}] {e['role']:<18} · {e['task']}")
        if metrics:
            print(f"      {metrics}")
        print(f"      ↳ {e['reflection']}")
    overall = entries[-1]["status"] if entries else "—"
    print("-" * 74)
    print(f"  Kết quả: {overall}  ·  trace: {TRACE}")
    print("=" * 74 + "\n")


def _prompt_approval() -> bool:
    """Human Review thật: hiện lời nhắc, đọc y/N từ bàn phím."""
    try:
        ans = input("\n>>> Phê duyệt phát hành kết quả? [y/N]: ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes")


def main() -> None:
    ap = argparse.ArgumentParser(description="Agentic SDLC orchestrator")
    ap.add_argument("--show", action="store_true", help="Chỉ in lại trace gần nhất")
    ap.add_argument("--interactive", action="store_true",
                    help="Dừng chờ người duyệt (human-in-the-loop) trước khi chốt")
    ap.add_argument("--data", default=DATA)
    args = ap.parse_args()

    if args.show:
        entries = load_trace(TRACE)
        if not entries:
            print("Chưa có trace. Chạy `python src/run_pipeline.py` trước.")
            return
        print_trace(entries)
        return

    approver = _prompt_approval if args.interactive else None
    ok, entries = run(args.data, approver=approver)
    print_trace(entries)

    final = entries[-1]["status"] if entries else "FAIL"
    # PASS (đã duyệt) hoặc PENDING (chờ duyệt) coi là chạy thành công; BLOCKED/FAIL -> lỗi
    sys.exit(0 if final in ("PASS", "PENDING") else 1)


if __name__ == "__main__":
    main()
