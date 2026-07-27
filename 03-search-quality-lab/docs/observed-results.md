# 実測結果

第5章へ掲載したレスポンスの確認用メモです。本文用の制御された代表例と、設定調整に使用していないtestセットの結果を分けて記録します。

## 環境

- 検証日: 2026-07-27
- 評価セット: v2
- OpenSearch: 2.19.1
- index: `fin-doc-search-demo-v3`
- 文書数: 180チャンク、12文書群
- 評価問い合わせ: dev 50問、test 50問
- 埋め込み: `cl-nagoya/ruri-v3-310m`
- 埋め込みrevision: `18b60fb8c2b9df296fb4212bb7d23ef94e579cd3`
- reranker: `BAAI/bge-reranker-v2-m3`
- reranker revision: `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`
- rerank候補数: 10
- hybrid重み: 全文検索0.6、ベクトル検索0.4
- 実行環境: macOS arm64、Docker Desktop

## v1からv2への変更

v1のtest結果を確認した後に問い合わせを上書きせず、別バージョンとしてv2を作成しました。主要4カテゴリを各split 5問から10問へ、文脈と厳密条件を各3問・2問から各5問へ増やしています。

validatorは`case_group`に加えて、正解文書、期待文書、必須文脈チャンクがdevとtestをまたがないことを直接検査します。v1の問い合わせと結果は`data/evaluation_queries-v1.json`と`docs/results/test-results-v1.json`へ保存しています。

## devによるhybrid重みの選定

testセットへ触れる前に、devの意味検索、識別子、混合、否定・例外の40問でmacro NDCG@5を比較しました。

| 全文 / vector | macro NDCG@5 |
|---|---:|
| 0.3 / 0.7 | 0.8670 |
| 0.4 / 0.6 | 0.9064 |
| 0.45 / 0.55 | 0.9164 |
| 0.5 / 0.5 | 0.9723 |
| 0.6 / 0.4 | 0.9815 |
| 0.7 / 0.3 | 0.9723 |

全文検索0.6、vector 0.4を採用し、以後のv2 test評価では変更していません。

## 制御された代表例

### 第19条

`vector`の上位3件には`rule-019`が入りませんでした。`fulltext`では`rule-019`が1位、`rule-019-2`が2位になり、`exact`では`rule-019`の1件だけが返りました。

### rerank

問い合わせは「高齢者への勧誘で問題になった事例」です。

| 方式 | 正解`elderly-case-01`の順位 |
|---|---:|
| `hybrid` | 4位 |
| `hybrid_rerank` | 1位 |

代表例では具体的な不適切勧誘事例が上昇しました。ただし、これは仕組みを説明するための例であり、test全体の改善を意味しません。

### 文脈復元

高額取引の原則、分割注文の合算、再投資時の例外を3チャンクへ分割しました。`hybrid_context`では同じ`parent_id`を使い、3チャンクすべてを`context_chunks`へ復元しました。

## 未調整testセットの結果

v2 test 50問を、設定固定後に初めて実行した結果です。

| 種別 | 方式 | Hit@3 | Hit@10 | MRR@5 | NDCG@5 |
|---|---|---:|---:|---:|---:|
| 意味的な言い換え | `vector` | 0.900 | 0.900 | 0.900 | 0.900 |
| 意味的な言い換え | `fulltext` | 0.800 | 1.000 | 0.775 | 0.806 |
| 意味的な言い換え | `hybrid` | 1.000 | 1.000 | 0.900 | 0.926 |
| 識別子・専門語 | `vector` | 0.100 | 0.400 | 0.150 | 0.186 |
| 識別子・専門語 | `fulltext` | 1.000 | 1.000 | 1.000 | 1.000 |
| 識別子・専門語 | `hybrid` | 1.000 | 1.000 | 1.000 | 1.000 |
| 意味とキーワードの混合 | `vector` | 0.900 | 0.900 | 0.733 | 0.776 |
| 意味とキーワードの混合 | `fulltext` | 0.900 | 1.000 | 0.900 | 0.900 |
| 意味とキーワードの混合 | `hybrid` | 1.000 | 1.000 | 0.933 | 0.950 |
| 否定・例外 | `hybrid` | 1.000 | 1.000 | 0.933 | 0.950 |
| 否定・例外 | `hybrid_rerank` | 0.900 | 1.000 | 0.900 | 0.900 |

意味的な言い換えと混合問い合わせでは、hybridだけがHit@3 1.000でした。識別子ではfulltextとhybridが同率で、vectorはHit@3 0.100でした。

否定・例外10問では、rerankにより1問の正解が3位から上位5件外へ下がりました。rerankは代表例を改善しましたが、test全体のMRR@5とNDCG@5は悪化しています。

## 文脈展開と厳密条件

文脈問い合わせ5問では、hybridとhybrid_contextのどちらも正しい親文書を上位3件で取得できました。必要チャンクのContext Completenessは`0.800`から`1.000`へ改善しました。

一方、複数の親文書を展開したため、取得した文脈チャンクのうち正解チャンクが占めるContext precisionは`0.350`でした。親文書展開は不足を補いますが、展開対象を絞らなければ不要な文脈も増えることが分かります。

完全一致3問とfilter 2問はすべて期待文書を取得しました。filterは返却された全hitの`document_type`、年齢、金額、判定結果を検査し、条件違反は0件でした。

## 再検証

```bash
python3 scripts/validate_dataset.py
./scripts/smoke-test.sh
python3 scripts/evaluate.py --split test --output docs/results/test-results.json
```

完全なレスポンスは`docs/results/controlled-examples.json`、集計値と問い合わせ別順位は`docs/results/test-results.json`に保存しています。
