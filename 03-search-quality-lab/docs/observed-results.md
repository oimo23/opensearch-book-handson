# 家電サポート文書検索の実測記録

## 再現条件

- 実行日: 2026-08-24
- OpenSearch: 2.19.1
- index: `appliance-support-demo-v1`
- 文書数: 180チャンク、12文書群
- 評価問い合わせ: dev 50件、test 50件
- 埋め込みモデル: `cl-nagoya/ruri-v3-310m` revision `18b60fb8c2b9df296fb4212bb7d23ef94e579cd3`
- reranker: `BAAI/bge-reranker-v2-m3` revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`
- rerank候補数: 10件
- ハイブリッド重み: 全文検索0.7、ベクトル検索0.3

ハイブリッド重みはdevセットだけで比較しました。macro NDCG@5は全文検索/ベクトル検索が0.3/0.7のとき0.8162、0.5/0.5のとき0.8739、0.6/0.4のとき0.8743、0.7/0.3のとき0.8901となり、0.7/0.3に固定しました。その後、testセットを一度実行しています。

## 代表例1: 型番と症状

問い合わせは「WM-A410でE42が出たときの給水エラーの対処」です。期待文書は`error-wm-a410-e42`です。

| 順位 | vector | fulltext | hybrid |
|---:|---|---|---|
| 1 | `repair-case-11` | `error-wm-a410-e42` | `error-wm-a410-e42` |
| 2 | `error-wm-a410-e42` | `error-wm-a410-e24` | `error-wm-a410-e24` |
| 3 | `error-wm-a410s-e42` | `error-wm-a410-c07` | `error-wm-a410-u11` |

ベクトル検索は、E42が表示され給水できない修理事例を1位にしました。全文検索では期待文書が1位に表示されましたが、同じ型番のエラー説明4件は同点です。ハイブリッド検索では4件に順位差がつき、期待文書が単独の1位になりました。

## 代表例2: rerank

問い合わせは「ソフトウェアを更新した後、再登録や再起動を試しても接続できなかった事例」です。`document_type=support_case`と`firmware_major>=3`で絞り、期待文書を`support-connect-03`としました。

| 順位 | hybrid | hybrid + rerank |
|---:|---|---|
| 1 | `support-connect-14` | `support-connect-03` |
| 2 | `support-connect-03` | `support-connect-13` |
| 3 | `support-connect-13` | `support-connect-01` |

hybridの上位10件をそのままrerankerへ渡すと、期待文書が2位から1位へ上がりました。候補集合は変わっていません。

## 代表例3: 文脈復元

問い合わせは「WM-A410の無償交換が認められる条件と、対象外になる場合」です。1位は`warranty-context-wm-a410-1`で、同じ親文書の次の3チャンクを復元しました。

1. 購入から12か月以内の製造上の不具合を無償修理または交換の対象とする原則
2. 申請に必要な製造番号、購入日、エラー、確認手順
3. 清掃不足、誤設置、異物混入、業務利用などの対象外条件

## testセットの結果

| 問い合わせ種別 | 比較 | 主な結果 |
|---|---|---|
| 意味的な言い換え | fulltext / vector / hybrid | NDCG@5は0.413 / 0.763 / 0.588で、vectorが最良 |
| 型番・エラーコード | fulltext / vector / hybrid | NDCG@5は0.900 / 0.363 / 0.863で、fulltextが最良 |
| 意味とキーワードの混合 | fulltext / vector / hybrid | NDCG@5は0.813 / 0.676 / 0.850で、hybridが最良 |
| 否定・例外 | hybrid / hybrid + rerank | NDCG@5は0.913 / 1.000へ改善 |
| 文脈復元 | hybrid / hybrid + context | Context Completenessは0.733 / 1.000へ改善 |
| 完全一致・filter | exact / hybrid + filter | 条件適合率1.000、条件違反0件 |

文脈復元のContext precisionは0.617でした。必要なチャンクは揃いましたが、検索結果の別の親文書も展開したため不要なチャンクが増えています。また、否定・例外では期待文書がすべて1位になった一方、紛らわしい反対例が上位5件へ残った問い合わせもありました。rerankも文脈復元も、後段の回答生成に必要な判断を保証するものではありません。

機械可読な全結果は`docs/results/test-results.json`、代表例のレスポンスは`docs/results/controlled-examples.json`に保存しています。
