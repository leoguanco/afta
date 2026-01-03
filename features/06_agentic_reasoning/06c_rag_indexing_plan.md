# 📋 Implementation Plan: RAG Integration Completion

> **Spec Reference:** [06c_rag_indexing_spec.md](./06c_rag_indexing_spec.md)

## Goal

Complete the RAG (Retrieval-Augmented Generation) integration so that match data is indexed after processing and retrieved during AI analysis.

---

## Current State

| Component             | Status    | Notes                                  |
| --------------------- | --------- | -------------------------------------- |
| `VectorStorePort`     | ✅ Exists | Domain interface defined               |
| `ChromaDBAdapter`     | ✅ Exists | Infrastructure adapter implemented     |
| `MatchDataIndexer`    | ⚠️ Unused | Use case exists but never called       |
| `MatchContextService` | ❌ No RAG | Only uses DB queries, not vector store |

## Gaps to Address

1. **No Indexing Trigger**: `MatchDataIndexer` is never called after ingestion/metrics calculation.
2. **No RAG Retrieval**: `MatchContextService` doesn't query the vector store before building AI context.
3. **No API Endpoint**: No way to manually trigger indexing or check index status.

---

## Proposed Changes

### 1. Infrastructure Layer

#### [MODIFY] `../../backend/src/infrastructure/di/container.py`

Add methods to resolve RAG-related dependencies:

- `get_vector_store()` → `ChromaDBAdapter`
- `get_match_data_indexer()` → `MatchDataIndexer`

---

#### [MODIFY] `../../backend/src/infrastructure/worker/tasks/ingestion_tasks.py`

After successful ingestion, trigger indexing:

```python
# After match is saved
indexer = Container.get_match_data_indexer()
indexer.execute(match_id, match_events=[...])
```

---

#### [MODIFY] `../../backend/src/infrastructure/worker/tasks/metrics_tasks.py`

After metrics are calculated, index them:

```python
# After metrics are saved
indexer = Container.get_match_data_indexer()
indexer.execute(match_id, match_metrics={...})
```

---

### 2. Application Layer

#### [MODIFY] `../../backend/src/application/services/match_context_service.py`

Add RAG retrieval before returning context:

```python
def __init__(self, match_repo, metrics_repo, vector_store=None):
    self.vector_store = vector_store

def build_context(self, match_id, query=None):
    # Existing DB-based context...

    # RAG Enhancement
    if self.vector_store and query:
        results = self.vector_store.query(query, n_results=5,
            filter_metadata={"match_id": match_id})
        if results:
            context_lines.append("\nRelevant Context (RAG):")
            for r in results:
                context_lines.append(f"  - {r.content}")
```

---

### 3. API Layer (Optional)

#### [NEW] `../../backend/src/infrastructure/api/endpoints/indexing.py`

Add endpoints for manual indexing control:

- `POST /api/v1/index/{match_id}` - Trigger indexing for a match
- `GET /api/v1/index/stats` - Get vector store statistics

---

## Verification Plan

### Automated Tests

1. **Unit Test**: `MatchDataIndexer.execute()` with mock vector store
2. **Integration Test**: Index → Query → Verify retrieval
3. **E2E Test**: Ingest match → Verify documents in ChromaDB

### Manual Verification

```bash
# After running ingestion
curl -X POST http://localhost:8000/api/v1/ingest -d '{"match_id": "test"}'

# Check indexing stats
curl http://localhost:8000/api/v1/index/stats
# Expected: {"document_count": N, ...}

# Run AI analysis and verify RAG context appears in response
curl -X POST http://localhost:8000/api/v1/chat/analyze \
  -d '{"match_id": "test", "query": "pressing intensity"}'
```

---

## Implementation Order

| Step | Task                          | Files                                    |
| ---- | ----------------------------- | ---------------------------------------- |
| 1    | Update DI Container           | `container.py`                           |
| 2    | Integrate with Ingestion Task | `ingestion_tasks.py`                     |
| 3    | Integrate with Metrics Task   | `metrics_tasks.py`                       |
| 4    | Update MatchContextService    | `match_context_service.py`               |
| 5    | Add Indexing API              | `indexing.py`, `main.py`                 |
| 6    | Write Tests                   | `tests/integration/test_rag_indexing.py` |
