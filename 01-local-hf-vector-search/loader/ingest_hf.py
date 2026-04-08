import json
import os
import time
from pathlib import Path
import sys

import boto3
import requests
from datasets import load_dataset


INDEX_MAPPING = {
    "settings": {
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 128,
            "number_of_replicas": 0,
            "refresh_interval": "30s",
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "text"},
            "url": {"type": "keyword"},
            "chunk": {"type": "text"},
            "vector": {
                "type": "knn_vector",
                "dimension": 1024,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "faiss",
                    "parameters": {"ef_construction": 128, "m": 16},
                },
            },
        }
    },
}

FIXED_NATURAL_LANGUAGE_QUERIES = [
    "ソ連の冬季スポーツで強かった人は？",
    "クモを研究する学問は何ですか？",
    "オリンピックで金メダルを取ったアイスダンス選手を知りたいです。",
]


def wait_for_opensearch(base_url: str, timeout_seconds: int = 300) -> None:
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            resp = requests.get(base_url, timeout=5)
            if resp.ok:
                return
            last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"OpenSearch did not become ready: {last_error}")


def reset_index(base_url: str, index_name: str) -> None:
    requests.delete(f"{base_url}/{index_name}", timeout=30)
    resp = requests.put(
        f"{base_url}/{index_name}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(INDEX_MAPPING),
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"Failed to create index: {resp.status_code} {resp.text[:400]}")


def normalize_record(row: dict) -> dict:
    record_id = row.get("_id") or row.get("id") or row.get("url")
    text = row.get("text") or row.get("chunk") or ""
    vector = row.get("emb") or row.get("vector")
    if vector is None:
        raise ValueError("missing vector field")
    return {
        "id": str(record_id),
        "title": row.get("title", ""),
        "url": row.get("url", ""),
        "chunk": text,
        "vector": [float(x) for x in vector],
    }


def iter_dataset(dataset_name: str, config_name: str, split: str, max_docs: int):
    dataset = load_dataset(dataset_name, config_name, split=split, streaming=True)
    count = 0
    for row in dataset:
        yield normalize_record(row)
        count += 1
        if count >= max_docs:
            break


