# ハンズオン3: ベクトル検索の弱点を補完する

第5章「ベクトル検索の限界と実務上の補完策」に対応するハンズオンです。架空の家電メーカーが持つ製品情報、エラーコード、サポート事例、保証条件など180チャンクを検索し、問い合わせに応じて検索方式を使い分けます。

- `vector`: ベクトル検索のみ
- `fulltext`: BM25による全文検索
- `exact`: `keyword`型フィールドを`term` queryで完全一致
- `hybrid`: 全文検索とベクトル検索を正規化して統合
- `hybrid_rerank`: ハイブリッド検索の上位10件をrerankerで再整列
- `hybrid_context`: 検索後に同じ親文書の前後チャンクを復元

文書種別filterは独立した検索方式ではありません。`vector`、`fulltext`、`hybrid`、`hybrid_rerank`の検索対象を、検索前に限定する条件として使います。

![家電サポート文書検索の構成](./docs/search-flow.svg)

## リポジトリを取得する

```bash
git clone https://github.com/oimo23/opensearch-book-handson.git
cd opensearch-book-handson/03-search-quality-lab
```

## 事前条件

- Docker Desktopが起動していること
- 初回のモデル取得に必要なインターネット接続があること
- Dockerへ6GB程度のメモリを割り当てられること
- `curl`と`jq`を実行できること
- 評価スクリプトも使う場合はPython 3.10以上があること

初回起動では埋め込みモデル`cl-nagoya/ruri-v3-310m`を取得し、180チャンクをベクトル化します。`hybrid_rerank`を初めて実行するときは`BAAI/bge-reranker-v2-m3`も取得します。

再現条件を揃えるため、OpenSearch、OpenSearch Dashboards、PythonのDockerイメージはdigestまで、Python依存とモデルはバージョンまたはcommit SHAまで固定しています。モデルのライセンスは[THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)を参照してください。

## 起動と確認

```bash
docker compose up --build
```

別のターミナルから次のURLを開けます。

- 家電サポート文書検索デモ: http://localhost:8100
- OpenSearch Dashboards: http://localhost:5601
- OpenSearch API: http://localhost:9200

APIの起動確認:

```bash
curl -s http://localhost:8100/api/health | jq
```

6方式と文書種別filterの基本動作を確認:

```bash
./scripts/smoke-test.sh
```

第5章の主要結果を確認:

```bash
./scripts/verify-chapter5-results.sh
```

初回のrerankではモデルの取得と読み込みに時間がかかることがあります。

## ケース1: 使えるfilterを先に適用する

次の問い合わせを考えます。

> サポート事例の中から、ファームウェア3以降で、ソフトウェアを更新した後、再登録や再起動を試しても接続できなかったものを探す

このデモでは文書種別だけを構造化しており、`document_type`へのfilterを利用できます。「サポート事例の中から」は検索文へ入れず、残りを自然文検索へ渡します。

```bash
query='ファームウェア3以降で、ソフトウェアを更新した後、再登録や再起動を試しても接続できなかったもの'

for filters in '{}' '{"document_type":"support_case"}'; do
  curl -s http://localhost:8100/api/search \
    -H 'Content-Type: application/json' \
    -d "{\"query\":\"${query}\",\"mode\":\"hybrid\",\"top_k\":10,\"filters\":${filters}}" \
    | jq '{filters: .request_body.query.hybrid.queries[0].bool.filter, hits: [.hits[] | {rank, id, document_type}]}'
done
```

filterなしではファームウェアのリリースノートも上位に入ります。`document_type=support_case`を指定すると、候補はサポート事例だけになります。

一方、ファームウェアのメジャーバージョンは構造化フィールドとして保持していません。そのため、ファームウェア2の事例も候補に残ります。バージョンを必須条件として確実に判定する必要があるなら、取り込み時に数値フィールドとして構造化し、`range` queryをfilterへ追加する設計が必要です。

## ケース2: 型番と症状を両方使う

`WM-A410でE42が出たときの給水エラーの対処`を3方式で検索します。

```bash
for mode in vector fulltext hybrid; do
  curl -s http://localhost:8100/api/search \
    -H 'Content-Type: application/json' \
    -d "{\"query\":\"WM-A410でE42が出たときの給水エラーの対処\",\"mode\":\"${mode}\",\"top_k\":5}" \
    | jq '{mode, hits: [.hits[] | {rank, id, title, score}]}'
done
```

