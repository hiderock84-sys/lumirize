# lumirize
株式会社ルミライズ

T 252-0237
神奈川県相模原市中央区千代田3-3-20
TEL.042-704-8308 FAX.042-707-0392
E-mail info@lumirize.com

## Cloud Agent 自動運用（simple サイト）

このリポジトリには、`simple/` 配下のサイトを自動で検証・公開する設定を追加しています。

- 品質チェック: `.github/workflows/simple-site-quality.yml`
  - `tools/validate_simple_site.py` によるリンク・構造検証
  - ローカル HTTP 起動による全ページ smoke test
- 自動公開: `.github/workflows/simple-site-pages.yml`
  - `main` ブランチ更新時に GitHub Pages へ自動デプロイ
  - 公開前に必ず検証ジョブを実行

### 初回に必要な設定

1. GitHub リポジトリの **Settings → Pages** で GitHub Pages を有効化  
2. Source を **GitHub Actions** に設定  
3. 以後は `simple/` 変更を `main` に反映すると自動で検証・公開されます