def bulk_lines(index_name: str, docs: list[dict]) -> str:
    lines = []
    for doc in docs:
        lines.append(json.dumps({"index": {"_index": index_name, "_id": doc["id"]}}, ensure_ascii=False))
        lines.append(json.dumps(doc, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def bulk_ingest(base_url: str, index_name: str, docs_iter, bulk_size: int):
    total = 0
    batch = []
    examples = []
    started = time.time()
    for doc in docs_iter:
        batch.append(doc)
        if len(examples) < 3:
            examples.append(doc)
        if len(batch) >= bulk_size:
            send_bulk(base_url, index_name, batch)
            total += len(batch)
            print(f"Indexed {total} docs...")
            batch = []
    if batch:
        send_bulk(base_url, index_name, batch)
        total += len(batch)
        print(f"Indexed {total} docs...")
    elapsed = time.time() - started
    docs_per_min = total / elapsed * 60 if elapsed > 0 else 0.0
    return total, docs_per_min, examples


def send_bulk(base_url: str, index_name: str, batch: list[dict]) -> None:
    payload = bulk_lines(index_name, batch)
    resp = requests.post(
        f"{base_url}/_bulk",
        headers={"Content-Type": "application/x-ndjson"},
        data=payload.encode("utf-8"),
        timeout=120,
    )
    if not resp.ok:
        raise RuntimeError(f"_bulk failed: {resp.status_code} {resp.text[:400]}")
    body = resp.json()
    if body.get("errors"):
        raise RuntimeError(f"_bulk returned errors: {json.dumps(body)[:400]}")


def natural_language_query(doc: dict) -> str:
    title = doc.get("title", "").strip()
    chunk = (doc.get("chunk") or "").strip()
    if title:
        return f"{title}とはどのような内容ですか。"
    if chunk:
        head = chunk.split("。", 1)[0].strip()
        return f"{head}について教えてください。"
    return "この文書の内容を教えてください。"


def embed_query_with_bedrock(query_text: str, model_id: str, region: str) -> list[float]:
    client = boto3.client("bedrock-runtime", region_name=region)
    body = json.dumps({"input_type": "search_query", "texts": [query_text]})
    response = client.invoke_model(modelId=model_id, body=body)
    payload = json.loads(response["body"].read())
    return [float(x) for x in payload["embeddings"][0]]


def fallback_query_vector(query_text: str, examples: list[dict]) -> list[float]:
    tokens = set(query_text.replace("？", "").replace("。", "").split())
    best_doc = examples[0]
    best_score = -1
    for doc in examples:
        hay = f"{doc.get('title', '')} {doc.get('chunk', '')}"
        score = sum(1 for token in tokens if token and token in hay)
        if score > best_score:
            best_doc = doc
            best_score = score
    return best_doc["vector"]


def build_example_query(doc: dict, embedding_mode: str, model_id: str, region: str) -> tuple[str, dict]:
    query_text = natural_language_query(doc)
    if embedding_mode == "bedrock":
        vector = embed_query_with_bedrock(query_text, model_id, region)
    else:
        vector = doc["vector"]
    query = {
        "size": 5,
        "_source": ["id", "title", "url", "chunk"],
        "query": {"knn": {"vector": {"vector": vector, "k": 5}}},
    }
    return query_text, query


def build_fixed_query(query_text: str, examples: list[dict], embedding_mode: str, model_id: str, region: str) -> dict:
    if embedding_mode == "bedrock":
        vector = embed_query_with_bedrock(query_text, model_id, region)
    else:
        vector = fallback_query_vector(query_text, examples)
    return {
        "size": 5,
        "_source": ["id", "title", "url", "chunk"],
        "query": {"knn": {"vector": {"vector": vector, "k": 5}}},
    }


def write_examples(
    path_md: Path,
    path_json: Path,
    index_name: str,
    examples: list[dict],
    embedding_mode: str,
    model_id: str,
    region: str,
) -> None:
    path_md.parent.mkdir(parents=True, exist_ok=True)
    payload = []
    lines = [
        "# Dev Tools query examples",
        "",
        "OpenSearch Dashboards の Dev Tools で、次のクエリをそのまま試せます。",
        "",
        f"- Index: `{index_name}`",
        f"- Query embedding mode: `{embedding_mode}`",
        "",
    ]
    lines.extend(
        [
            "## Fixed natural-language examples",
            "",
            "次の質問は、ハンズオンでそのまま試しやすい固定例です。",
            "",
        ]
    )
    for query_text in FIXED_NATURAL_LANGUAGE_QUERIES:
        query = build_fixed_query(query_text, examples, embedding_mode, model_id, region)
        payload.append(
            {
                "type": "fixed",
                "query_text": query_text,
                "query": query,
            }
        )
        lines.extend(
            [
                f"### {query_text}",
                "",
                "```json",
                f"GET {index_name}/_search",
                json.dumps(query, ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    for i, doc in enumerate(examples, start=1):
        query_text, query = build_example_query(doc, embedding_mode, model_id, region)
        payload.append(
            {
                "type": "derived",
                "title": doc["title"],
                "id": doc["id"],
                "url": doc["url"],
                "query_text": query_text,
                "query": query,
            }
        )
        lines.extend(
            [
                f"## Example {i}: {doc['title'][:80]}",
                "",
                f"自然文クエリ例: `{query_text}`",
                "",
                "```json",
                f"GET {index_name}/_search",
                json.dumps(query, ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    path_md.write_text("\n".join(lines), encoding="utf-8")
    path_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def refresh_index(base_url: str, index_name: str) -> None:
    resp = requests.post(f"{base_url}/{index_name}/_refresh", timeout=60)
    if not resp.ok:
        raise RuntimeError(f"refresh failed: {resp.status_code} {resp.text[:400]}")


def main() -> None:
    base_url = os.environ["OPENSEARCH_URL"].rstrip("/")
    index_name = os.environ.get("OPENSEARCH_INDEX", "wiki-ja-demo")
    dataset_name = os.environ.get("HF_DATASET", "Cohere/wikipedia-2023-11-embed-multilingual-v3")
    config_name = os.environ.get("HF_CONFIG", "ja")
    split = os.environ.get("HF_SPLIT", "train")
    max_docs = int(os.environ.get("MAX_DOCS", "10000"))
    bulk_size = int(os.environ.get("BULK_SIZE", "200"))
    examples_path = Path(os.environ.get("EXAMPLES_PATH", "/app/generated/example_queries.md"))
    examples_json_path = Path(os.environ.get("EXAMPLES_JSON_PATH", "/app/generated/example_queries.json"))
    embedding_mode = os.environ.get("SAMPLE_QUERY_EMBEDDING_MODE", "heuristic")
    bedrock_model_id = os.environ.get("BEDROCK_EMBED_MODEL_ID", "cohere.embed-multilingual-v3")
    bedrock_region = os.environ.get("BEDROCK_EMBED_REGION", "us-east-1")

    print("Waiting for OpenSearch ...")
    wait_for_opensearch(base_url)
    print(f"Creating index {index_name} ...")
    reset_index(base_url, index_name)
    print(f"Loading {dataset_name} ({config_name}, {split}) and indexing {max_docs} docs ...")
    total, docs_per_min, examples = bulk_ingest(
        base_url,
        index_name,
        iter_dataset(dataset_name, config_name, split, max_docs),
        bulk_size,
    )
    refresh_index(base_url, index_name)
    write_examples(
        examples_path,
        examples_json_path,
        index_name,
        examples,
        embedding_mode,
        bedrock_model_id,
        bedrock_region,
    )
    print("")
    print("Completed.")
    print(f"Indexed docs: {total}")
    print(f"Approx docs/min: {docs_per_min:.1f}")
    print(f"Dashboards: http://localhost:5601")
    print(f"OpenSearch: http://localhost:9200")
    print(f"Example queries: {examples_path}")
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
