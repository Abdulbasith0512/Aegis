# System Transaction Flow & Pipelines

This document details the operational pipelines and transaction execution flows governing AI agents inside AegisAI.

---

## 1. Governance Processing Pipeline

Below is the step-by-step transaction flow executing inside the AI Orchestrator:

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Bank Customer
    participant GW as API Gateway
    participant ORC as AI Orchestrator
    participant Context as Context Collectors (Device, Behavior, KYC)
    participant Core as Core Evaluators (Fraud, AML)
    participant Gov as Governance Layer (Trust, Policy, XAI)
    participant HReview as Human Review Portal
    participant DB as Postgres/Neo4j/Qdrant

    Customer->>GW: Submit Transaction (Metadata)
    GW->>ORC: Intercept & Delegate Flow
    
    rect rgb(240, 248, 255)
        Note over ORC, Context: Step 1: Context Gathering (Parallel)
        par Context Gathering
            ORC->>Context: Call Device Intelligence Agent
            Context-->>ORC: Device Fingerprint & IP Assessment
        and
            ORC->>Context: Call Behavior Agent
            Context-->>ORC: Historical Variance Score
        and
            ORC->>Context: Call KYC Agent
            Context-->>ORC: Verification Match State
        end
    end

    rect rgb(255, 240, 245)
        Note over ORC, Core: Step 2: Risk Scoring
        ORC->>Core: Invoke Fraud & AML Agents (passing context profiles)
        Core-->>ORC: Return Risk Vectors & Graph Relationships
    end

    rect rgb(245, 255, 250)
        Note over ORC, Gov: Step 3: Governance & Analysis
        ORC->>Gov: Calculate Trust Score & Explain Verdict
        Gov-->>ORC: Trust Score & SHAP Feature Explanations
        ORC->>Gov: Evaluate Deterministic Policies
        Gov-->>ORC: Compliance Verdict (Clear / Alert)
    end

    alt Trust Score < Threshold OR Policy Alert Triggered
        Note over ORC, HReview: Step 4a: Human-in-the-Loop Escalation
        ORC->>DB: Write Pending Transaction & Explanation Audit
        ORC->>HReview: Push Alert via WebSocket
        HReview-->>ORC: Auditor Verdict (Approve/Decline)
    end

    Note over ORC, DB: Step 5: Execution & Archival
    ORC->>DB: Save Immutable Audit Log (Hash and Embedding)
    ORC-->>GW: Return Final Transaction Decision
    GW-->>Customer: Transaction Approved / Declined Status
```

---

## 2. Processing Pipeline Steps

### Step 1: Context Gathering (Parallel Phase)
The Orchestrator receives the transaction payload. It calls the **Device Agent**, **Behavior Agent**, and **KYC Agent** concurrently to evaluate the background environment of the request. Doing this in parallel reduces gateway latency.

### Step 2: Core Risk Scoring
Using the combined user identity, device posture, and historical context variables, the Orchestrator executes the **Fraud Agent** (statistical risk) and **AML Agent** (relationship graphing in Neo4j).

### Step 3: Governance & Safety Calculations
The raw outputs of the agents are analyzed by the control plane:
- The **Trust Score Engine** weighs the data drift, confidence metrics, and device health to calculate a dynamic score.
- The **Explainability Engine** triggers SHAP calculation to trace which input features (e.g. device IP, transfer speed, transfer amount) contributed to the risk output.
- The **Policy Engine** runs checks against regulatory rules.

### Step 4: Human-in-the-Loop (HITL) Intervention
If a transaction triggers a high-severity policy alert or has a Trust Score below the configured threshold, the transaction is marked as `pending` and written to PostgreSQL. A message is broadcasted via WebSockets to active review screens.

### Step 5: Archival
Once resolved (automatically or by an auditor), the final state is committed to PostgreSQL, and the explainability explanation is converted into vector embeddings and logged inside PostgreSQL/pgvector for subsequent audit searches.
