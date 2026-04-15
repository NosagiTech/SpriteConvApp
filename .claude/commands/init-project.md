# init-project

プロジェクトの初期セットアップを行う。以下の手順を順番に実行すること。

## 1. 仮想環境の作成

プロジェクトルート直下に `.venv` という名称でvenv仮想環境を作成する。

```
python -m venv .venv
```

## 2. Gitの初期化

```
git init
```

その後、以下の内容で `.gitignore` を作成する。

```
# 仮想環境
.venv/

# ユーザ設定（個人の作業状態のため管理対象外）
user_settings.yaml

# 環境変数・外部公開不可の設定ファイル
*.env
*.secret

# Pythonキャッシュ
__pycache__/
*.pyc
*.pyo
```

## 3. 初回コミット

README.mdが存在しない場合は空のREADME.mdを作成し、.gitignoreとともに初回コミットを行う。

```
git add .gitignore README.md
git commit -m "初期セットアップ"
```

## 完了後の確認事項

* `.venv/` が `.gitignore` に含まれていること
* `user_settings.yaml` が `.gitignore` に含まれていること
* `git status` で `.venv` フォルダと `user_settings.yaml` が追跡対象外になっていること