# 🏗️ Architecture Specification: Application Layer Design

> **Context:** This spec defines the patterns and rules for the **Application Layer** within the project's Hexagonal Architecture. It supplements the [Infrastructure Spec](01_infrastructure_spec.md).

## 1. 🎯 Overview & Motivation

- **Goal:** enforce a strict, consistent structure for business logic orchestration.
- **Problem Solved:** Prevents business logic leakage into Infrastructure (API/Tasks) and avoids "god classes" or ambiguous Services.
- **Principle:** "Handlers Orchestrate, Use Cases Execute."

---

## 2. 📏 Design Rules

### **Rule 1: Use Case Structure**

- **Single Responsibility:** Each Use Case class handles exactly **one** specific business action.
- **Naming Convention:** `Feature + Action + er` (Action-oriented naming).
  - ✅ `TrackingFinder`
  - ✅ `PhaseClassifier`
  - ✅ `ReportGenerator`
  - ❌ `TrackingService` (Too generic)
  - ❌ `PhaseManager` (Ambiguous)
- **Single Public Method:** Expose **only one** public method to trigger the action.
  - Preferred: `.execute(...)`
  - Alternatives: `.run(...)`, `.handle(...)`, `__call__(...)`

### **Rule 2: Dependency Injection**

- **Inversion of Control:** Use Cases must never instantiate dependencies directly.
- **Domain Ports:** Constructor arguments must be type-hinted with **Domain Ports** (Interfaces/ABCs), not concrete Infrastructure classes.
  - ✅ `def __init__(self, repo: PhaseRepository)`
  - ❌ `def __init__(self, repo: PostgresPhaseRepository)`

### **Rule 3: Anemic Handlers**

- **Role of Adapters:** API Routes (FastAPI) and Workers (Celery) are **Infrastructure Adapters**.
- **No Logic:** They must contain **zero** business logic. Their only job is:
  1.  **Parse/Validate Input** (DTOs).
  2.  **Compose Dependencies** (Instantiate concrete adapters).
  3.  **Instantiate Use Case** (Injecting adapters).
  4.  **Execute Use Case**.
  5.  **Format Output** (HTTP Response / Task Result).

---

## 3. 📝 Example Pattern

### **The Use Case (Application Layer)**

```python
class PhaseClassifier:
    def __init__(self, ml_engine: PhaseClassifierPort, storage: PhaseRepository):
        self.ml_engine = ml_engine
        self.storage = storage

    def execute(self, match_id: str) -> PhaseSequence:
        # 1. Orchestrate Logic
        data = self.storage.get_data(match_id)
        # 2. Use Domain Logic
        result = self.ml_engine.classify(data)
        # 3. Side Effects
        self.storage.save(result)
        return result
```

### **The Handler (Infrastructure Layer)**

```python
@shared_task
def classify_task(match_id: str):
    # 1. Composition Root (Wire up dependencies)
    ml_adapter = SklearnPhaseClassifier()
    db_adapter = PostgresPhaseRepository()

    # 2. Instantiate Use Case
    use_case = PhaseClassifier(ml_adapter, db_adapter)

    # 3. Execute
    return use_case.execute(match_id)
```
