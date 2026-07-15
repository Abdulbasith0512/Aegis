# Security Architecture & Compliance Policies

This document details the security model, container sandboxing, data protection policies, and compliance boundaries of AegisAI.

---

## 1. Network & Container Isolation
AegisAI employs a dual-boundary architectural layout to split untrusted model execution from trusted financial workflows:

```
[ Public Network / Clients ]
            │
            ▼ (HTTPS / TLS 1.3)
   ┌─────────────────┐
   │   API Gateway   │
   └────────┬────────┘
            │
            ▼ (Internal VPC / mTLS)
   ┌────────────────────────────────────────────────────────┐
   │ CONTROL PLANE (Orchestrator, Explainability, Trust)    │
   └────────────────────────┬───────────────────────────────┘
                            │
                            ▼ (Isolated gRPC / Local Loopback)
   ┌────────────────────────────────────────────────────────┐
   │ SECURITY SANDBOX ZONE                                  │
   │  - Fraud, AML, KYC, Device Agents (No egress internet) │
   └────────────────────────────────────────────────────────┘
```

- **No Egress for Models**: Domain agents run in container networks with egress traffic disabled. External LLM calls are routed via the central API Gateway which logs payloads.
- **Mutual TLS (mTLS)**: All communication between the API Gateway and backend microservices is encrypted using TLS with mutual authentication.

---

## 2. Real-Time PII Masking & Data Redaction
To ensure compliance with GDPR, HIPAA, and financial privacy laws, the API Gateway runs an inline PII Masking filter on all prompts:

```
Input Prompt: "Verify transfer of $500 for John Doe (SSN: 000-12-3456)"
Filter: Ingest -> Regex/Model Scan -> Masking
Masked Prompt: "Verify transfer of $500 for [REDACTED_NAME] (SSN: [REDACTED_SSN])"
```

* **Masking Strategy**:
  - Regex patterns mask SSNs, credit card numbers, email addresses, and phone numbers.
  - Named Entity Recognition (NER) models mask names, addresses, and organizations.
  - The map of hashes is saved inside a secure, encrypted Redis cache keyspace to allow mapping of the unmasked values on response ingestion.

---

## 3. Ephemeral Sandbox Execution
When autonomous agents need to execute tool calls (e.g. searching databases, writing documents), they must not execute code on the host machine.
- **Docker-in-Docker Sandboxing**: Spawns isolated, ephemeral Docker runtimes with limited execution memory (256MB) and a CPU quota (0.25 cores).
- **Execution step limits**: Run loops are capped at a max execution depth of 10 steps to prevent infinite loop recursion.

---

## 4. Cryptographic Audit Ledger (WORM Compliance)
To verify database record integrity:
- Every agent decision and user action logged to PostgreSQL is appended with a SHA-256 hash.
- The hash computes: `hash_n = SHA256(data_n + hash_n-1)`.
- This creates an immutable hash chain, ensuring any tampering with historical audit rows invalidates the chain.
