#!/usr/bin/env bash
# Obsidian Vault に Claude Code 連携（AI秘書・外部脳）を組み込むセットアップ（macOS 用）
#
#   bash setup.sh "<Obsidian Vault のパス>"
#
# - 既存ファイルは上書きしない（追加のみ）
# - Google Drive for desktop の同期フォルダから「iCloud外部脳」「Obsidian_AI_Export」を自動検出
set -euo pipefail

VAULT="${1:-}"
if [[ -z "$VAULT" || ! -d "$VAULT" ]]; then
  echo "使い方: bash setup.sh \"<Obsidian Vault のパス>\""
  echo "  例: bash setup.sh ~/Documents/Ishihara-Brain"
  exit 1
fi
VAULT="$(cd "$VAULT" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$HERE/vault-template"

if [[ ! -d "$VAULT/.obsidian" ]]; then
  read -r -p "⚠ $VAULT に .obsidian がありません。Obsidian の Vault で間違いないですか？ [y/N] " ok
  [[ "$ok" == "y" || "$ok" == "Y" ]] || exit 1
fi

command -v python3 >/dev/null || { echo "python3 が必要です（xcode-select --install で入ります）"; exit 1; }

echo "▶ テンプレートを追加（既存ファイルは上書きしません）"
# cp -n は既存ファイルをスキップ
(cd "$TEMPLATE" && find . -type d -exec mkdir -p "$VAULT/{}" \;)
(cd "$TEMPLATE" && find . -type f ! -name .gitkeep | while read -r f; do
  if [[ -e "$VAULT/$f" ]]; then echo "  skip（既存）: $f"; else cp "$f" "$VAULT/$f"; echo "  add: $f"; fi
done)

# 既存の CLAUDE.md がある場合は上書きせず、ガイドを別ファイルにして読み込み行だけ追記
if ! cmp -s "$TEMPLATE/CLAUDE.md" "$VAULT/CLAUDE.md"; then
  cp "$TEMPLATE/CLAUDE.md" "$VAULT/.claude/obsidian-brain-guide.md"
  if ! grep -q "@.claude/obsidian-brain-guide.md" "$VAULT/CLAUDE.md"; then
    printf '\n\n## AI秘書・外部脳連携（setup.sh が追記）\n@.claude/obsidian-brain-guide.md\n' >> "$VAULT/CLAUDE.md"
    echo "  append: CLAUDE.md に連携ガイドの読み込みを追記"
  fi
fi

echo "▶ Google Drive の外部脳フォルダを探しています…"
EB=""; EX=""
for root in "$HOME"/Library/CloudStorage/GoogleDrive-*/{マイドライブ,"My Drive"} "$HOME/Google Drive/マイドライブ" "$HOME/Google Drive/My Drive"; do
  [[ -d "$root/iCloud外部脳" && -z "$EB" ]] && EB="$root/iCloud外部脳"
  [[ -d "$root/Obsidian_AI_Export" && -z "$EX" ]] && EX="$root/Obsidian_AI_Export"
done
if [[ -z "$EB" ]]; then
  read -r -p "iCloud外部脳 フォルダのパスを入力（Finder からドラッグ可）: " EB
  EB="${EB%/}"; EB="${EB//\\ / }"
fi
if [[ -z "$EX" ]]; then
  read -r -p "Obsidian_AI_Export フォルダのパスを入力（空欄なら後で設定）: " EX
  EX="${EX%/}"; EX="${EX//\\ / }"
fi
echo "  外部脳: $EB"
echo "  AIエクスポート先: ${EX:-（未設定）}"

CONFIG="$VAULT/scripts/config.json"
if [[ -e "$CONFIG" ]]; then
  echo "  skip（既存）: scripts/config.json"
else
  EB="$EB" EX="$EX" python3 - "$CONFIG" <<'PY'
import json, os, sys
json.dump({
  "external_brain_dir": os.environ["EB"],
  "export_dir": os.environ["EX"],
  "inbox_dir": "00_Inbox/外部脳",
  "sources": ["ボイスメモ", "AINOTE自動保存"],
}, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
  echo "  add: scripts/config.json"
fi

# AI秘書_運用ルール（Drive が正本）をシンボリックリンクで参照 → 常に最新版を読む
RULE_LINK="$VAULT/.claude/AI秘書_運用ルール.md"
if [[ -f "$EB/AI秘書_運用ルール" && ! -e "$RULE_LINK" ]]; then
  ln -s "$EB/AI秘書_運用ルール" "$RULE_LINK"
  echo "  link: .claude/AI秘書_運用ルール.md → Drive"
fi

LOCAL_MD="$VAULT/CLAUDE.local.md"
if [[ ! -e "$LOCAL_MD" ]]; then
  cat > "$LOCAL_MD" <<EOF
# このPC固有の設定（setup.sh が生成・git管理外）

- 外部脳（Google Drive 同期フォルダ）: \`$EB\`
- AIエクスポート先: \`${EX:-未設定}\`
- 外部脳のファイルは **読むだけ**。Drive 側のファイルを編集・削除しない。

## AI秘書_運用ルール（正本は Drive）
@.claude/AI秘書_運用ルール.md
EOF
  echo "  add: CLAUDE.local.md"
fi

# Claude Code が Vault の外（Drive 同期フォルダ）も読めるようにする
SETTINGS_LOCAL="$VAULT/.claude/settings.local.json"
if [[ ! -e "$SETTINGS_LOCAL" ]]; then
  EB="$EB" EX="$EX" python3 - "$SETTINGS_LOCAL" <<'PY'
import json, os, sys
dirs = [d for d in (os.environ["EB"], os.environ["EX"]) if d]
json.dump({"permissions": {
  "additionalDirectories": dirs,
  "allow": [f"Read(/{d}/**)" for d in dirs],  # 絶対パスは // で始める
}}, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
  echo "  add: .claude/settings.local.json"
fi

echo
echo "▶ 動作確認（取り込みの dry-run）"
(cd "$VAULT" && python3 scripts/import_external_brain.py --dry-run | head -20) || true

cat <<EOF

✅ セットアップ完了
次の手順:
  cd "$VAULT"
  claude
  > /inbox        … 外部脳の新着を取り込んで整理
  > /today        … 今日やること
  > /person 福本さん
EOF
