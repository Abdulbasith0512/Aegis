# AegisAI: AI Governance Operating System for Banking

AegisAI is an enterprise-grade AI Governance Operating System designed to supervise, monitor, stress-test, explain, and audit autonomous AI agents operating in banking environments. It ensures transparency, resilience, compliance, and trust in financial workflows.

---

## Key Modules

* **AI Orchestrator**: Manages execution state and runs coordinate workflows across banking agents.
* **Domain Agents**:
  * **Fraud Agent**: Screens transactions for high-risk fraud metrics.
  * **AML Agent**: Monitors transactional flow to identify structuring and money laundering patterns.
  * **KYC Agent**: Processes identities, verify registries, and matches documents.
  * **Device Agent**: Evaluates network profiles, emulators, IP reputations, and device footprints.
  * **Behavior Agent**: Identifies deviations from historical user engagement.
  * **Compliance Agent**: Ensures checks align with banking laws (e.g., Fair Lending, KYC/AML laws).
* **Explainability Engine**: Translates complex AI verdicts into human-readable rationales using feature attributions.
* **Trust Score Engine**: Generates a unified, real-time safety index (0-100) before executions.
* **Policy Engine**: Enforces deterministic, regulatory policies over transactions and prompt inputs/outputs.
* **Chaos Engine**: Simulates failures, data drift, and network latency to stress-test system resilience.
* **Digital Twin**: Emulates a shadow core banking interface to safely execute agent loops.

---

## Directory Structure

```
AegisAI/
├── .agents/             # Agent guidelines & project configuration
├── agents/              # Orchestrators and domain agent implementations
├── backend/             # FastAPI API Gateway & Control Plane
├── configs/             # Configuration templates & YAML files
├── data/                # Database migrations & schemas
├── docs/                # Architecture, PRD, and API specifications
├── docker/              # Dockerfiles and orchestration files
├── frontend/            # Next.js App Router admin dashboard
├── ml/                  # ML models, classifiers, & explainability engines
├── monitoring/          # Prometheus & Grafana configurations
├── research/            # Jupyter notebooks, digital twin experiments, & papers
├── scripts/             # Setup and bootstrap shell scripts
└── tests/               # Unit, integration, & chaos testing suites
```

---

## Getting Started

### Prerequisites

* Node.js v18+
* Python 3.10+
* Docker & Docker Compose
* PostgreSQL / Neo4j / Qdrant / Redis (if running locally without Docker)

### Run the Architecture Scaffolding

1. **Environment Variables Setup**:
   ```bash
   cp .env.example .env
   ```

2. **Docker Compose Infrastructure Setup**:
   ```bash
   docker-compose up -d
   ```

3. **Backend API Gateway Startup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

4. **Frontend Dashboard Startup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## Production Pipeline & ML Engine

AegisAI now has a fully integrated production-grade transaction governance pipeline:

1. **Transaction Interception (`POST /api/v1/transactions/intercept`)**:
   - Ingests telemetry including device fingerprints, location coords, beneficiary records, and metadata.
   - Runs validation using Pydantic schemas.
   - Coordinates dynamic execution across all sub-agents via the compiled LangGraph execution graph.
   - Saves all predictions, consensus votes, policies metrics, trust score calculations, human review queues, and explanations in the PostgreSQL relational tier.

2. **Concrete Machine Learning Integration (`ml/models.py`)**:
   - **Fraud Agent**: Leverages Scikit-Learn `RandomForestClassifier` and `GradientBoostingClassifier` trained dynamically at startup on synthetic parameters.
   - **Behavior Agent**: Leverages scikit-learn `IsolationForest` to analyze data drifts.
   - **AML Agent**: Reconstructs active transfer networks using `NetworkX` graph nodes, identifying structuring thresholds and cycle/smurfing routing loops.
   - **KYC Agent**: Assesses identity verification logs.

3. **Semantic Vector Storage**:
   - Implements semantic indices inside **Qdrant** with unit-normalized deterministic text hash embeddings.
   - Backed by an in-memory document store fallback layer to ensure runtime isolation if the Qdrant server is offline.

---

## AI Research Lab & Governance Intelligence

The **AI Research Lab** allows researchers and administrators to simulate, benchmark, and review model performance:

- **Governance Score Engine**: Computes a dynamic rating (0-100) and maps a grade (A-F) based on trust compliance, agent health, security score, recovery score, and reviews frequency.
- **Agent Reputation Engine**: Computes a dynamic performance-based reputation leaderboard rank for all AI agents.
- **Governance Maturity Index**: Audits the maturity level (Initial, Managed, Defined, Quantitatively Managed, Optimized) across 9 strategic dimensions.
- **AI Failure Index**: Tracks metrics of system anomalies, model drifts, consensus errors, and logs root cause diagnoses.
- **Dynamic Consensus V2**: Upgrades voting by weighting decisions based on active reputations and confidence matrices.
- **APIs**:
  - `POST /api/v1/research/experiment` / `GET /api/v1/research/experiments`: CRUD for scenarios.
  - `POST /api/v1/research/run` / `GET /api/v1/research/results`: Triggers and gets simulation outcomes.
  - `GET /api/v1/research/governance-score`: Overall score.
  - `GET /api/v1/research/reputation`: Rankings leaderboard.
  - `GET /api/v1/research/maturity`: Maturity assessment.
  - `GET /api/v1/research/failure-index`: Failure index analysis.
  - `GET /api/v1/research/benchmarks` / `POST /api/v1/research/compare`: Comparative performance matrix calculations.
  - `GET /api/v1/research/download/csv`: Export statistics report.

---


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

