"""
agentic_trace.py — Agentic Trace logger (AC-09).

Ghi lại mỗi bước thực thi của pipeline dưới dạng JSONL để truy vết (audit) theo
tinh thần Agentic SDLC: mỗi dòng là một hành động của một "agent" gồm role, task,
status (PASS/FAIL), metrics và reflection.

Đặt tên module là `agentic_trace` (không phải `trace`) để tránh đè module chuẩn
`trace` của Python.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class Tracer:
    """Ghi Agentic Trace ra file JSONL (mỗi hành động = 1 dòng JSON)."""

    def __init__(self, path: str = "outputs/agentic_trace.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.entries: list[dict] = []
        self.path.write_text("", encoding="utf-8")  # làm mới mỗi lần chạy

    def log(self, role: str, task: str, status: str,
            metrics: dict | None = None, reflection: str = "") -> dict:
        """Ghi một bước. status nên là 'PASS' hoặc 'FAIL'."""
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "step": len(self.entries) + 1,
            "role": role,
            "task": task,
            "status": status,
            "metrics": metrics or {},
            "reflection": reflection,
        }
        self.entries.append(entry)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry


def load_trace(path: str = "outputs/agentic_trace.jsonl") -> list[dict]:
    """Đọc lại trace JSONL thành list dict (bỏ qua dòng rỗng/hỏng)."""
    p = Path(path)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
