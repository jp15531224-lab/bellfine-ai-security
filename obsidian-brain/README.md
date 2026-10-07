# Obsidian 外部脳 × Claude Code 連携キット

Obsidian Vault（Ishihara-Brain）を「外部脳の正本」にして、PC の Claude Code から
AI秘書として使えるようにするキットです。Google Drive「iCloud外部脳」（ボイスメモ・AINOTE）と
既存の **AI秘書_運用ルール** にそのままつながります。

```
[話す] Whisper Memos / AINOTE / Plaud
   │  （既存：Make → Google Drive「iCloud外部脳」）
   ▼
[PC] Claude Code（Vault で起動）
   │  /inbox  … 新着を取り込み → 人物・案件・会議ノートへ整理 → ToDo抽出
   ├─▶ Obsidian Vault（記憶の正本：人物カルテ・案件・会議・日次）
   ├─▶ Todoist（実行ToDo）／ Googleカレンダー（予定）
   └─▶ Drive「Obsidian_AI_Export」（/ai-export：ChatGPT 等に渡す読み取り専用コピー）
```

## 前提（PC側・Mac）
1. Obsidian の Vault（例：`~/Documents/Ishihara-Brain`）
2. **Google Drive for desktop** で「マイドライブ」が同期されていること
   （`~/Library/CloudStorage/GoogleDrive-<Gmail>/マイドライブ/iCloud外部脳` が Finder で見える状態）
3. Claude Code（`claude` コマンド）と python3

## セットアップ（5分）
```bash
git clone https://github.com/jp15531224-lab/bellfine-ai-security.git
cd bellfine-ai-security/obsidian-brain
bash setup.sh ~/Documents/Ishihara-Brain     # ← 自分の Vault のパスに置き換え
```
setup.sh がやること（既存ファイルは **上書きしません**）:
- Vault に `CLAUDE.md`・スラッシュコマンド・テンプレート・フォルダ構成・スクリプトを追加
  （既存の CLAUDE.md がある場合は、ガイドを読み込む1行だけ追記）
- Drive の「iCloud外部脳」「Obsidian_AI_Export」を自動検出して `scripts/config.json` を作成
- Drive の「AI秘書_運用ルール」を Vault からシンボリックリンクで参照（Drive 側を直せば常に最新が効く）
- Claude Code が Drive 同期フォルダを読めるよう `.claude/settings.local.json` を作成

## 使い方
```bash
cd ~/Documents/Ishihara-Brain
claude
```
| コマンド | やること |
|---|---|
| `/inbox` | 外部脳の新着を取り込み、人物・案件・会議ノートへ整理、ToDo を Todoist へ |
| `/today` | 今日の最重要3件と行動計画（`40_日次/` に保存） |
| `/person 福本さん` | 人物・会社カルテ（過去の話・約束・金額・未回答・次の一手） |
| `/before-meeting 北川さん` | 打ち合わせ前の1分ブリーフィング |
| `/weekly` | 週次未完了チェック（期限超過・止まっている案件・追客漏れ） |
| `/ai-export` | Vault → Drive「Obsidian_AI_Export」へエクスポート（機密・private は除外） |

普通の会話（「ダイセルの件どうなってる？」など）でも、CLAUDE.md の指示で Vault・外部脳を探して答えます。

## コネクタ（あると精度が上がる）
Claude Code に claude.ai アカウントでログインしていれば、claude.ai で接続済みのコネクタ
（Google Drive・Todoist・Plaud・Googleカレンダー）を Claude Code からも使えます。
`claude` 起動後に `/mcp` で一覧を確認してください。
- 無くても動く範囲：Vault の読み書き、ボイスメモ・AINOTE の .txt 取り込み、AIエクスポート
- コネクタが必要：PDF・Googleドキュメントの中身、Plaud 録音、Todoist 登録、カレンダー

## フォルダ構成（Vault 内）
```
00_Inbox/外部脳/   自動取り込みした原文（/inbox で整理）
10_事業/           グリーン興産・ベルフィーヌ・AI防犯カメラ・全厚済・新規事業
20_人物/           人物・会社カルテ
30_会議/           議事録
40_日次/           日次ノート・行動計画・週次チェック
50_アイデア/
90_テンプレート/   テンプレート（エクスポート対象外）
```
Obsidian の「設定 → テンプレート」でテンプレートフォルダを `90_テンプレート` に指定すると、手入力でも同じ形式で書けます。

## 安全設計
- 外部脳（Drive）のファイルは **読むだけ**。取り込み済みは `.claude/state/imported.json` で管理し二重取り込みしない。
- エクスポートは一方向。`private: true`・`#private`・パスワード/口座番号/カード番号らしき記述のあるノートは自動除外。
- エクスポート先に `00_README_AI参照用.md` が無い場合は中止（誤ったフォルダを消さないため）。
- `.claude/settings.json` で `.obsidian/` の編集と `rm -rf` を禁止。

## ⚠ 注意
- **このリポジトリは公開（public）です。Vault の中身・運用ルール（Todoist ID 等）は絶対にコミットしないでください。**
  このキットにはテンプレートとスクリプトだけが入っています。
- Windows は setup.sh 非対応（スクリプト本体は動きます。`scripts/config.example.json` をコピーして手動設定）。
