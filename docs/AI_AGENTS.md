# Banking AI Agents Specification

This document details the functional specifications, model architectures, and interfaces for the six core banking agents operated by the AegisAI Control Plane.

---

## 1. Device Agent (`agents/domain/device.py`)
* **Purpose**: Evaluates user device integrity, network authenticity, and location threats.
* **Input Schema**:
  ```json
  {
    "device_ip": "198.51.100.12",
    "user_agent": "Mozilla/5.0...",
    "fingerprint": "df4a2e88b39c09c2a3ef",
    "location_lat_long": [35.6762, 139.6503]
  }
  ```
* **Decision Logic**:
  - Compares IP against known proxy, VPN, and TOR list databases.
  - Matches device fingerprint against historical logins.
  - Calculates geographical speed anomalies (e.g. login from Tokyo 10 minutes after login from London).
* **Output Schema**:
  ```json
  {
    "device_trust_score": 85,
    "vpn_detected": false,
    "is_new_device": false,
    "geo_anomaly": false
  }
  ```

---

## 2. KYC Agent (`agents/domain/kyc.py`)
* **Purpose**: Inspects user documentation, registry status, and identity attributes.
* **Input Schema**:
  ```json
  {
    "user_id": "usr_99824a7d",
    "document_type": "passport",
    "document_image_path": "/vault/docs/doc_0029.jpg"
  }
  ```
* **Decision Logic**:
  - Executes document verification models (layout matching, OCR extraction).
  - Cross-references national databases or credit bureau registry records.
* **Output Schema**:
  ```json
  {
    "identity_verified": true,
    "document_match_confidence": 0.98,
    "pep_status_flag": false
  }
  ```

---

## 3. Behavior Agent (`agents/domain/behavior.py`)
* **Purpose**: Detects anomalies in user interactions compared to historic base transaction profiles.
* **Input Schema**:
  ```json
  {
    "user_id": "usr_99824a7d",
    "transaction_amount": 250.00,
    "transaction_timestamp": "2026-07-15T09:32:00Z"
  }
  ```
* **Decision Logic**:
  - Isolation Forest model checks transaction details (amount, velocity, time-of-day) against historical profile clusters.
* **Output Schema**:
  ```json
  {
    "behavioral_anomaly_flag": false,
    "anomaly_score": 0.12
  }
  ```

---

## 4. Fraud Agent (`agents/domain/fraud.py`)
* **Purpose**: Identifies transaction-level risk models for instant payments.
* **Input Schema**:
  - Ingestion payload combined with output maps from Device Agent and Behavior Agent.
* **Decision Logic**:
  - XGBoost classifier trained on historical transaction fraud patterns. Evaluates amounts, device risk, behavior anomaly indicators, and vendor risk profiles.
* **Output Schema**:
  ```json
  {
    "fraud_risk_probability": 0.04,
    "verdict": "low_risk"
  }
  ```

---

## 5. AML Agent (`agents/domain/aml.py`)
* **Purpose**: Analyzes relational graphs to flag money structuring, laundering, or asset placement patterns.
* **Input Schema**:
  - Source account, destination account, transfer chains.
* **Decision Logic**:
  - Queries Neo4j database to identify transactional chains, cycles (looping transfers), or highly-connected hub accounts.
* **Output Schema**:
  ```json
  {
    "aml_alert_flag": false,
    "graph_cycle_detected": false,
    "hop_count": 1
  }
  ```

---

## 6. Compliance Agent (`agents/domain/compliance.py`)
* **Purpose**: Assesses regulatory logic (e.g., USA PATRIOT Act KYC compliance, Fair Lending criteria) and updates compliance tables.
* **Input Schema**:
  - End-to-end trace payload from preceding agents.
* **Decision Logic**:
  - Evaluation of strict regulatory policies (e.g. blocking transactions to OFAC sanctioned entities).
* **Output Schema**:
  ```json
  {
    "compliance_verdict": "pass",
    "violated_policies": []
  }
  ```
