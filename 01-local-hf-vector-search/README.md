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
- Streamlit UI: [http://localhost:8501](http://localhost:8501)

## Optional: Streamlit で自然文から試す

Dashboards の Dev Tools よりもう少し体験寄りに試したい場合は、`Streamlit` の補助 UI も使えます。自然文クエリを入力し、Bedrock で埋め込みを取得してから、そのベクトルで OpenSearch を検索するだけの小さなアプリです。これは `docker compose up --build` に含まれているため、追加の手動インストールは不要です。

前提:

- `aws sso login`、`AWS_PROFILE`、`aws-vault`、一時クレデンシャルの `export` などで AWS 認証が通っていること
- `./run.sh` により OpenSearch が起動済みであること

使い方:

```bash
./run.sh
```

`docker compose` は `streamlit` サービスも一緒に起動します。認証は、次のどちらでも構いません。

- `~/.aws` に `default` profile があれば、そのまま使う
- 別の profile を使いたい場合は、ホストで `AWS_PROFILE` を export し、`~/.aws` をコンテナに読ませる
- 一時クレデンシャルを `AWS_ACCESS_KEY_ID` などの環境変数で export してから起動する

たとえば `default` 以外の profile を使う場合は、次のようにしてから起動します。

```bash
export AWS_PROFILE=your-profile
./run.sh
```

画面では、次の流れを確認できます。

1. 自然文クエリを入力する
2. Bedrock で埋め込みベクトルを取得する
3. 取得したベクトルの先頭要素と次元数を見る
4. そのベクトルで `wiki-ja-demo` を検索する

この UI は必須ではありませんが、「自然文 -> ベクトル -> 検索結果」の流れをひと目で確認したい場合に便利です。

## 片付け

```bash
docker compose down
```

データも消す場合:

```bash
docker compose down -v
```
