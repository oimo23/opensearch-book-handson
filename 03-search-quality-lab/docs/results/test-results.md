# test split evaluation

- Executed: 2026-08-23T17:10:03+09:00
- Documents: 180
- Evaluation version: v3
- Candidate size: 10
- Hybrid weights: [0.6, 0.4]

## Quality by category

| Category | Mode | Queries | Hit@3 | Hit@10 | MRR@5 | NDCG@5 | Parent@3 | Context | Context precision | Constraint | Violations |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constraint | `exact` | 3 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | 1.000 | 0 |
| constraint | `hybrid_filter` | 2 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | 1.000 | 0 |
| context | `hybrid` | 5 | 1.000 | 1.000 | 1.000 | 0.764 | 1.000 | 0.800 | - | - | 0 |
| context | `hybrid_context` | 5 | 1.000 | 1.000 | 1.000 | 0.418 | 1.000 | 1.000 | 0.350 | - | 0 |
| lexical | `fulltext` | 10 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | - | 0 |
| lexical | `hybrid` | 10 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | - | 0 |
| lexical | `vector` | 10 | 0.100 | 0.400 | 0.145 | 0.182 | - | - | - | - | 0 |
| mixed | `fulltext` | 10 | 0.900 | 1.000 | 0.900 | 0.900 | - | - | - | - | 0 |
| mixed | `hybrid` | 10 | 1.000 | 1.000 | 0.933 | 0.950 | - | - | - | - | 0 |
| mixed | `vector` | 10 | 0.900 | 0.900 | 0.733 | 0.776 | - | - | - | - | 0 |
| negation_exception | `hybrid` | 10 | 1.000 | 1.000 | 0.933 | 0.950 | - | - | - | - | 0 |
| negation_exception | `hybrid_rerank` | 10 | 0.900 | 1.000 | 0.900 | 0.900 | - | - | - | - | 0 |
| semantic | `fulltext` | 10 | 0.800 | 1.000 | 0.775 | 0.806 | - | - | - | - | 0 |
| semantic | `hybrid` | 10 | 1.000 | 1.000 | 0.883 | 0.913 | - | - | - | - | 0 |
| semantic | `vector` | 10 | 0.900 | 0.900 | 0.900 | 0.900 | - | - | - | - | 0 |
