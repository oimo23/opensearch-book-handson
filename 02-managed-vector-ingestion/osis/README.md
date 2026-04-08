# OSIS Pipeline テンプレート

このディレクトリには、ハンズオン2で使う OSIS pipeline の雛形を置いています。  
まだ pipeline は起動しません。まずは設定ファイルだけを用意し、必要になった時点で AWS コンソールまたは CLI から作成します。

## 置いてあるもの

- `synthetic-10m-faiss2x.pipeline.json`
  - 10M の synthetic Parquet を入力とする pipeline 設定です。
  - auto-optimize が返した `Faiss + on_disk + 2x` を土台にしています。
  - 以前に高い ingest スループットが出たときの tuned 設定も、`settings` 側に寄せています。

- `synthetic-10m-faiss16x.pipeline.json`
  - 10M の synthetic Parquet を入力とする pipeline 設定です。
  - auto-optimize が返した `Faiss + on_disk + 16x` を土台にしています。
  - UI では触りにくい `refresh_interval` や `approximate_threshold` を加えた版です。

- `create_pipeline_example.sh`
  - `2x` 版を CLI で作成する例です。

- `create_pipeline_16x_example.sh`
  - `16x` 版を CLI で作成する例です。

## この設定の意図

今回の `16x` 版 pipeline 設定は、次の方針で作っています。

- engine: `faiss`
- mode: `on_disk`
- compression_level: `16x`
- `m = 16`
- `ef_construction = 128`
- `ef_search = 128`

さらに、以前にスループットが高く出た時の index settings として、次も入れています。

- `refresh_interval = 300s`
- `number_of_shards = 1`
- `number_of_replicas = 0`
- `index.knn.advanced.approximate_threshold = 100000`
- `index.knn.remote_index_build.enabled = true`
- `index.knn.remote_index_build.size.min = 5mb`

source 側も、以前の tuned run に寄せて `workers = 5` にしています。

## 入力データ

今回の入力 Parquet は次の公開 prefix を前提にしています。

```text
s3://opensearch-book-handson-data-153766774185/synthetic-cohere-like-parquet-10m-v2/data/
```

## 出力先ドメイン

現在の設定は、次の OpenSearch ドメインに向くようにしてあります。

```text
https://search-handson-vector-xlarge-fajj4fnh75nikgzragag3wjxyq.ap-northeast-1.es.amazonaws.com
```

## 注意

- この設定ファイルを作っただけでは pipeline は起動しません。
- `synthetic_10m_faiss_16x` や `synthetic_10m_faiss_2x` の index が既にある場合は、template 変更だけでは既存 index に反映されません。
- 実際に作成する前に、対象ドメインが `ACTIVE` であることを確認してください。
- `2x` 版は recall を優先した比較用、`16x` 版は auto-optimize の推奨を土台にした本命用、という使い分けを想定しています。
