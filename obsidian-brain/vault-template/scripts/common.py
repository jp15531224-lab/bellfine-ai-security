"""import_external_brain.py / ai_export.py の共通処理（Python 3.8+ 標準ライブラリのみ）。"""
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
VAULT = Path(__file__).resolve().parent.parent
CONFIG_PATH = VAULT / "scripts" / "config.json"
STATE_DIR = VAULT / ".claude" / "state"


def now_jst() -> datetime:
    return datetime.now(JST)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(
            f"設定ファイルがありません: {CONFIG_PATH}\n"
            "setup.sh を実行するか、scripts/config.example.json をコピーして作成してください。"
        )
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    for key in ("external_brain_dir", "export_dir"):
        if cfg.get(key):
            cfg[key] = os.path.expanduser(cfg[key])
    return cfg


def load_state(name: str) -> dict:
    path = STATE_DIR / name
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_state(name: str, data: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def parse_frontmatter(text: str) -> dict:
    """簡易 YAML パーサ（key: value の1階層のみ）。"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "-")):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip("'\"")
    return meta


def safe_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|#^\[\]]', "_", name).strip() or "untitled"
