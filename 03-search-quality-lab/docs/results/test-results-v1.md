# test split evaluation

- Executed: 2026-07-27T00:06:07+09:00
- Documents: 180
- Candidate size: 10
- Hybrid weights: [0.5, 0.5]

## Quality by category

| Category | Mode | Queries | Hit@3 | Hit@10 | MRR@5 | NDCG@5 | Context | Constraint | Violations |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| constraint | `exact` | 1 | 1.000 | 1.000 | 1.000 | 1.000 | - | 1.000 | 0 |
| constraint | `hybrid_filter` | 1 | 1.000 | 1.000 | 1.000 | 0.834 | - | 1.000 | 0 |
| context | `hybrid` | 3 | 1.000 | 1.000 | 1.000 | 0.737 | 0.778 | - | 0 |
| context | `hybrid_context` | 3 | 1.000 | 1.000 | 1.000 | 0.369 | 1.000 | - | 0 |
| lexical | `fulltext` | 5 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | 0 |
| lexical | `hybrid` | 5 | 1.000 | 1.000 | 0.800 | 0.852 | - | - | 0 |
| lexical | `vector` | 5 | 0.200 | 0.400 | 0.250 | 0.286 | - | - | 0 |
| mixed | `fulltext` | 5 | 0.800 | 1.000 | 0.800 | 0.800 | - | - | 0 |
| mixed | `hybrid` | 5 | 1.000 | 1.000 | 0.900 | 0.926 | - | - | 0 |
| mixed | `vector` | 5 | 0.800 | 0.800 | 0.567 | 0.626 | - | - | 0 |
| negation_exception | `hybrid` | 5 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | 0 |
| negation_exception | `hybrid_rerank` | 5 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | 0 |
| semantic | `fulltext` | 5 | 0.600 | 1.000 | 0.550 | 0.612 | - | - | 0 |
| semantic | `hybrid` | 5 | 1.000 | 1.000 | 0.900 | 0.926 | - | - | 0 |
| semantic | `vector` | 5 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | 0 |

## Latency

| Mode | Runs | p50 total | p95 total | p50 search | p50 rerank |
|---|---:|---:|---:|---:|---:|
| `vector` | 5 | 212 ms | 213 ms | 6 ms | 0 ms |
| `fulltext` | 5 | 5 ms | 5 ms | 5 ms | 0 ms |
| `hybrid` | 5 | 217 ms | 222 ms | 10 ms | 0 ms |
| `hybrid_rerank` | 5 | 2714 ms | 2783 ms | 12 ms | 2487 ms |
| `hybrid_context` | 5 | 228 ms | 230 ms | 11 ms | 0 ms |
| `exact` | 5 | 2 ms | 2 ms | 2 ms | 0 ms |
| `hybrid_filter` | 5 | 205 ms | 229 ms | 8 ms | 0 ms |
