# OSIS設定

このディレクトリには、1000万件のParquetデータをOpenSearchへ投入するmappingとpipelineテンプレートがあります。

## 主な手順

- `syn10m-autoopt32x.index.json`
  - 2026年8月23日に実機検証した固定mappingです。
  - Faiss、HNSW、`on_disk`、`32x`、1シャード、レプリカ0です。
- `synthetic-10m-autoopt32x.pipeline.json`
  - 事前作成した`32x` indexへ投入します。
  - endpoint、IAM role ARN、region、index名はプレースホルダーです。

`../scripts/create-pipeline.sh`がCloudFormation出力を読み、次の値を自動で置換します。

- `__DOMAIN_ENDPOINT__`
- `__INGESTION_ROLE_ARN__`
- `__AWS_REGION__`
- `__INDEX_NAME__`
- `__SOURCE_PREFIX__`

生成後の設定は`.handson/<pipeline-name>.pipeline.json`へ保存されます。

## 比較用

- `synthetic-10m-faiss2x.pipeline.json`
  - Faiss、HNSW、`on_disk`、`2x`をOSISのindex templateから作成します。
- `synthetic-10m-faiss16x.pipeline.json`
  - Faiss、HNSW、`on_disk`、`16x`をOSISのindex templateから作成します。
- `create_pipeline_example.sh`
  - `2x`テンプレートを動的なendpointとrole ARNで実行します。
- `create_pipeline_16x_example.sh`
  - `16x`テンプレートを動的なendpointとrole ARNで実行します。

比較用pipelineを使う場合も、先に`../scripts/deploy.sh`でドメインとIAM roleを作成してください。

## S3 Vectors

- `syn10m-s3vector.index.json`
  - `s3vector` engineを使うindex mappingです。
- `synthetic-10m-s3vector.pipeline.json`
  - 事前作成したS3 Vectors indexへ投入します。
- `s3vector_or2_medium_experiment.md`
  - `or2.medium.search`での構築、投入、計測、削除手順です。

## 共有データ

すべてのpipelineは、次の公開データを読みます。

```text
s3://opensearch-book-handson-data-153766774185/synthetic-cohere-like-parquet-10m-v2/data/
```

200個のParquetファイルに、1000万件、1024次元のsyntheticデータが入っています。`delete_s3_objects_on_read`は`false`であり、読者の実行によって共有データが削除されることはありません。