正解の`error-wm-a410-e42`は、ベクトル検索では修理事例の後の2位、全文検索とハイブリッド検索では1位です。ベクトル検索は「給水できない」という意味を拾いますが、型番とエラーコードの一致を最優先にはしません。ハイブリッド検索は、文字列一致と意味の近さの両方を候補生成へ使います。

エラー識別子だけで1件へ限定したい場合は、関連度を調整せず完全一致を使います。

```bash
for mode in fulltext exact; do
  curl -s http://localhost:8100/api/search \
    -H 'Content-Type: application/json' \
    -d "{\"query\":\"WM-A410-E42\",\"mode\":\"${mode}\",\"top_k\":5}" \
    | jq '{mode, ids: [.hits[].id]}'
done
```

全文検索は同じ型番の別エラーも候補に残しますが、`exact`は`identifiers.raw`への`term` queryで`error-wm-a410-e42`だけを返します。

## ケース3: 候補10件をrerankする

ケース1と同じ問い合わせを使います。文書種別はfilterへ分けますが、ファームウェア3以降という条件は検索文に残します。

```bash
query='ファームウェア3以降で、ソフトウェアを更新した後、再登録や再起動を試しても接続できなかったもの'
for mode in hybrid hybrid_rerank; do
  curl -s http://localhost:8100/api/search \
    -H 'Content-Type: application/json' \
    -d "{\"query\":\"${query}\",\"mode\":\"${mode}\",\"top_k\":10,\"filters\":{\"document_type\":\"support_case\"}}" \
    | jq '{mode, hits: [.hits[] | {rank, id, score, rerank_score}]}'
done
```

hybridでは、更新後に接続が切れたものの再起動で解決した`support-connect-13`が1位です。問い合わせに最も合う`support-connect-03`は2位ですが、rerank後は1位へ上がります。rerankは候補を検索し直さず、hybridが取得した同じ10件を質問との適合度で並べ替えます。

## ケース4: 前後チャンクを復元する

保証ガイドは「原則」「申請に必要な情報」「対象外」の3チャンクに分かれています。

```bash
curl -s http://localhost:8100/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"WM-A410の無償交換が認められる条件と、対象外になる場合","mode":"hybrid_context","top_k":5}' \
  | jq '{mode, hits: [.hits[] | {rank, id, title, context_chunks}]}'
```

1位の`warranty-context-wm-a410-1`には、同じ`parent_id`を持つ3チャンクが`chunk_order`順で付加されます。検索で1チャンクに到達した後、回答に必要な前提や例外を同じ親文書から補う処理です。

## 評価セットを実行する

`data/evaluation_queries.json`にはdev 50件とtest 50件があります。devはハイブリッド重みの調整にだけ使い、testは設定固定後の最終評価に使います。

```bash
python3 scripts/validate_dataset.py
python3 scripts/evaluate.py --split test --output docs/results/test-results.json
```

候補生成はHit Rate@3、Hit Rate@10、MRR@5、NDCG@5で評価します。文脈復元は必要な全チャンクが揃った割合と、追加したチャンクのうち必要だった割合を記録します。完全一致とfilterは順位ではなく、返却結果が指定条件を満たした割合を検査します。

著者がdevセットだけで重みを再調整する場合:

```bash
python3 scripts/tune_hybrid.py
```

test結果を確認した後で、testクエリ、正解ラベル、検索設定を変更しないでください。

## Dashboardsで直接試す

APIレスポンスの`request_body`に、OpenSearchへ送ったリクエストが含まれます。`body_vector.vector`を省略せずコピーし、Dev Toolsから次へ送信できます。

```text
POST appliance-support-demo-v1/_search?search_pipeline=appliance-hybrid
```

## 設定を変更する

```bash
cp .env.example .env
```

主な設定は`CANDIDATE_SIZE`、`HYBRID_KEYWORD_WEIGHT`、`HYBRID_VECTOR_WEIGHT`、`ENABLE_RERANK`、`EMBEDDING_MODEL_NAME`、`RERANK_MODEL_NAME`です。モデルを変更する場合は、次元数、入力prefix、ライセンス、用途を確認してください。現在のmappingは768次元です。

## 片付け

```bash
docker compose down
```

OpenSearchのデータとモデルキャッシュも削除する場合:

```bash
docker compose down -v
```

## 注意点

- 代表例は処理の違いを理解するための制御された例です。一般的な傾向は分離したtestセットで確認します。
- rerankは候補10件の順序だけを変えます。候補に入らなかった文書は復活できません。
- 文脈復元は必要なチャンクを補える一方、不要な前後チャンクも増やすことがあります。
- 実データへ適用する場合は、自分たちの問い合わせと正解集合で評価してください。
