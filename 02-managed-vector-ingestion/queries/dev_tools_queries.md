# Dev Tools Query Examples

1024 次元のベクトルをそのまま Dev Tools に貼り付けると、途中で欠けたり、エディタの色分けが崩れたりしやすいです。  
そのため、このハンズオンでは **検索テンプレートを 1 回だけ登録して、短いクエリで呼び出す** 形をおすすめします。

対象文書
- `id`: `ja-synthetic-00000000`
- `title`: `政治史 クラスタ26 文書0`

まず、次のファイルを使って検索テンプレートを登録します。

- [register_search_template.md](./register_search_template.md)
- [register_search_template.json](./register_search_template.json)

登録後は、Dev Tools で次の短いクエリだけを実行すれば大丈夫です。

```json
GET syn10m_autoopt32x/_search/template
{
  "id": "syn10m_autoopt32x_knn_sample"
}
```

巨大なベクトル本体を確認したい場合は、次の生ファイルを参照してください。

- [dev_tools_query_syn10m_full.json](./dev_tools_query_syn10m_full.json)

## キャッシュを明示的に解放したいとき

`k-NN` の試行後に 502 や極端な遅延が出たときは、次のリクエストで index のキャッシュを明示的に解放できます。

```json
POST syn10m_autoopt32x/_cache/clear
```

ドメイン全体に対して行いたい場合は、次でも構いません。

```json
POST _cache/clear
```

## k-NN メモリ使用率を確認したいとき

`graph_memory_usage_percentage` や circuit breaker の状態は、次の k-NN stats で確認できます。

```json
GET _plugins/_knn/stats
```

特に見たい項目は次です。

- `graph_memory_usage_percentage`
- `cache_capacity_reached`
- `circuit_breaker_triggered`
- `indices_in_cache`
