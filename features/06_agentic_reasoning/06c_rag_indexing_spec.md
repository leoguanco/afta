# ✨ Feature Specification: RAG Indexing & Retrieval

> **Context:** This spec is part of the [Football Intelligence Engine](../../feature_specs.md) project. For infrastructure constraints (TDD, Hexagonal Architecture, Async Workers), see [../01_infrastructure/01_infrastructure_spec.md](../01_infrastructure/01_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** RAG (Retrieval-Augmented Generation) Indexing
- **Goal:** Index match data (events, metrics, summaries) into a vector store to provide contextual retrieval for AI-powered analysis.
- **Problem Solved (The "Why"):** LLMs have limited context windows and no memory of match-specific data. By indexing match information into a vector database, we enable the AI to retrieve relevant context before generating analysis, resulting in more accurate and data-grounded responses.
- **Scope:**
  - **In Scope:** Vector store port, ChromaDB adapter, match data indexer use case, embedding generation.
  - **Out of Scope:** Real-time incremental updates, multi-tenant isolation.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As an **AI System**, I want **match data indexed for retrieval**, so that **I can provide context-aware analysis.**

| Criteria ID | Acceptance Criteria                                                          | Status |
| :---------- | :--------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL index match events (goals, shots, cards) into vector store. | [x]    |
| US1.2       | The system SHALL index calculated metrics (PPDA, xT, possession) as text.    | [x]    |
| US1.3       | The system SHALL support semantic similarity search on indexed data.         | [x]    |

### **User Story 2:** As a **Developer**, I want **a pluggable vector store**, so that **I can swap implementations.**

| Criteria ID | Acceptance Criteria                                                        | Status |
| :---------- | :------------------------------------------------------------------------- | :----- |
| US2.1       | The system SHALL define a `VectorStorePort` interface in the domain layer. | [x]    |
| US2.2       | The system SHALL provide a ChromaDB implementation as the default adapter. | [x]    |
| US2.3       | The system SHALL use local embeddings (no external API calls for privacy). | [x]    |

### **User Story 3:** As an **Analyst**, I want **AI responses grounded in match data**, so that **analysis is accurate.**

| Criteria ID | Acceptance Criteria                                                            | Status |
| :---------- | :----------------------------------------------------------------------------- | :----- |
| US3.1       | The AI analysis flow SHALL query the vector store before generating responses. | [x]    |
| US3.2       | Retrieved context SHALL be injected into the LLM prompt.                       | [x]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hexagonal)**

- **Domain Layer:**
  - `src/domain/ports/vector_store_port.py`: Abstract interface defining `add_documents`, `query`, `delete_by_metadata`, `get_collection_stats`.
  - `src/domain/ports/vector_store_port.SearchResult`: Value object for query results.
- **Infrastructure Layer:**
  - `src/infrastructure/storage/chroma_adapter.py`: ChromaDB implementation using SentenceTransformers for local embeddings.
- **Application Layer:**
  - `src/application/use_cases/match_data_indexer.py`: Orchestrates indexing of events, metrics, and summaries.
  - `src/application/services/match_context_service.py`: Retrieves and formats context for AI analysis.

### **3.2 Implementation Steps**

1.  **Define Port:** Create `VectorStorePort` with CRUD operations for documents.
2.  **Implement Adapter:** Create `ChromaDBAdapter` using `chromadb` and `sentence-transformers`.
3.  **Create Use Case:** `MatchDataIndexer` to format and index match data.
4.  **Integrate with AI:** Modify `CrewAIAdapter` / `MatchContextService` to query vector store before LLM calls.

### **3.3 Key Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────────┐    ┌─────────────────────────────┐    │
│  │ MatchDataIndexer │    │ MatchContextService         │    │
│  │ (Index Data)     │    │ (Retrieve Context for AI)   │    │
│  └────────┬─────────┘    └──────────────┬──────────────┘    │
│           │                             │                    │
│           └───────────┬─────────────────┘                    │
│                       ▼                                      │
│              ┌────────────────┐                              │
│              │ VectorStorePort│ (Domain Interface)           │
│              └────────┬───────┘                              │
└───────────────────────┼──────────────────────────────────────┘
                        │
┌───────────────────────┼──────────────────────────────────────┐
│                       ▼              Infrastructure Layer    │
│              ┌────────────────┐                              │
│              │ ChromaDBAdapter│                              │
│              └────────┬───────┘                              │
│                       │                                      │
│   ┌───────────────────┼───────────────────┐                  │
│   ▼                   ▼                   ▼                  │
│ ChromaDB         SentenceTransformers   Local Storage        │
│ (Vector DB)      (Embeddings)           (./chroma_db)        │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Privacy:** Must use local embeddings (SentenceTransformers) to avoid sending match data to external APIs.
  - **Performance:** Indexing should complete in <5 seconds for a typical match (~100 events).
  - **Dependencies:** `chromadb`, `sentence-transformers` must be in worker requirements.
- **Assumptions:**
  - Embedding model `all-MiniLM-L6-v2` provides sufficient quality for tactical text similarity.
  - Matches are indexed after ingestion/metrics calculation is complete.
- **Edge Cases:**
  - **Empty Match:** If no events/metrics, indexer returns `status: "no_documents"`.
  - **Re-indexing:** Delete existing documents by `match_id` before re-indexing.
  - **ChromaDB Unavailable:** Graceful fallback to in-memory storage with warning.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Unit tests for formatting, integration tests for ChromaDB operations.
- **Key Test Scenarios:**
  - **Scenario 1:** Index 10 events → verify `documents_indexed == 10`.
  - **Scenario 2:** Query "pressing intensity" → verify PPDA-related documents are returned.
  - **Scenario 3:** Delete by match_id → verify collection count decreases.

---

## 6. 🔗 References and Related Documentation

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [SentenceTransformers](https://www.sbert.net/)
- [RAG Pattern (LangChain)](https://python.langchain.com/docs/use_cases/question_answering/)
