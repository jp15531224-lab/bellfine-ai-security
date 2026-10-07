#!/usr/bin/env python3
"""Obsidian Vault → Google Drive「Obsidian_AI_Export」への一方向エクスポート。

出力:
  ALL_IN_ONE_01.md, 02...  全ノート連結版（ChatGPT のプロジェクト等に添付）
  notes/                    フォルダ構成そのままのコピー
  EXPORT_INFO.md            実行日時・件数・除外したノート
除外: テンプレート、private: true、機密らしき記述（パスワード・口座番号等）を含むノート、.obsidian/.claude 等

使い方:
  python3 scripts/ai_export.py            # エクスポート
  python3 scripts/ai_export.py --dry-run  # 件数と除外理由の確認だけ
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

from common import VAULT, load_config, now_jst, parse_frontmatter

SKIP_DIRS = {".obsidian", ".trash", ".claude", ".git", "scripts", "node_modules"}
TEMPLATE_DIR_NAMES = {"90_テンプレート", "テンプレート", "templates", "Templates"}
SECRET_PATTERNS = [
    (re.compile(r"(パスワード|password|passwd|暗証番号)\s*[:：=]", re.I), "パスワード/暗証番号"),
    (re.compile(r"(口座番号|account\s*number)\s*[:：=]?\s*\d", re.I), "口座番号"),
    (re.compile(r"(api[_\- ]?key|secret|token)\s*[:：=]\s*\S{8,}", re.I), "APIキー/トークン"),
    (re.compile(r"\b\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}\b"), "カード番号らしき数字"),
    (re.compile(r"マイナンバー\s*[:：]?\s*\d"), "マイナンバー"),
]
CHUNK_CHARS = 400_000  # ALL_IN_ONE 1ファイルあたりの最大文字数
MARKER = "00_README_AI参照用.md"


def classify(path: Path, text: str):
    parts = set(path.relative_to(VAULT).parts[:-1])
    if parts & TEMPLATE_DIR_NAMES:
        return "テンプレート"
    meta = parse_frontmatter(text)
    if meta.get("private", "").lower() == "true" or "#private" in text:
        return "private"
    for pat, label in SECRET_PATTERNS:
        if pat.search(text):
            return f"機密らしき記述（{label}）"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    out = Path(cfg["export_dir"])
    if not args.dry_run:
        if not out.is_dir():
            print(f"出力先が見つかりません: {out}（Google Drive の同期と config.json を確認）")
            return 1
        if not (out / MARKER).exists() and not (out / "EXPORT_INFO.md").exists():
            print(f"安全のため中止: {out} に {MARKER} がありません。正しい Obsidian_AI_Export フォルダか確認してください。")
            return 1

    included, excluded = [], []
    for path in sorted(VAULT.rglob("*.md")):
        rel = path.relative_to(VAULT)
        if set(rel.parts) & SKIP_DIRS or rel.name in ("CLAUDE.md", "CLAUDE.local.md"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        reason = classify(path, text)
        (excluded.append((rel, reason)) if reason else included.append((rel, text)))

    print(f"対象: {len(included)}件 / 除外: {len(excluded)}件")
    for rel, reason in excluded:
        print(f"  - {rel} … {reason}")
    if args.dry_run:
        return 0

    # 前回の出力を消す（このスクリプトが作るものだけ）
    shutil.rmtree(out / "notes", ignore_errors=True)
    for old in out.glob("ALL_IN_ONE_*.md"):
        old.unlink()

    chunks, buf = [], ""
    for rel, text in included:
        dest = out / "notes" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        block = f"\n\n---\nFILE: {rel.as_posix()}\n---\n\n{text.strip()}\n"
        if buf and len(buf) + len(block) > CHUNK_CHARS:
            chunks.append(buf)
            buf = ""
        buf += block
    if buf:
        chunks.append(buf)

    stamp = now_jst().strftime("%Y-%m-%d %H:%M JST")
    for i, body in enumerate(chunks, 1):
        header = f"# Ishihara-Brain 全ノート連結版 {i:02d}/{len(chunks):02d}（{stamp}）\n" \
                 "出典は各ブロックの `FILE:` 行。事実・推測・不明を区別して回答すること。\n"
        (out / f"ALL_IN_ONE_{i:02d}.md").write_text(header + body, encoding="utf-8")

    info = [f"# EXPORT_INFO", "", f"- 実行日時: {stamp}", f"- 対象ノート: {len(included)}件",
            f"- 連結ファイル: {len(chunks)}個", f"- 除外: {len(excluded)}件", "", "## 除外したノート"]
    info += [f"- {rel.as_posix()} … {reason}" for rel, reason in excluded] or ["- なし"]
    (out / "EXPORT_INFO.md").write_text("\n".join(info) + "\n", encoding="utf-8")
    print(f"完了: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
