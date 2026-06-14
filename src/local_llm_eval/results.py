from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json(path: Path, data: dict[str, Any]) -> None:
    """辞書を整形済み UTF-8 JSON として書き出す。

    Args:
        path: 書き出し先 JSON ファイルのパス。
        data: JSON シリアライズ可能な辞書。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
