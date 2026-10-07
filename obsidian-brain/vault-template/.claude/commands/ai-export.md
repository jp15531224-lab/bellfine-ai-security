---
description: Vault を Drive「Obsidian_AI_Export」へ一方向エクスポート（ChatGPT等の参照用）
---

1. `python3 scripts/ai_export.py` を実行する（出力先は `CLAUDE.local.md` / `scripts/config.json` の `export_dir`）。
2. 実行結果（件数・除外したノートと理由）を短く報告する。
3. 除外理由が「機密らしき記述」のノートがあれば一覧で示し、`private: true` を付けるか、記述を削除するか本人に確認する（勝手に編集しない）。
