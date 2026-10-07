# C案：Vault を非公開 GitHub に置いて iPad から Claude Code で使う

```
iPad の Obsidian ──(Obsidian Git: pull/push)──┐
Mac の Obsidian  ──(Obsidian Git: pull/push)──┼─▶ GitHub 非公開リポジトリ「ishihara-brain」(main)
iPad の Claude アプリ（Claude Code クラウド）──┘        ▲
        │  /inbox /today /person …                    │ 作業の最後に commit & push
        └─ Google Drive・Todoist・Plaud・カレンダー（コネクタ）
```
Mac の電源が切れていても、iPad だけで「外部脳の取り込み → 整理 → ToDo登録」まで回ります。

## 手順1：非公開リポジトリを作る（iPad・2分）
1. Safari で https://github.com/new を開く
2. Repository name：`ishihara-brain`
3. **Private を必ず選択**（Public は絶対に不可）
4. 「Add a README file」に✓ →「Create repository」
5. Claude に「ishihara-brain 作った」と伝える → Claude がキット一式を入れて push する

## 手順2：Claude Code（iPad）で使う
1. Claude アプリ →「Code」→ 新しいセッション → リポジトリ `ishihara-brain` を選択
2. `/inbox` `/today` `/person 福本さん` などを入力
   - Google Drive・Todoist・Plaud・カレンダーはコネクタ経由で使われる
   - 作業の最後に Claude が自動で commit & push（main へ）

## 手順3：iPad の Obsidian で同じノートを見る（任意・10分）
1. GitHub で「Fine-grained personal access token」を作成
   （Settings → Developer settings → Personal access tokens → Fine-grained →
   Repository access: `ishihara-brain` のみ／Permissions: Contents = Read and write）
   **トークンは誰にも送らない・Claude にも貼らない。**
2. iPad の Obsidian で新しい Vault「ishihara-brain」を作成（iCloud に保存しない設定推奨）
3. 設定 → コミュニティプラグイン → 「Git」（Obsidian Git）をインストール・有効化
4. Git の設定：Authentication に GitHub ユーザー名とトークン →
   コマンドパレット「Git: Clone an existing remote repo」→ `https://github.com/jp15531224-lab/ishihara-brain.git`
5. 「Auto pull interval」5分、「Auto commit-and-sync interval」10分 に設定

※ iPad の Obsidian Git は大きな Vault だと遅いことがあります。重い場合は「閲覧は iPad の Obsidian、整理は Claude」に分けてください。

## 手順4：Mac の既存 Vault（Ishihara-Brain）を移す（Mac・10分）
```bash
cd ~/Documents/Ishihara-Brain            # 既存 Vault
git init -b main
git remote add origin https://github.com/jp15531224-lab/ishihara-brain.git
git pull origin main --allow-unrelated-histories   # キットを取り込む（既存ノートは残る）
git add -A && git commit -m "既存Vaultを追加" && git push -u origin main
```
その後 Mac の Obsidian にも Obsidian Git を入れれば、Mac・iPad・Claude の3者が同じ Vault を共有します。
Mac で `bash setup.sh` を実行すると PC モード（Drive 同期フォルダから直接取り込み）も使えます。

## リスクと対策
| リスク | 対策 |
|---|---|
| 個人情報・取引情報が GitHub に置かれる | Private 必須。2段階認証を ON。パスワード・口座番号・カード番号は Vault に書かない |
| 端末間の同時編集で衝突 | Claude は push 前に pull。衝突時は勝手に解決せず確認する設定済み |
| トークン漏えい | トークンは ishihara-brain だけに権限を絞る。有効期限を1年に |
| GitHub 障害 | 各端末にローカルコピーが残るので閲覧は可能 |
