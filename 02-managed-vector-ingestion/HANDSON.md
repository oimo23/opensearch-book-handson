# Hands-on 2: OpenSearch Service で vector ingestion と auto-optimize を試す

このハンズオンでは、Amazon OpenSearch Service の managed vector ingestion を使って、大規模ベクトルデータの自動最適化とインデックス構築を体験します。  
データセットは、あらかじめ S3 に配置済みの Parquet ファイルを利用します。

## Step 1. OpenSearch ドメインをデプロイする

まずは OpenSearch ドメインを用意します。  
この手順は README にまとめてあります。

- [README.md](/Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion/README.md)

この CDK は次のような構成のドメインを作成します。

- OpenSearch 3.1
- `or2.xlarge.search x1`
- public endpoint
- 実行者のグローバル IP `/32` を許可する access policy
- `VectorIngestionRole-*` を許可する access policy

まずは次を実行してください。

```bash
cd /Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion
npm install
npx cdk deploy
```

deploy が終わったら、出力された `DashboardsUrl` を控えておきます。

## Step 2. vector ingestion から auto-optimize を行う

次に AWS コンソールから vector ingestion job を作成し、自動最適化を実行します。  
ここでは、事前に用意した S3 上の Parquet データセットを使います。

今回使う S3 prefix は次です。

```text
s3://realworld-opensearch-vector-data-153766774185/synthetic-cohere-like-parquet-10m-v1/data/
```

### 2-1. vector ingestion の作成画面を開く

![step1](/Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion/images/step1.png)

### 2-2. データセットと接続先ドメインを指定する

- Data source: 上記の S3 prefix
- Destination: Step 1 で作成した OpenSearch ドメイン
- ベクトル列名: `vector`
- 次元数: `1024`

![step2](/Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion/images/step2.png)

### 2-3. auto-optimize を有効にして recommendation を待つ

auto-optimize では、与えた recall 要件と latency 要件に合わせて、候補となるインデックス構成が提案されます。  
候補が出るまで数十分かかることがあります。

![step3](/Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion/images/step3.png)

## Step 3. 推奨された設定で index build を行う

候補が表示されたら、内容を確認して `Build index` を実行します。  
これにより、推奨された設定で実際のインデックス構築が始まります。

確認したいポイントは次のとおりです。

- engine が何になったか
- `on_disk` か `in_memory` か
- compression level がどの程度か
- recall と memory footprint のトレードオフがどうなっているか

![step4](/Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion/images/step4.png)

## Step 4. Dashboards の Dev Tools で `k-NN` クエリを試す

インデックス構築が終わったら、Dashboards の Dev Tools から `k-NN` クエリを投げて結果を確認します。  
1024 次元のベクトルをそのまま貼り付けると崩れやすいので、まず検索テンプレートを登録し、その後は短いクエリで呼び出します。

- [queries/dev_tools_queries.md](/Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion/queries/dev_tools_queries.md)
- [queries/dev_tools_query_syn10m_full.json](/Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion/queries/dev_tools_query_syn10m_full.json)
- [queries/register_search_template.md](/Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion/queries/register_search_template.md)
- [queries/register_search_template.json](/Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion/queries/register_search_template.json)

## 補足

- auto-optimize の recommendation は、全件に対する厳密評価ではなく、AWS 側の sampled evaluation に基づく推奨です。
- そのため、ここでの数値は「この条件ならこういう候補が有望」という判断材料として読みます。
- 本ハンズオンでは managed vector ingestion の流れを体験することを重視し、pipeline や index build の細かい設定は AWS 側の recommendation に委ねます。
