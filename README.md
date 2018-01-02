# 乃木坂ブログで遊ぶリポジトリ

## TODO
- ブログをスクレイピングして永続化する
- 分かち書きして構造化する(全文検索用)
- 自然言語処理系
- エンドポイント
  - タスク管理(実行, 制御, 進捗)
  - 検索(メンバー別, 日別, 全文)
  - 自然言語処理系

## Install
GCP環境に依存する

```sh
$ virtualenv -p python3 env
$ source env/bin/activate
$ pip install -r requirements.txt
```

## Web
- gunicorn
- Flask

## MiddleWare
- Cloud Datastore
- Cloud Storage
- Cloud Pub/Sub

### Cloud Datastore

Kind: `Nogizaka`

column | desc
--- | ---
id | キー
value | `nanase.nishino`
name | `西野七瀬`

### Cloud Storage
GCSにスクレイピングしたデータを入れる  
json形式で書き込む  

Key | desc
--- | ---
postUrl | 記事URL
author | メンバー名
title | 記事タイトル
content | 記事内容

### Cloud Pub/Sub
`psq` を使ってタスクキュー処理をする