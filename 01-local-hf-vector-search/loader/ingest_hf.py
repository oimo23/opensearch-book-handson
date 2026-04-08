import json
import os
import time
import sys

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
    print("Waiting for OpenSearch ...")
    wait_for_opensearch(base_url)
    print(f"Creating index {index_name} ...")
    reset_index(base_url, index_name)
    print(f"Loading {dataset_name} ({config_name}, {split}) and indexing {max_docs} docs ...")
    total, docs_per_min, _examples = bulk_ingest(
        base_url,
        index_name,
        iter_dataset(dataset_name, config_name, split, max_docs),
        bulk_size,
    )
    refresh_index(base_url, index_name)
    print("")
    print("Completed.")
    print(f"Indexed docs: {total}")
    print(f"Approx docs/min: {docs_per_min:.1f}")
    print(f"Dashboards: http://localhost:5601")
    print(f"OpenSearch: http://localhost:9200")
    print("Example queries: ./generated/example_queries.md")
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
