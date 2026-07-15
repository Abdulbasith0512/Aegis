# Product Features & Algorithms Specification

This document details the functional features and mathematical calculations powering the AegisAI governance modules.

---

## 1. Real-Time Trust Score Calculation
The Trust Score Engine generates an inline reliability metric (0-100) before a transaction is approved. The score is computed as:

$$\text{Trust Score} = w_1 \cdot C_{\text{model}} + w_2 \cdot (100 - D_{\text{data}}) + w_3 \cdot P_{\text{device}} + w_4 \cdot C_{\text{compliance}}$$

Where:
- $C_{\text{model}}$ (Model Confidence, 0-100): The raw prediction probability of the model (e.g. classification certainty).
- $D_{\text{data}}$ (Data Drift, 0-100): Statistical distance (e.g., Population Stability Index) of current input variables compared to baseline training profiles.
- $P_{\text{device}}$ (Device Security, 0-100): Score based on network integrity, VPN flags, IP reputation, and emulation indicators.
- $C_{\text{compliance}}$ (Policy Match, 0-100): Score representing alignment with deterministic compliance rules (e.g. deductions if user is approaching limits).

### Weights Configuration
By default, the engine uses:
$$w_1 = 0.35, \quad w_2 = 0.25, \quad w_3 = 0.20, \quad w_4 = 0.20$$

Transactions with a dynamic score **below 75** are flagged for human review. Transactions **below 50** are instantly rejected.

---

## 2. Real-Time Alerting & Notification Engine
AegisAI triggers immediate security alerts on the following events:
- Prompt injection attempts detected.
- Transactions requiring auditor review (Trust Score < 75).
- Model drift surpassing operational stability thresholds.

### Notification Channels
- **WebSocket Broadcast**: Pushes real-time json payloads to connected auditor sessions in the Human Review Portal.
- **Webhook Dispatch**: Sends POST requests to enterprise Security Information and Event Management (SIEM) systems.

---

## 3. Drift & Anomaly Detection
To combat model degradation:
- **Feature Drift**: Evaluates input variables (e.g., distribution of transaction locations) using the **Kolmogorov-Smirnov test**.
- **Concept Drift**: Monitors the accuracy of risk predictions compared to historical audit resolutions.
- Alerts are generated inside the dashboard when feature drift metrics exceed a threshold ($\alpha = 0.05$).

---

## 4. Failure & Chaos Simulation (Chaos Engine)
The Chaos Engine allows administrators to validate the resilience of banking systems:
- **Synthetic Drift Injection**: Skews input variables to simulate changing customer activity or fraudulent attacks, measuring how fast the Trust Engine identifies the drift.
- **Latency Injections**: Adds artificial delays to agent microservices to verify that timeouts and circuit breakers execute correctly.
- **Agent Shutdown**: Shuts down specific containers (e.g., AML Agent) to evaluate if the Orchestrator safely shifts decisions to fallbacks or prompts human review.
