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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
