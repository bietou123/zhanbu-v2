"""
周公解梦 (Zhou Gong Jie Meng) —— 关键词模糊匹配
===================================================
当前为种子字典（30 条左右覆盖主流），后续可扩展 dream_dict.json。
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "dream_dict.json"


@lru_cache(maxsize=1)
def _load() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def _score(query: str, keywords: list[str]) -> int:
    """简单相关度评分：完全匹配 +3，包含匹配 +1。"""
    s = 0
    for kw in keywords:
        if query == kw:
            s += 3
        elif kw in query or query in kw:
            s += 1
    return s


class JieMengService:
    @classmethod
    def search(cls, query: str, top_k: int = 5) -> dict[str, Any]:
        if not query or not query.strip():
            raise ValueError("梦境关键词不能为空")
        q = query.strip()
        data = _load()
        scored: list[tuple[int, dict]] = []
        for entry in data["entries"]:
            s = _score(q, entry["keywords"])
            if s > 0:
                scored.append((s, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [
            {**entry, "score": s}
            for s, entry in scored[:top_k]
        ]
        return {
            "query": q,
            "total_matched": len(scored),
            "results": results,
            "dict_version": data.get("version"),
            "note": "种子字典；后续可通过 data/dream_dict.json 扩充条目。",
        }

    @classmethod
    def categories(cls) -> dict[str, Any]:
        data = _load()
        cats: dict[str, int] = {}
        for e in data["entries"]:
            cats[e["category"]] = cats.get(e["category"], 0) + 1
        return {"categories": cats, "total_entries": len(data["entries"])}
