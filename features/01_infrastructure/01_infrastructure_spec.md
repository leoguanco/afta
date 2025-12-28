# ✨ Feature Specification: Infrastructure & Deployment

## 1. 🚀 Overview & Motivation

- **Feature Name:** Infrastructure & Deployment (Async Multi-Worker Stack)
- **Goal:** Establish a containerized, observable environment that supports multiple specialized asynchronous workers, utilizing **Hexagonal Architecture** and **Domain-Driven Design**.
- **Problem Solved (The "Why"):** The system requires heavy GPU dependencies (CUDA for YOLO), specialized databases (PostGIS/pgvector), and coordinated services (Python API + Next.js UI). A manual setup is brittle. We need a Distributed Task Queue to manage GPU-heavy vision tasks separately from CPU-heavy math tasks.
- **Scope:**
  - **In Scope:** Docker configurations, Hexagonal Project Structure, TDD Enforcement, Observability Stack, Distributed Task Queue (Celery/Redis).
  - **Out of Scope:** Cloud provisioning.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Developer**, I want **Hexagonal Architecture**, so that **my domain logic is isolated.**

| Criteria ID | Acceptance Criteria                                                                                | Status |
| :---------- | :------------------------------------------------------------------------------------------------- | :----- |
| US1.1       | The project structure SHALL clearly separate `domain`, `application`, and `infrastructure` layers. | [x]    |
| US1.2       | The `domain` layer SHALL NOT depend on any external libraries (Framework Agnostic).                | [x]    |

### **User Story 2:** As a **System**, I want **Specialized Workers (GPU/CPU)**, so that **I can scale efficiently.**

| Criteria ID | Acceptance Criteria                                                                      | Status |
| :---------- | :--------------------------------------------------------------------------------------- | :----- |
| US2.1       | The stack SHALL include a `vision-worker` container with **NVIDIA CUDA Runtime** access. | [x]    |
| US2.2       | The stack SHALL include a `general-worker` container for CPU tasks (Ingestion, Metrics). | [x]    |
| US2.3       | Celery SHALL route vision tasks to the `gpu_queue`.                                      | [x]    |

### **User Story 3:** As a **DevOps Engineer**, I want **Observability**, so that **I can debug issues.**

| Criteria ID | Acceptance Criteria                                                                         | Status |
| :---------- | :------------------------------------------------------------------------------------------ | :----- |
| US3.1       | The system SHALL expose **Prometheus** metrics at `/metrics`.                               | [x]    |
| US3.2       | The system SHALL log in **JSON format** only when errors occur, containing correlation IDs. | [ ]    |
| US3.3       | **Grafana** SHALL be pre-configured with a dashboard showing system health.                 | [x]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Polyglot + Distributed Async)**

- **Architecture Pattern:** **Hexagonal (Ports & Adapters)**
  - `src/domain/`, `src/application/`, `src/infrastructure/`.
- **Components:**
  - **Backend:** Python (FastAPI).
  - **Frontend:** Next.js (TypeScript).
  - **Database:** PostgreSQL (with **PostGIS** and **pgvector** extensions).
  - **Broker:** Redis.
  - **Storage:** MinIO (S3 Compatible).
- **New Dependencies:**
  - `nvidia-container-toolkit`: Host requirement.
  - `prometheus-client`: For Python metrics.
  - `pytest`: For TDD.

### **3.2 Implementation Steps**

1.  **Project Skeleton:** Scaffold the Hexagonal directory structure.
2.  **Docker Compose:** Define services for API, Frontend, Postgres, Redis, MinIO, GPU Worker, and CPU Worker.
3.  **Config:** Setup `nvidia-container-toolkit` for the vision worker.
4.  **Observability:** Implement central Logger and Metrics middleware.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Language:** Python (Backend), TypeScript (Frontend).
  - **Methodology:** **TDD (Test First)** is mandatory.
  - **GPU Drivers:** Host must have NVIDIA drivers installed (CUDA 11.8+).
- **Edge Cases:**
  - **No GPU:** If no GPU is found, the `vision-worker` should log a warning and potentially fail dense tracking tasks (or fall back to slow CPU mode).

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** TDD loop (Red-Green-Refactor).
- **Key Test Scenarios:**
  - **Scenario 1:** `docker-compose up` launches all 7 containers (API, Web, DB, Redis, MinIO, Worker-GPU, Worker-CPU).
  - **Scenario 2:** Run `nvidia-smi` inside `vision-worker` to verify GPU access.
  - **Scenario 3:** Verify that a Vision task is _never_ picked up by a CPU-only worker.

---

## 6. 🔗 References and Related Documentation

- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- [Hexagonal Architecture in Python](https://eng.lyft.com/python-at-lyft-large-scale-systems-4f28525287a3)
