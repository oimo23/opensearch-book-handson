import json
from pathlib import Path

import boto3
import requests
import streamlit as st
import os


DEFAULT_MODEL_ID = os.environ.get("BEDROCK_EMBED_MODEL_ID", "cohere.embed-multilingual-v3")
DEFAULT_REGION = os.environ.get("BEDROCK_EMBED_REGION", "us-east-1")
DEFAULT_OPENSEARCH_URL = os.environ.get("OPENSEARCH_URL", "http://localhost:9200")
DEFAULT_INDEX = os.environ.get("OPENSEARCH_INDEX", "wiki-ja-demo")


def has_default_profile() -> bool:
    for filename in ("config", "credentials"):
        path = Path("/root/.aws") / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "[default]" in text or "[profile default]" in text:
            return True
    return False


def bedrock_client(region: str):
    profile = os.environ.get("AWS_PROFILE", "").strip()
    if not profile:
        os.environ.pop("AWS_PROFILE", None)
        os.environ.pop("AWS_DEFAULT_PROFILE", None)
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    elif has_default_profile():
        session = boto3.Session(profile_name="default", region_name=region)
    else:
        session = boto3.Session(region_name=region)
    return session.client("bedrock-runtime", region_name=region)


def embed_query(query_text: str, model_id: str, region: str) -> list[float]:
    client = bedrock_client(region)
    body = json.dumps({"input_type": "search_query", "texts": [query_text]})
    response = client.invoke_model(modelId=model_id, body=body)
    payload = json.loads(response["body"].read())
    return [float(x) for x in payload["embeddings"][0]]


def search_opensearch(base_url: str, index_name: str, vector: list[float]) -> dict:
    query = {
        "size": 5,
        "_source": ["id", "title", "url", "chunk"],
        "query": {"knn": {"vector": {"vector": vector, "k": 5}}},
    }
    response = requests.post(
        f"{base_url.rstrip('/')}/{index_name}/_search",
        headers={"Content-Type": "application/json"},
        data=json.dumps(query).encode("utf-8"),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="Local Vector Search Demo", layout="wide")
st.title("ローカルベクトル検索デモ")
st.write(
    "自然文を Bedrock で埋め込みに変換し、そのベクトルを使ってローカルの OpenSearch を検索します。"
)

with st.sidebar:
    st.header("接続設定")
    model_id = st.text_input("Bedrock model ID", value=DEFAULT_MODEL_ID)
    region = st.text_input("Bedrock region", value=DEFAULT_REGION)
    opensearch_url = st.text_input("OpenSearch URL", value=DEFAULT_OPENSEARCH_URL)
    index_name = st.text_input("Index name", value=DEFAULT_INDEX)
    st.caption("AWS 認証は `AWS_PROFILE` や `aws sso login` 済みの状態を前提にしています。")

default_query = "がんの研究で有名な科学者を知りたいです。"
query_text = st.text_area("自然文クエリ", value=default_query, height=100)

if "query_vector" not in st.session_state:
    st.session_state.query_vector = None
if "search_result" not in st.session_state:
    st.session_state.search_result = None
if "last_query_text" not in st.session_state:
    st.session_state.last_query_text = ""

col1, col2 = st.columns(2)

with col1:
    if st.button("1. ベクトルを取得", use_container_width=True):
        if not query_text.strip():
            st.warning("自然文クエリを入力してください。")
        else:
            with st.spinner("Bedrock で埋め込みを取得しています..."):
                try:
                    vector = embed_query(query_text.strip(), model_id, region)
                except Exception as exc:
                    st.session_state.query_vector = None
                    st.error(f"埋め込み取得に失敗しました: {exc}")
                else:
                    st.session_state.query_vector = vector
                    st.session_state.last_query_text = query_text.strip()
                    st.session_state.search_result = None
                    st.success("埋め込みを取得しました。")

with col2:
    if st.button("2. 検索する", use_container_width=True):
        vector = st.session_state.query_vector
        if vector is None:
            st.warning("先に「ベクトルを取得」を実行してください。")
        else:
            with st.spinner("OpenSearch を検索しています..."):
                try:
                    st.session_state.search_result = search_opensearch(
                        opensearch_url,
                        index_name,
                        vector,
                    )
                except Exception as exc:
                    st.session_state.search_result = None
                    st.error(f"検索に失敗しました: {exc}")
                else:
                    st.success("検索結果を取得しました。")

vector = st.session_state.query_vector
if vector is not None:
    st.subheader("取得したベクトル")
    st.write(f"クエリ: `{st.session_state.last_query_text}`")
    st.write(f"次元数: `{len(vector)}`")
    st.caption("表示しているのは先頭 16 次元のプレビューです。")
    st.code(json.dumps(vector[:16], ensure_ascii=False, indent=2), language="json")
    if st.checkbox("1024次元すべてを表示する"):
        st.code(json.dumps(vector, ensure_ascii=False, indent=2), language="json")

result = st.session_state.search_result
if result is not None:
    st.subheader("検索結果")
    hits = result.get("hits", {}).get("hits", [])
    if not hits:
        st.info("ヒットがありませんでした。")
    for i, hit in enumerate(hits, start=1):
        source = hit.get("_source", {})
        title = source.get("title") or "(no title)"
        score = hit.get("_score")
        with st.expander(f"{i}. {title} | score={score:.4f}" if isinstance(score, (int, float)) else f"{i}. {title}"):
            if source.get("url"):
                st.markdown(f"[URL]({source['url']})")
            st.write(source.get("chunk", ""))
            st.caption(f"id: {source.get('id', '')}")
