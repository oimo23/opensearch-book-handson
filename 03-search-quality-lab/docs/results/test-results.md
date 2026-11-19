# test split evaluation

- Executed: 2026-11-19T16:29:35+09:00
- Documents: 180
- Evaluation version: v5
- Candidate size: 10
- Hybrid weights: [0.7, 0.3]

## Quality by category

| Category | Mode | Queries | Hit@3 | Hit@10 | MRR@5 | NDCG@5 | Parent@3 | Context | Context precision | Constraint | Violations |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| constraint | `exact` | 2 | - | - | - | - | - | - | - | 1.000 | 0 |
| constraint | `hybrid` | 3 | - | - | - | - | - | - | - | 1.000 | 0 |
| context | `hybrid` | 5 | 1.000 | 1.000 | 1.000 | 0.481 | 1.000 | 0.800 | - | - | 0 |
| context | `hybrid_context` | 5 | 1.000 | 1.000 | 1.000 | 0.271 | 1.000 | 1.000 | 0.517 | - | 0 |
| lexical | `fulltext` | 10 | 0.900 | 1.000 | 0.900 | 0.900 | - | - | - | - | 0 |
| lexical | `hybrid` | 10 | 0.900 | 1.000 | 0.900 | 0.900 | - | - | - | - | 0 |
| lexical | `vector` | 10 | 0.500 | 0.700 | 0.428 | 0.495 | - | - | - | - | 0 |
| mixed | `fulltext` | 10 | 0.700 | 1.000 | 0.700 | 0.700 | - | - | - | - | 0 |
| mixed | `hybrid` | 10 | 0.700 | 1.000 | 0.720 | 0.739 | - | - | - | - | 0 |
| mixed | `vector` | 10 | 0.800 | 0.900 | 0.633 | 0.676 | - | - | - | - | 0 |
| negation_exception | `hybrid` | 10 | 1.000 | 1.000 | 0.883 | 0.913 | - | - | - | - | 6 |
| negation_exception | `hybrid_rerank` | 10 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | - | 6 |
| semantic | `fulltext` | 10 | 0.500 | 1.000 | 0.383 | 0.413 | - | - | - | - | 0 |
| semantic | `hybrid` | 10 | 0.500 | 1.000 | 0.545 | 0.631 | - | - | - | - | 0 |
| semantic | `vector` | 10 | 0.800 | 1.000 | 0.770 | 0.802 | - | - | - | - | 0 |
