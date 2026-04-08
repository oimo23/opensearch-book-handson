# ハンズオン1: Dockerでローカルにベクトル検索を立ち上げる

このディレクトリでは、次の構成をワンコマンドで立ち上げます。

- OpenSearch
- OpenSearch Dashboards
- Hugging Face の `Cohere/wikipedia-2023-11-embed-multilingual-v3` から日本語データを取り込み、ローカルの OpenSearch に ingest する loader

## 事前条件

- Docker Desktop が起動していること
- インターネット接続があること

## 起動

```bash
git clone https://github.com/oimo23/opensearch-book-handson.git
cd opensearch-book-handson/01-local-hf-vector-search
./run.sh
```

初回は Docker イメージの build とデータ取得があるため、少し時間がかかります。

## デフォルト設定

- 取り込み件数: `10,000`
- 対象 index: `wiki-ja-demo`

より多く入れたい場合は `.env` を編集してください。

```bash
cp .env.example .env
```

例:

```dotenv
MAX_DOCS=100000
```

サンプルクエリは、次の生成済みファイルをそのまま使います。`example_queries.md` には Dashboards の Dev Tools に貼り付けられる `k-NN` クエリ例が入っています。

- [generated/example_queries.md](./generated/example_queries.md)
- [generated/example_queries.json](./generated/example_queries.json)

これらのファイルはリポジトリに含めているため、読者はサンプルクエリの生成方法を気にせず、そのまま検索体験を試せます。

## 起動後に見る場所

- OpenSearch Dashboards: [http://localhost:5601](http://localhost:5601)
- OpenSearch API: [http://localhost:9200](http://localhost:9200)

## 片付け

```bash
docker compose down
```

データも消す場合:

```bash
docker compose down -v
```
