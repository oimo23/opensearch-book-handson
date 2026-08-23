# 実測結果

第5章へ掲載したレスポンスの確認用メモです。本文用の制御された代表例と、設定調整に使用していないtestセットの結果を分けて記録します。

## 環境

- test評価日: 2026-08-23
- 代表例再取得日: 2026-08-23
- 評価セット: v3
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

## v1からv3への変更

v1のtest結果を確認した後に問い合わせを上書きせず、別バージョンとしてv2を作成しました。主要4カテゴリを各split 5問から10問へ、文脈と厳密条件を各3問・2問から各5問へ増やしています。

validatorは`case_group`に加えて、正解文書、期待文書、必須文脈チャンクがdevとtestをまたがないことを直接検査します。v1の問い合わせと結果は`data/evaluation_queries-v1.json`と`docs/results/test-results-v1.json`へ保存しています。

v3では、filterとrerankの役割が重ならないよう、顧客対応事例へ「説明不足のみ」「承認記録不足のみ」「両方不足」のhard negativeを追加しました。問い合わせはv2から変更していません。v2のコーパスに対する問い合わせと結果は`data/evaluation_queries-v2.json`と`docs/results/test-results-v2.json`へ保存しています。

## devによるhybrid重みの選定

testセットへ触れる前に、devの意味検索、識別子、混合、否定・例外の40問でmacro NDCG@5を比較しました。

| 全文 / vector | macro NDCG@5 |
|---|---:|
| 0.3 / 0.7 | 0.8641 |
| 0.4 / 0.6 | 0.9064 |
| 0.45 / 0.55 | 0.9164 |
| 0.5 / 0.5 | 0.9723 |
| 0.6 / 0.4 | 0.9815 |
| 0.7 / 0.3 | 0.9723 |

全文検索0.6、vector 0.4を採用し、以後のv3 test評価では変更していません。

## 制御された代表例

### 第19条

`vector`の上位3件には`rule-019`が入りませんでした。`fulltext`では`rule-019`が1位、`rule-019-2`が2位になり、`exact`では`rule-019`の1件だけが返りました。

### 問い合わせ表現による候補の取りこぼし

同じ`elderly-case-03`を、意味的な言い換えと事例IDの2通りで検索しました。

| 問い合わせ | `vector` | `fulltext` | `hybrid` |
|---|---:|---:|---:|
| 説明した証拠が残っておらず、後から適切だったか確かめられない高齢者販売 | 1位 | 8位 | 3位 |
| `CASE-ELDERLY-03` | 7位 | 1位 | 1位 |

`vector`と`fulltext`は、得意な問い合わせが逆になりました。`hybrid`はどちらでも正解を上位3件へ残しています。事例IDだけと判定できる場合は`exact`を使う方が単純ですが、自然文と重要語が混在する問い合わせ群では、異なる検索方式の候補を残す意味があります。

### 同じ問い合わせで候補生成とrerankを比較する

問い合わせは「高齢者への販売について、後日になって対応の妥当性を裏付けられない事例」です。文書種別が事例、顧客が75歳以上という同じfilterと候補数10件を、4方式で固定しました。問題あり判定と金額条件は使っていません。

| 方式 | `elderly-case-03`の順位 |
|---|---:|
| `vector` | 2位 |
| `fulltext` | 4位 |
| `hybrid` | 3位 |
| `hybrid_rerank` | 1位 |

この1問ではvectorが最も上位であり、hybridが常に順位を改善するわけではありません。hybridは`elderly-case-03`を10件の候補へ残し、同じ候補集合をrerankすると3位から1位になりました。

### rerank前後の上位3件

| 順位 | `hybrid` | `hybrid_rerank` |
|---:|---|---|
| 1 | `elderly-case-11`（承認後の金額変更） | `elderly-case-03`（確認方法の記録なし） |
| 2 | `elderly-case-02`（販売を見送り、問題なし） | `elderly-case-02`（販売を見送り、問題なし） |
| 3 | `elderly-case-03`（確認方法の記録なし） | `elderly-case-11`（承認後の金額変更） |

候補集合は同じ10件のまま、`elderly-case-03`が3位から1位へ上がりました。rerank scoreは`0.4227`です。問題なしの`elderly-case-02`も2位に残っているため、rerank結果を問題判定として使えません。test全体でも悪化した問い合わせがあり、適用前の回帰評価が必要です。

### 文脈復元

高齢顧客への販売について、承認の原則、申請項目、継続購入時の簡易承認を3チャンクへ分割しました。`hybrid_context`では同じ`parent_id`を使い、3チャンクすべてを`context_chunks`へ復元しました。

## 未調整testセットの結果

v3 test 50問を、設定固定後に初めて実行した結果です。

| 種別 | 方式 | Hit@3 | Hit@10 | MRR@5 | NDCG@5 |
|---|---|---:|---:|---:|---:|
| 意味的な言い換え | `vector` | 0.900 | 0.900 | 0.900 | 0.900 |
| 意味的な言い換え | `fulltext` | 0.800 | 1.000 | 0.775 | 0.806 |
| 意味的な言い換え | `hybrid` | 1.000 | 1.000 | 0.883 | 0.913 |
| 識別子・専門語 | `vector` | 0.100 | 0.400 | 0.145 | 0.182 |
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
