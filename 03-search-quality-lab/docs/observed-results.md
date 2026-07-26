# 実測結果

第5章へ掲載したレスポンスの確認用メモです。本文用の制御された代表例と、設定調整に使用していないtestセットの結果を分けて記録します。

## 環境

- 検証日: 2026-07-27
- OpenSearch: 2.19.1
- index: `fin-doc-search-demo-v3`
- 文書数: 180チャンク、12文書群
- 埋め込み: `cl-nagoya/ruri-v3-310m`
- 埋め込みrevision: `18b60fb8c2b9df296fb4212bb7d23ef94e579cd3`
- reranker: `BAAI/bge-reranker-v2-m3`
- reranker revision: `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`
- rerank候補数: 10
- hybrid重み: 全文検索0.5、ベクトル検索0.5
- 実行環境: macOS arm64、Docker Desktop

## devによるhybrid重みの選定

testセットへ触れる前に、devの意味検索、識別子、混合、否定・例外の20問でmacro NDCG@5を比較しました。

| 全文 / vector | macro NDCG@5 |
|---|---:|
| 0.3 / 0.7 | 0.8702 |
| 0.4 / 0.6 | 0.9096 |
| 0.45 / 0.55 | 0.9131 |
| 0.5 / 0.5 | 0.9631 |
| 0.6 / 0.4 | 0.9631 |
| 0.7 / 0.3 | 0.9446 |

同率のうち中立的な0.5 / 0.5を採用し、以後のtest評価では変更していません。

## 制御された代表例

### 第19条

`vector`の上位3件には`rule-019`が入りませんでした。`fulltext`では`rule-019`が1位、`rule-019-2`が2位になり、`exact`では`rule-019`の1件だけが返りました。

### rerank

問い合わせは「高齢者への勧誘で問題になった事例」です。

| 方式 | 上位3件 |
|---|---|
| `hybrid` | `market-case-05`、`elderly-case-02`、`elderly-case-01` |
| `hybrid_rerank` | `elderly-case-01`、`elderly-case-02`、`elderly-case-14` |

正解として扱う不適切勧誘事例`elderly-case-01`は3位から1位へ上がりました。これは仕組みを説明するための代表例であり、test全体の改善を意味しません。

### 文脈復元

高額取引の原則、分割注文の合算、再投資時の例外を3チャンクへ分割しました。`hybrid_context`では同じ`parent_id`を使い、3チャンクすべてを`context_chunks`へ復元しました。

## 未調整testセットの結果

test 25問を、設定固定後に初めて実行した結果です。

| 種別 | 方式 | Hit@3 | Hit@10 | MRR@5 | NDCG@5 |
|---|---|---:|---:|---:|---:|
| 意味的な言い換え | `vector` | 1.000 | 1.000 | 1.000 | 1.000 |
| 意味的な言い換え | `fulltext` | 0.600 | 1.000 | 0.550 | 0.612 |
| 意味的な言い換え | `hybrid` | 1.000 | 1.000 | 0.900 | 0.926 |
| 識別子・専門語 | `vector` | 0.200 | 0.400 | 0.250 | 0.286 |
| 識別子・専門語 | `fulltext` | 1.000 | 1.000 | 1.000 | 1.000 |
| 識別子・専門語 | `hybrid` | 1.000 | 1.000 | 0.800 | 0.852 |
| 意味とキーワードの混合 | `vector` | 0.800 | 0.800 | 0.567 | 0.626 |
| 意味とキーワードの混合 | `fulltext` | 0.800 | 1.000 | 0.800 | 0.800 |
| 意味とキーワードの混合 | `hybrid` | 1.000 | 1.000 | 0.900 | 0.926 |
| 否定・例外 | `hybrid` | 1.000 | 1.000 | 1.000 | 1.000 |
| 否定・例外 | `hybrid_rerank` | 1.000 | 1.000 | 1.000 | 1.000 |

意味的な言い換えではvector、識別子ではfulltextが最良でした。混合問い合わせではhybridだけがHit@3 1.000となりました。否定・例外5問はhybridの時点で全問1位だったため、rerankによる集計値の改善はありませんでした。

文脈問い合わせ3問では、必要な3チャンクのContext Completenessが`hybrid`の0.778から`hybrid_context`の1.000へ改善しました。完全一致とfilterは期待条件をすべて満たし、禁止文書の混入は0件でした。

## レイテンシー

ウォームアップ後、方式ごとに5回実行しました。

| 方式 | p50 total | p95 total | p50 search | p50 rerank |
|---|---:|---:|---:|---:|
| `vector` | 212ms | 213ms | 6ms | 0ms |
| `fulltext` | 5ms | 5ms | 5ms | 0ms |
| `hybrid` | 217ms | 222ms | 10ms | 0ms |
| `hybrid_rerank` | 2714ms | 2783ms | 12ms | 2487ms |
| `hybrid_context` | 228ms | 230ms | 11ms | 0ms |
| `exact` | 2ms | 2ms | 2ms | 0ms |
| `hybrid_filter` | 205ms | 229ms | 8ms | 0ms |

このローカルCPU環境ではrerankが約2.5秒を占めました。否定・例外のtest集計値は改善していないため、すべての問い合わせへ一律に適用する根拠はありません。

## 再検証

```bash
python3 scripts/validate_dataset.py
./scripts/smoke-test.sh
python3 scripts/evaluate.py --split test --latency-runs 5
```

完全なレスポンスは`docs/results/controlled-examples.json`、集計値と問い合わせ別順位は`docs/results/test-results.json`に保存しています。
