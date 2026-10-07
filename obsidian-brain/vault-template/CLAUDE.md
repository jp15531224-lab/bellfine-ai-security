# Ishihara-Brain（Obsidian外部脳）× Claude Code 運用ガイド

このフォルダは石原淳平さんの Obsidian Vault（外部脳の正本）です。
Claude Code はこの Vault を直接読み書きして「AI秘書」として動きます。

## 0. 最初に読むもの
- `CLAUDE.local.md`（setup.sh が生成。PCごとのパスと「AI秘書_運用ルール」の読み込み）
- AI秘書_運用ルールが読み込めない場合は、Google Drive コネクタで「AI秘書_運用ルール」を検索して読む。
  **運用ルールとこのファイルが矛盾したら、運用ルールを優先する。**

## 1. 基本原則
- タイムゾーンは Asia/Tokyo。「今日」はJSTで判断。
- 本人は話すだけ。AIが覚え・整理し・Todoistに登録し・期限を管理し・必要な時に思い出させる。
- 【事実】（記録にある）／【推測】（AIの解釈）／【提案】／【不明】を必ず分ける。情報を創作しない。
- 録音文字起こし由来の人名・社名・金額・日付は誤認識の可能性あり →「（聞き取り要確認）」を付ける。
- 回答の根拠には `FILE: パス` または `drive:<fileId>` / `plaud:<id>` を出典として示す。
- 全厚済（全国福利厚生共済会）は営利事業とは別の論理（会員拡大・組織運営）で扱う。
- 業務・案件・取引先・約束・過去の発言・ToDo・期限の質問は、コマンドが無くても
  Vault → 外部脳（Drive 同期フォルダ / Drive コネクタ）→ Plaud・Todoist・カレンダーの順に探してから答える。

## 2. Vault のフォルダ構成
| フォルダ | 用途 |
|---|---|
| `00_Inbox/外部脳/` | 外部脳（ボイスメモ・AINOTE）から取り込んだ未整理ノート。`/inbox` で整理する |
| `10_事業/<事業名>/` | 事業ごとの案件ノート（グリーン興産・ベルフィーヌ・AI防犯カメラ・全厚済・新規事業） |
| `20_人物/` | 人物・会社カルテ（1人1ノート。ファイル名は「姓名」または「会社名」） |
| `30_会議/` | 打ち合わせ・会食の議事録（`YYYY-MM-DD_相手_テーマ.md`） |
| `40_日次/` | 日次ノート・今日の行動計画（`YYYY-MM-DD.md`） |
| `50_アイデア/` | アイデア・将来検討 |
| `90_テンプレート/` | テンプレート（AIエクスポート対象外） |

既存のフォルダ構成がある場合はそちらを優先し、無理に移動しない。

## 3. タグ規約
- `#promise/mine` 石原側の約束 ／ `#promise/theirs` 相手側の約束
- `#todo` ToDo ／ `#verify` 要確認 ／ `#idea` アイデア
- `#biz/green`（グリーン興産）`#biz/bellefine`（ベルフィーヌ）`#biz/camera`（AI防犯カメラ）`#biz/zenkosai`（全厚済）`#biz/new`（新規事業）`#private`
- 人物・会社は `[[20_人物/福本さん]]` のように wikilink でつなぐ（Obsidian のグラフで関係が見えるように）。

## 4. ノートを書くときのルール
- frontmatter を必ず付ける：`type`（meeting/person/project/daily/inbox/idea）, `date`, `source`, `tags`。
- 機密（パスワード・口座番号・暗証番号・カード番号・APIキー）は Vault に書かない。どうしても必要なノートは frontmatter に `private: true`。
- 既存ノートを上書きしない。追記は末尾に `## YYYY-MM-DD 追記` 見出しで足す。
- ノートを削除・移動するときは必ず本人に確認する。

## 5. 外部サービスとの役割分担
- **Obsidian Vault**：記憶の正本（人物・案件・会議・判断の経緯）
- **Google Drive「iCloud外部脳」**：録音・文字起こしの入口（Whisper Memos→Make→Drive、AINOTE）。既存の仕組みは壊さない
- **Todoist**：実行するToDoの正式な受け皿（登録ルールは運用ルール §2〜§9）
- **Googleカレンダー**：日時が決まった予定
- **Plaud**：会議録音（start_at が正確な録音日時）
- **Drive「Obsidian_AI_Export」**：ChatGPT等に渡す読み取り専用コピー（`/ai-export` で更新）

## 6. スラッシュコマンド
| コマンド | 内容 |
|---|---|
| `/inbox` | 外部脳の新着（ボイスメモ・AINOTE・Plaud）を取り込み → 人物/案件/会議ノートへ整理 → ToDo抽出 |
| `/today` | 今日の予定と最重要3件（Vault・Todoist・カレンダー横断） |
| `/person 名前` | 人物・会社カルテ（過去の話・約束・金額・未回答・次の一手） |
| `/before-meeting 名前` | 打ち合わせ前の1分ブリーフィング |
| `/weekly` | 週次未完了チェック（期限超過・止まっている案件・追客漏れ） |
| `/ai-export` | Vault → Drive「Obsidian_AI_Export」へ一方向エクスポート |

## 7. 実行環境の判定（PC / iPad・クラウド）
- **PC モード**：`scripts/config.json` があり、`external_brain_dir` のフォルダが存在する → スクリプトで取り込み・エクスポート。
- **クラウドモード**（iPad の Claude アプリ / claude.ai/code。Vault は非公開 GitHub リポジトリ）：
  ローカルに Google Drive は無い。外部脳は **Google Drive コネクタ** で読む。
  - `/inbox`：Drive の「iCloud外部脳」内「ボイスメモ」「AINOTE自動保存」を modifiedTime で新しい順に検索し、
    `.claude/state/imported.json` に fileId が無く、かつ `00_Inbox/外部脳/` に同名ノートも無いものだけを読み（PC で取り込み済みの重複防止）、`00_Inbox/外部脳/<フォルダ名>/<ファイル名>.md` に
    import_external_brain.py と同じ frontmatter（source / source_path に `drive:<fileId>` / record_date / date_confirmed / status）で保存してから整理する。
    1回の処理は新しい順に最大10件（AINOTE は巨大なので要点部分のみ読む）。
  - `/ai-export`：`python3 scripts/ai_export.py` は使えないので、Vault を連結した `ALL_IN_ONE_01.md` と `EXPORT_INFO.md` を作り、
    Drive コネクタで「Obsidian_AI_Export」へアップロードする（除外ルールは同じ）。
- **クラウドモードでの保存**：作業の最後に必ず `git add -A && git commit && git push origin main`。
  この Vault リポジトリでは **main への直接 push をオーナーが許可済み**（iPad/Mac の Obsidian は main を同期するため）。
  push 前に `git pull --rebase origin main` で他端末の変更を取り込む。衝突したら勝手に解決せず本人に確認。
