#!/usr/bin/env python3
"""外部脳（Google Drive「iCloud外部脳」）の新着テキストを Obsidian Vault の 00_Inbox/外部脳/ に取り込む。

- 元ファイルは読むだけ（変更・削除しない）。
- 取り込み済みは .claude/state/imported.json で管理（同じファイルが更新された場合は再取り込み）。
- .txt / .md のみ対象。PDF・Googleドキュメント（.gdoc）はローカルで中身が読めないため、
  一覧だけ出して /inbox の中で Google Drive コネクタから読む。

使い方:
  python3 scripts/import_external_brain.py            # 新着を取り込む
  python3 scripts/import_external_brain.py --dry-run  # 何が取り込まれるか確認だけ
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from common import JST, VAULT, load_config, load_state, now_jst, safe_filename, save_state

TEXT_EXT = {".txt", ".md"}
REMOTE_ONLY_EXT = {".pdf", ".gdoc", ".docx", ".gsheet"}
AINOTE_DATE_RE = re.compile(r"(20\d{2})[-/年.](\d{1,2})[-/月.](\d{1,2})日?(?:\D+(\d{1,2}):(\d{2}))?")


def detect_record_date(source: str, path: Path, text: str):
    """録音・記録日時を推定する。確実に分かる場合のみ返す（運用ルール §5）。"""
    if source == "AINOTE自動保存":
        first = text.strip().splitlines()[0] if text.strip() else ""
        m = AINOTE_DATE_RE.search(first)
        if m:
            y, mo, d, h, mi = m.groups()
            return f"{y}-{int(mo):02d}-{int(d):02d}" + (f" {int(h):02d}:{mi}" if h else ""), True
    m = re.search(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})", path.name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}", True
    return None, False


def build_note(source: str, rel: str, path: Path, text: str) -> str:
    record_date, confirmed = detect_record_date(source, path, text)
    mtime = datetime.fromtimestamp(path.stat().st_mtime, JST).strftime("%Y-%m-%d %H:%M")
    lines = [
        "---",
        "type: inbox",
        f"source: {source}",
        f'source_path: "{rel}"',
        f"imported_at: {now_jst().strftime('%Y-%m-%d %H:%M')}",
        f"record_date: {record_date or '不明'}",
        f"date_confirmed: {'true' if confirmed else 'false'}",
        f"file_saved_at: {mtime}  # 保存日時（録音日時ではない）",
        "status: unprocessed",
        "tags: [外部脳, 未整理]",
        "---",
        "",
        f"# {path.stem}",
        "",
        f"> 出典: 外部脳/{rel}",
        "> このノートは自動取り込みの原文です。/inbox で整理してください。",
        "",
        text.rstrip(),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    root = Path(cfg["external_brain_dir"])
    if not root.is_dir():
        print(f"外部脳フォルダが見つかりません: {root}\n"
              "Google Drive for desktop が同期しているか、scripts/config.json の external_brain_dir を確認してください。")
        return 1

    inbox = VAULT / cfg.get("inbox_dir", "00_Inbox/外部脳")
    state = load_state("imported.json")
    new, updated, remote_only = [], [], []

    for source in cfg.get("sources", ["ボイスメモ", "AINOTE自動保存"]):
        src_dir = root / source
        if not src_dir.is_dir():
            print(f"[skip] フォルダなし: {src_dir}")
            continue
        for path in sorted(src_dir.rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue
            rel = str(path.relative_to(root))
            ext = path.suffix.lower()
            if ext in REMOTE_ONLY_EXT:
                if rel not in state:
                    remote_only.append(rel)
                continue
            if ext not in TEXT_EXT:
                continue
            mtime = path.stat().st_mtime
            prev = state.get(rel)
            if prev and prev.get("mtime") == mtime:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            out = inbox / source / f"{safe_filename(path.stem)}.md"
            (updated if prev else new).append(str(out.relative_to(VAULT)))
            if args.dry_run:
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            if prev and out.exists():
                # 既存ノート（整理済みの可能性あり）は上書きせず、更新版を別名で置く
                out = out.with_name(f"{out.stem}_更新{now_jst().strftime('%Y%m%d%H%M')}.md")
            out.write_text(build_note(source, rel, path, text), encoding="utf-8")
            state[rel] = {"mtime": mtime, "note": str(out.relative_to(VAULT))}

    if not args.dry_run:
        save_state("imported.json", state)

    label = "（dry-run）" if args.dry_run else ""
    print(f"新規取り込み{label}: {len(new)}件")
    for n in new:
        print(f"  + {n}")
    print(f"更新取り込み{label}: {len(updated)}件")
    for n in updated:
        print(f"  ~ {n}")
    print(f"ローカルで読めない形式（Driveコネクタで読む）: {len(remote_only)}件")
    for n in remote_only[:30]:
        print(f"  ? {n}")
    if len(remote_only) > 30:
        print(f"  …ほか {len(remote_only) - 30}件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
