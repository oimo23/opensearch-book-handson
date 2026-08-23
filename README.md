# opensearch-book-handson

このリポジトリは、技術書『大規模ベクトル検索実践ガイド──AWS 上の OpenSearch で構築する 1000 万件レベルの検索基盤』に対応するハンズオン用リポジトリです。

- 技術書典の書籍ページ  
  https://techbookfest.org/product/bU1x8wGX5Jz1Zynusb2Qcw?productVariantID=1cgfbBf8DCLiYLjGa4jqjw

本リポジトリには、書籍内で扱うハンズオンの実行コードや手順書をまとめています。

## 紙の本からコマンドを利用する

書籍に掲載したコマンドは、このリポジトリのREADMEからコピーできます。最初にリポジトリを取得してください。

```bash
git clone https://github.com/oimo23/opensearch-book-handson.git
cd opensearch-book-handson
```

各章の手順は次のページにあります。

- [ハンズオン1: ローカルOpenSearchとHugging Faceモデル](./01-local-hf-vector-search/README.md)
- [ハンズオン2: managed vector ingestion](./02-managed-vector-ingestion/README.md)
- [ハンズオン3: ベクトル検索の弱点と補完策](./03-search-quality-lab/README.md)

## 含まれているハンズオン

- `01-local-hf-vector-search`  
  ローカルの OpenSearch と埋め込みモデルを使って、ベクトル検索の基本的な流れを体験するハンズオンです。

- `02-managed-vector-ingestion`  
  Amazon OpenSearch Service の managed vector ingestion と auto-optimize を使って、大規模ベクトルデータの取り込みと index build を体験するハンズオンです。

- `03-search-quality-lab`
  架空の家電メーカーの製品・サポート文書を使い、ベクトル検索の弱点と、全文検索、filter、hybrid、rerank、文脈復元による補完を比較するハンズオンです。

各ディレクトリのREADMEに、前提条件と実行手順を記載しています。書籍の該当章を参照しながら進めてください。
