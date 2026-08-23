# test split evaluation

- Executed: 2026-08-24T01:14:04+09:00
- Documents: 180
- Evaluation version: v3
- Candidate size: 10
- Hybrid weights: [0.7, 0.3]

## Quality by category

| Category | Mode | Queries | Hit@3 | Hit@10 | MRR@5 | NDCG@5 | Parent@3 | Context | Context precision | Constraint | Violations |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constraint | `exact` | 2 | - | - | - | - | - | - | - | 1.000 | 0 |
| constraint | `hybrid_filter` | 3 | - | - | - | - | - | - | - | 1.000 | 0 |
| context | `hybrid` | 5 | 1.000 | 1.000 | 1.000 | 0.481 | 1.000 | 0.733 | - | - | 0 |
| context | `hybrid_context` | 5 | 1.000 | 1.000 | 1.000 | 0.271 | 1.000 | 1.000 | 0.617 | - | 0 |
| lexical | `fulltext` | 10 | 0.900 | 1.000 | 0.900 | 0.900 | - | - | - | - | 0 |
| lexical | `hybrid` | 10 | 0.900 | 0.900 | 0.850 | 0.863 | - | - | - | - | 0 |
| lexical | `vector` | 10 | 0.400 | 0.500 | 0.350 | 0.363 | - | - | - | - | 0 |
| mixed | `fulltext` | 10 | 0.900 | 1.000 | 0.783 | 0.813 | - | - | - | - | 0 |
| mixed | `hybrid` | 10 | 0.900 | 1.000 | 0.833 | 0.850 | - | - | - | - | 0 |
| mixed | `vector` | 10 | 0.800 | 0.900 | 0.633 | 0.676 | - | - | - | - | 0 |
| negation_exception | `hybrid` | 10 | 1.000 | 1.000 | 0.883 | 0.913 | - | - | - | - | 7 |
| negation_exception | `hybrid_rerank` | 10 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | - | 7 |
| semantic | `fulltext` | 10 | 0.500 | 1.000 | 0.383 | 0.413 | - | - | - | - | 0 |
| semantic | `hybrid` | 10 | 0.500 | 1.000 | 0.520 | 0.588 | - | - | - | - | 0 |
| semantic | `vector` | 10 | 0.800 | 1.000 | 0.750 | 0.763 | - | - | - | - | 0 |
