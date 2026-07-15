# AegisAI API Specification

Base Endpoint URL: `https://api.aegisai.internal/api/v1`

---

## 1. Authentication

### 1.1 POST `/auth/login`
Authenticates administrators or human review auditors.

* **Request Body**:
  ```json
  {
    "email": "auditor@aegisai.bank",
    "password": "secure_password"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
    "token_type": "bearer"
  }
  ```

---

## 2. Transactions & Interception

### 2.1 POST `/transactions/intercept`
Intercepts a proposed banking transaction for security evaluation.

* **Request Body**:
  ```json
  {
    "account_number": "1002934",
    "amount": 25000.00,
    "recipient_account": "9938472",
    "device_ip": "198.51.100.12",
    "currency": "USD"
  }
  ```
* **Response (200 OK - Approved)**:
  ```json
  {
    "transaction_id": "8a01db4c-c081-4f11-9a99-4d69317bbbf1",
    "verdict": "approved",
    "trust_score": 92,
    "requires_review": false,
    "explanation": "Transaction complies with all standard risk parameters."
  }
  ```
* **Response (200 OK - Requires Review / Pending)**:
  ```json
  {
    "transaction_id": "8a01db4c-c081-4f11-9a99-4d69317bbbf1",
    "verdict": "pending",
    "trust_score": 62,
    "requires_review": true,
    "explanation": "Transaction amount exceeds threshold for new device IP.",
    "escalated_rules": ["rule-102: New Device IP Transaction Threshold"]
  }
  ```

---

## 3. Agents Control

### 3.1 GET `/agents`
Returns status lists of supervised autonomous banking agents.

* **Response (200 OK)**:
  ```json
  [
    {
      "agent_id": "fraud-agent",
      "status": "active",
      "model_version": "v1.4.2",
      "avg_latency_ms": 32.5
    },
    {
      "agent_id": "aml-agent",
      "status": "active",
      "model_version": "v2.1.0",
      "avg_latency_ms": 48.1
    }
  ]
  ```

---

## 4. Compliance Policies

### 4.1 GET `/compliance/rules`
Fetch active regulatory checks configured in the Policy Engine.

* **Response (200 OK)**:
  ```json
  [
    {
      "rule_id": "rule-101",
      "name": "AML Structuring Check",
      "action": "block",
      "enabled": true
    }
  ]
  ```

---

## 5. Chaos Simulation

### 5.1 POST `/chaos/inject`
Triggers an active chaos experiment on target agents.

* **Request Body**:
  ```json
  {
    "scenario_id": "geo-drift",
    "target_agent": "fraud-agent",
    "duration_seconds": 600
  }
  ```
* **Response (202 Accepted)**:
  ```json
  {
    "experiment_id": "e9a04a5d-ec4b-4b10-a232-db27cdad9db9",
    "status": "active",
    "message": "Synthetic input data drift injection started."
  }
  ```

---

## 6. Live Portal WebSockets

### 6.1 WS `/portal/ws`
Auditors connect to this WebSocket to receive live, high-priority transactions awaiting human review.

* **Server Outbound Payload (Transaction Pending Alert)**:
  ```json
  {
    "event": "transaction_review_required",
    "data": {
      "transaction_id": "8a01db4c-c081-4f11-9a99-4d69317bbbf1",
      "amount": 25000.00,
      "trust_score": 62,
      "reasons": ["Transaction exceeds threshold for new device IP"]
    }
  }
  ```
