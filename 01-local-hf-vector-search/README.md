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
cd /Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/01-local-hf-vector-search
./run.sh
```

初回は Docker イメージの build とデータ取得があるため、少し時間がかかります。

## デフォルト設定

- 取り込み件数: `10,000`
- 対象 index: `wiki-ja-demo`
- サンプルクエリ生成: `heuristic`

より多く入れたい場合は `.env` を編集してください。

```bash
cp .env.example .env
```

例:

```dotenv
MAX_DOCS=100000
```

サンプルクエリの見せ方を自然文寄りにしたい場合は、デフォルトの `heuristic` のままで構いません。Bedrock の Cohere 埋め込みを使って自然文クエリ用の埋め込みを生成したい場合は、次も指定できます。

```dotenv
SAMPLE_QUERY_EMBEDDING_MODE=bedrock
BEDROCK_EMBED_MODEL_ID=cohere.embed-multilingual-v3
BEDROCK_EMBED_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
```

## 起動後に見る場所

- OpenSearch Dashboards: [http://localhost:5601](http://localhost:5601)
- OpenSearch API: [http://localhost:9200](http://localhost:9200)

loader が完了すると、`generated/example_queries.md` と `generated/example_queries.json` が作られます。`example_queries.md` には Dashboards の Dev Tools に貼り付けられる `k-NN` クエリ例が入っています。

## 片付け

```bash
docker compose down
```

データも消す場合:

```bash
docker compose down -v
```
