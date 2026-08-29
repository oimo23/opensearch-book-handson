# Hands-on 2: managed vector ingestionで1000万件を投入する

このハンズオンでは、Amazon OpenSearch ServiceとAmazon OpenSearch Ingestion（OSIS）を使い、S3上のParquetデータをベクトルindexへ投入します。

主な手順では、過去のAuto-Optimize実測で得た`Faiss + HNSW + on_disk + 32x`の設定を固定して使います。AWSコンソールの操作に依存せず、構築、投入、検索、削除までコマンドで再現できます。

## AWS料金に関する注意

OpenSearchドメインとOSIS pipelineを作成するため、実行中はAWS料金が発生します。スクリプトは、次の確認変数がなければ課金リソースを作成しません。

```bash
CONFIRM_AWS_COSTS=yes
```

検証後は、必ず`./scripts/destroy.sh`まで実行してください。

## 検証済みの構成

2026年8月23日に、次の構成で1000万件の投入から削除まで確認しました。

- OpenSearch 3.1
- `or2.xlarge.search x1`
- gp3 512 GiB
- GPUベースのvector index build acceleration有効
- 1シャード、レプリカ0
- Faiss、HNSW、`on_disk`、`32x`
- OSIS 4〜8 OCU、S3 source 5 workers
- 1000万件、1024次元、200 Parquetファイル

実測では、投入開始から約83分で1000万件へ到達しました。初回検索は8,559 ms、ウォーム後は10〜16 msでした。

## 自動化している範囲

CDKとスクリプトが次を行います。

1. OpenSearchドメインとOSIS用IAM roleを作成する
2. CloudFormation出力からendpointとrole ARNを取得する
3. 固定mappingでindexを作成する
4. 読者自身のendpointとrole ARNを埋めたOSIS設定を生成する
5. pipelineを作成し、指定件数まで投入する
6. 件数、mapping、k-NN queryを検証する
7. pipeline、index、OpenSearchドメインを削除する

著者環境のendpointやAWSアカウントIDを入力する必要はありません。

## 前提

- Node.js 20以上
- AWS CLI v2
- AWS CDK v2
- `jq`、`curl`
- `cdk bootstrap`済みのAWSアカウント
- OpenSearch、OSIS、CloudFormation、IAM roleを作成できる権限
- `ap-northeast-1`を利用できること

OSISへIAM roleを渡すため、実行ユーザーには作成されたroleに対する`iam:PassRole`も必要です。共有データと検証済み構成をそろえるため、このハンズオンではリージョンを`ap-northeast-1`に固定します。

AWSプロファイルを使う場合は、実行前に設定します。

```bash
export AWS_PROFILE=your-profile
export AWS_REGION=ap-northeast-1
```

## まずsmokeテストを実行する

新規clone後、最初に事前確認を行います。この処理では課金リソースを作成しません。

```bash
git clone https://github.com/oimo23/opensearch-book-handson.git
cd opensearch-book-handson/02-managed-vector-ingestion
./scripts/preflight.sh
```

smokeモードは、先頭のParquet 1ファイルだけを読み込み、5万件の投入を確認します。1000万件すべてを走査しないため、OSISとindexの接続を短時間で確認できます。

```bash
MODE=smoke \
CONFIRM_AWS_COSTS=yes \
./scripts/run.sh
```

結果は`.handson/verification.json`へ保存されます。

```bash
jq . .handson/verification.json
```

確認後、リソースを削除します。

```bash
CONFIRM_DESTROY=yes ./scripts/destroy.sh
```

## 1000万件を投入する

smokeテストのリソースを削除した後、fullモードを実行します。1000万件の投入は時間と料金が増えるため、追加の確認変数が必要です。

```bash
MODE=full \
CONFIRM_AWS_COSTS=yes \
CONFIRM_10M_INGEST=yes \
./scripts/run.sh
```

投入と確認が終わったら削除します。

```bash
CONFIRM_DESTROY=yes ./scripts/destroy.sh
```

## スクリプトを個別に実行する

問題を切り分ける場合は、次の順序で個別実行できます。

```bash
./scripts/preflight.sh
CONFIRM_AWS_COSTS=yes ./scripts/deploy.sh
./scripts/create-index.sh
SOURCE_PREFIX=synthetic-cohere-like-parquet-10m-v2/data/part-00000.parquet \
./scripts/create-pipeline.sh
TARGET_COUNT=50000 ./scripts/monitor-ingest.sh
EXPECTED_COUNT=50000 ./scripts/verify.sh
CONFIRM_DESTROY=yes ./scripts/destroy.sh
```

主な環境変数は次のとおりです。

| 変数 | 既定値 | 用途 |
| --- | --- | --- |
| `AWS_REGION` | `ap-northeast-1` | AWSリージョン |
| `DOMAIN_NAME` | `handson-vector-<account>` | OpenSearchドメイン名 |
| `INSTANCE_TYPE` | `or2.xlarge.search` | データノードの種類 |
| `ALLOWED_CIDRS` | 実行マシンのIP `/32` | APIとDashboardsの接続元 |
| `PIPELINE_NAME` | `book-vector-10m-32x` | OSIS pipeline名 |
| `INDEX_NAME` | `syn10m_autoopt32x` | 投入先index名 |
| `SOURCE_PREFIX` | fullではデータフォルダ全体 | OSISが読み込むS3 key prefix |
| `TARGET_COUNT` | smokeでは50,000 | pipelineを停止する件数 |

## 共有データセット

投入元は次の公開S3 prefixです。

```text
s3://opensearch-book-handson-data-153766774185/synthetic-cohere-like-parquet-10m-v2/data/
```

バケット名には著者のAWSアカウントIDが含まれますが、これは全読者が参照する共有データの配置先です。OpenSearchのendpointとOSIS用IAM roleは、読者自身のAWSアカウントに作成されます。

## Auto-Optimizeについて

Auto-Optimizeジョブの作成とrecommendation取得はAWSコンソールのUIに依存し、AWS CLIだけでは再現できません。そのため、読者が実行する手順からは外しています。

第4章では、Auto-Optimizeを使って`on_disk + 32x`が提案された過去の実測をケーススタディとして扱います。このハンズオンは、その結果を固定mappingとして再利用し、UI以降の工程を再現します。

## 発展: S3 Vectors

同じ1000万件を`or2.medium.search`とS3 Vectorsで試す手順は、次を参照してください。

- [S3 Vectorsを`or2.medium.search`で比較する](./osis/s3vector_or2_medium_experiment.md)

通常のハンズオンとはmappingと削除順序が異なります。先に主な手順のリソースを削除してから実行してください。

## dry-run

AWSリソースを作成せず、コマンド生成とプレースホルダー置換を確認できます。

```bash
DRY_RUN=1 MODE=smoke ./scripts/run.sh
DRY_RUN=1 CONFIRM_DESTROY=yes ./scripts/destroy.sh
```

シェル構文、JSON、TypeScript、別アカウントでのCDK synth、dry-runをまとめて確認する場合は、次を実行します。

```bash
./scripts/test-local.sh
```
