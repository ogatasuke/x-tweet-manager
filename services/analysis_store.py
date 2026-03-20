import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data" / "analyses"


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _path(username: str) -> Path:
    clean = username.lstrip("@").lower()
    return DATA_DIR / f"{clean}.json"


def save(username: str, analysis: dict) -> Path:
    _ensure_dir()
    analysis["saved_at"] = datetime.now().isoformat()
    p = _path(username)
    p.write_text(json.dumps(analysis, ensure_ascii=False, indent=2))
    return p


def load(username: str) -> dict | None:
    p = _path(username)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def list_analyses() -> list[dict]:
    _ensure_dir()
    result = []
    for f in sorted(DATA_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            result.append(
                {
                    "username": data.get("username", f.stem),
                    "saved_at": data.get("saved_at", ""),
                    "summary": data.get("summary", ""),
                    "file": str(f),
                }
            )
        except Exception:
            continue
    return result
