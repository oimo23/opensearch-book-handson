# S3 Vectorsを`or2.medium.search`で比較する

この手順では、第4章の`or2.large.search`による計測と同じ1000万件のデータを使い、インスタンスだけを`or2.medium.search`へ下げて比較します。OpenSearchドメインとOSIS pipelineを作成するため、実行中はAWS料金が発生します。

## 比較条件

- OpenSearch 3.1
- `or2.medium.search x1`
- 512 GiB gp3
- S3 Vectors有効
- GPU acceleration有効
- 1000万件、1024次元
- `s3vector` engine
- 1シャード、レプリカ0
- OSIS 4〜8 OCU、S3 source 5 workers
- 同じ検索ベクトル、`k = 10`

通常の`32x`ハンズオンを実行中の場合は、先にそのリソースを削除してください。

## 1. 事前確認とデプロイ

```bash
./scripts/preflight.sh

INSTANCE_TYPE=or2.medium.search \
ENABLE_S3_VECTORS=true \
CONFIRM_AWS_COSTS=yes \
./scripts/deploy.sh
```

CDKは読者のAWSアカウントにOSIS用IAM roleを作り、CloudFormationへendpointとrole ARNを出力します。既存のroleやpipelineは必要ありません。

## 2. S3 Vectors indexを作成する

```bash
INDEX_NAME=syn10m_s3vector \
INDEX_CONFIG=osis/syn10m-s3vector.index.json \
EXPECTED_COMPRESSION= \
EXPECTED_ENGINE=s3vector \
EXPECTED_MODE= \
./scripts/create-index.sh
```

## 3. OSIS pipelineを作成する

pipelineテンプレートのendpoint、region、IAM role ARNは、スクリプトがCloudFormation出力から埋めます。

```bash
PIPELINE_NAME=book-s3vector-10m \
INDEX_NAME=syn10m_s3vector \
TEMPLATE_PATH=osis/synthetic-10m-s3vector.pipeline.json \
./scripts/create-pipeline.sh
```

投入元は次の200個のParquetファイルです。

```text
s3://opensearch-book-handson-data-153766774185/synthetic-cohere-like-parquet-10m-v2/data/
```

## 4. 1000万件まで投入する

```bash
PIPELINE_NAME=book-s3vector-10m \
INDEX_NAME=syn10m_s3vector \
TARGET_COUNT=10000000 \
MAX_WAIT_SECONDS=21600 \
./scripts/monitor-ingest.sh
```

2026年7月25日の実測では、件数が増え始めてから約4時間4分で1000万件へ到達しました。投入期間のCPU使用率は平均79.4%、最大96.0%、JVM memory pressureは平均44.62%、最大82.2%でした。

## 5. 検索レイテンシを計測する

CloudFormation出力からendpointを取得します。

```bash
export DOMAIN_ENDPOINT=$(
  aws cloudformation describe-stacks \
    --stack-name ManagedVectorIngestionStack \
    --region ap-northeast-1 \
    --query "Stacks[0].Outputs[?OutputKey=='DomainEndpoint'].OutputValue | [0]" \
    --output text
)

DOMAIN_ENDPOINT="$DOMAIN_ENDPOINT" \
INDEX_NAME=syn10m_s3vector \
ROUNDS=30 \
bash queries/benchmark_s3vector.sh
```

実測結果は次のとおりです。

| instance | warmup | mean | p50 | min | max | graph memory |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `or2.large.search` | 0.114秒 | 796.3 ms | 783.0 ms | 544 ms | 1048 ms | 0.0% |
| `or2.medium.search`（定常30回） | 0.131秒 | 1041.0 ms | 1064.5 ms | 882 ms | 1202 ms | 0.0% |

投入直後の初回10回は平均1818.1 ms、p50 1656.5 ms、最小1330 ms、最大3409 msでした。S3 Vectorsはgraph cacheに載らないため、初回と定常状態を分けて確認します。

検索品質は、入力Parquet 1ファイルの5万件からseed固定で3万件を抽出し、300クエリで`Recall@10`を評価しました。結果は平均0.9697、p50とp95は1.0、最小0.8でした。第4章の`or2.large.search`の0.937とは抽出母集団と距離条件が異なるため、改善したとは解釈しません。

## 6. 後片付け

S3 Vectors indexを先に削除してから、OpenSearchドメインを破棄します。

```bash
PIPELINE_NAME=book-s3vector-10m \
INDEX_NAME=syn10m_s3vector \
CONFIRM_DESTROY=yes \
./scripts/destroy.sh
```

S3 Vectors indexが残った状態では、engineの無効化やドメイン削除に失敗する場合があります。`destroy.sh`はpipeline、index、CDK stackの順に削除します。
