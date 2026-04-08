# Hands-on 2: Managed Vector Ingestion 用の OpenSearch ドメインを用意する

このディレクトリでは、Amazon OpenSearch Service のドメインだけを TypeScript CDK で起動します。  
vector ingestion pipeline や auto-optimize job は、AWS コンソールから作成する前提です。

## この CDK が作るもの

- OpenSearch 3.1 のドメイン
- `or2.xlarge.search x1` の単一ノード構成
- public endpoint
- Dashboards にアクセスできる CIDR 制限付き resource policy
- 今後コンソールが作成する `VectorIngestionRole-*` からの書き込みを許可する policy
- GPU acceleration (`ServerlessVectorAcceleration`) を有効化した構成

## この CDK がまだ作らないもの

- vector ingestion pipeline
- auto-optimize job
- index template や index build

これらは、読者が AWS コンソールの UI から作成します。

## 前提

- Node.js 20 以上
- AWS CDK v2
- `cdk bootstrap` 済みの AWS アカウント

## 使い方

```bash
cd /Users/yuki/Desktop/programming/projects/opensearch-book/hands-on/02-managed-vector-ingestion
npm install
npx cdk synth
npx cdk deploy
```

## よく使う context

デフォルトでは `or2.xlarge.search x1`、`512 GiB gp3` で作ります。  
`allowedCidrs` を指定しない場合は、CDK 実行マシンのグローバル IP を自動検出して `/32` を許可します。  
OpenSearch Service は `0.0.0.0/0` のような広すぎる access policy を fine-grained access control なしでは受け付けません。Dashboards を public endpoint で使う場合でも、少なくとも `/32` や社内ネットワーク単位の **CIDR 制限** を付けて deploy してください。

```bash
npx cdk deploy \
  -c domainName=handson-vector-xlarge \
  -c instanceType=or2.xlarge.search \
  -c instanceCount=1 \
  -c ebsVolumeSize=512 \
  -c allowedCidrs=203.0.113.10/32
```

複数 CIDR を許可する場合はカンマ区切りです。

```bash
npx cdk deploy -c allowedCidrs=203.0.113.10/32,198.51.100.0/24
```

IP 自動検出に任せる場合は、context を省略してそのまま deploy できます。

```bash
npx cdk deploy
```

## 出力

deploy が終わると、次の値が出ます。

- `DomainName`
- `DomainEndpoint`
- `DashboardsUrl`
- `AllowedCidrs`

## 注意

- Dashboards を public に開く場合でも、最低でも IP 制限はかけるほうが安全です。
- vector ingestion の UI を使うと、`VectorIngestionRole-*` という service role が作られます。本 CDK は、その role が後から domain に書き込めるように access policy を先に入れています。
