# Database Schema & Storage Design

## 1. Storage Architecture Overview
AegisAI employs a multi-model database strategy to isolate relational transactional data from graph relationships and semantic vector indexes:

| Database Tier | Storage Format | Key System Purpose |
|---|---|---|
| **PostgreSQL** | Relational / Document | Audit trails, relational mapping, validation schemas, and policies. |
| **Neo4j** | Graph | Network graph mapping account relationships (AML). |
| **Qdrant** | Vector | Vector collections storing malicious prompt payloads and policy indexes. |
| **Redis** | Key-Value / Memory | Active chaos experiments, session caching, and rate limiting counters. |

---

## 2. PostgreSQL Schema & Data Dictionary

All relational tables are defined in PostgreSQL with **UUID Primary Keys** and optimized indexes.

```
                    [ RELATIONAL DB ENTITIES DIAGRAM ]

  ┌─────────────────────────────────────────────────────────────┐
  │ 1. User & Access Control                                    │
  │    roles ◄──► role_permissions ◄──► permissions             │
  │    └─► users                                                │
  └─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. Core Banking Entities                                    │
  │    customers ──► accounts ◄──► beneficiaries                │
  │    branches       merchants                                 │
  └─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. Transactions & Telemetry                                 │
  │    devices ◄──► transactions                                │
  └─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. Machine Learning & Agents                                │
  │    ai_agents ──► model_versions ──► predictions             │
  │                                     └─► explanations        │
  │    consensus_votes                                          │
  └─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 5. Governance, Audit & Operations                           │
  │    trust_scores     policy_checks      human_reviews        │
  │    audit_logs       compliance_reports                      │
  │    chaos_tests      alerts ──► incidents                    │
  └─────────────────────────────────────────────────────────────┘
```

---

### Group 1: User & Access Control

#### 1. `roles`
* **Purpose**: Defines system authorization groups.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `name` (VARCHAR, Unique, Indexed): Group identifier (e.g. 'admin', 'auditor').
  - `description` (VARCHAR, Nullable): Description.
  - `created_at` (TIMESTAMP): Creation date.
  - `updated_at` (TIMESTAMP): Last update date.

#### 2. `permissions`
* **Purpose**: Atomic resource capability mapping.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `name` (VARCHAR, Unique, Indexed): Permission action string (e.g. 'read:transactions').
  - `description` (VARCHAR): Description.
  - `created_at` (TIMESTAMP): Creation date.

#### 3. `role_permissions`
* **Purpose**: Many-to-many join table linking `roles` and `permissions`.
* **Columns**:
  - `role_id` (UUID, PK, FK to `roles.id`, Cascades).
  - `permission_id` (UUID, PK, FK to `permissions.id`, Cascades).

#### 4. `users`
* **Purpose**: Accounts representing administrative and auditing operators.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `role_id` (UUID, FK to `roles.id`, Index): Associated role.
  - `email` (VARCHAR, Unique, Indexed): User email login.
  - `hashed_password` (VARCHAR): Password string.
  - `is_active` (BOOLEAN): Status toggle.
  - `created_at` (TIMESTAMP): Creation date.
  - `updated_at` (TIMESTAMP): Last update date.

---

### Group 2: Core Banking Entities

#### 5. `customers`
* **Purpose**: Retail and commercial client demographic profiles.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `user_id` (UUID, FK to `users.id`, Nullable, Index): Associated portal login user profile.
  - `first_name` (VARCHAR): Client first name.
  - `last_name` (VARCHAR): Client last name.
  - `email` (VARCHAR, Unique, Indexed): Client contact email.
  - `phone` (VARCHAR, Nullable): Client contact phone.
  - `risk_level` (VARCHAR): Assigned AML risk rating ('low', 'medium', 'high').
  - `status` (VARCHAR): Status toggle ('active', 'suspended').
  - `created_at` (TIMESTAMP): Ingestion timestamp.
  - `updated_at` (TIMESTAMP): Last profile update.

#### 6. `accounts`
* **Purpose**: Financial account balances and identifiers.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `customer_id` (UUID, FK to `customers.id`, Index): Owner customer.
  - `account_number` (VARCHAR, Unique, Indexed): Account number.
  - `account_type` (VARCHAR): Account structure ('checking', 'savings').
  - `balance` (NUMERIC(15,2)): Active balance ledger.
  - `currency` (VARCHAR): Standard currency code.
  - `status` (VARCHAR): State toggle ('active', 'frozen').
  - `created_at` (TIMESTAMP): Account opening timestamp.
  - `updated_at` (TIMESTAMP): Last ledger balance update.

#### 7. `branches`
* **Purpose**: Physical or digital branch location identifiers.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `branch_code` (VARCHAR, Unique, Indexed): Branch code identifier.
  - `name` (VARCHAR): Branch name.
  - `location` (VARCHAR, Nullable): Geographical region descriptions.
  - `created_at` (TIMESTAMP): Creation timestamp.

#### 8. `merchants`
* **Purpose**: Corporate merchant entities processing retail transactions.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `merchant_code` (VARCHAR, Unique, Indexed): Merchant terminal code.
  - `name` (VARCHAR): Merchant name.
  - `category_code` (VARCHAR, Indexed): Merchant Category Code (MCC).
  - `created_at` (TIMESTAMP): Registration timestamp.

#### 9. `beneficiaries`
* **Purpose**: Client-designated pre-authorized transfer targets.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `account_id` (UUID, FK to `accounts.id`, Index): Debited account.
  - `nickname` (VARCHAR, Nullable): Nickname.
  - `beneficiary_account_number` (VARCHAR, Indexed): Recipient account number.
  - `bank_code` (VARCHAR): Target financial routing code.
  - `created_at` (TIMESTAMP): Creation timestamp.

---

### Group 3: Transactions & Telemetry

#### 10. `devices`
* **Purpose**: User terminal attributes evaluating spoof/network warnings.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `fingerprint` (VARCHAR, Unique, Indexed): Hardware hash.
  - `ip_address` (VARCHAR, Indexed): Origin IP.
  - `user_agent` (VARCHAR, Nullable): Browser details.
  - `os` (VARCHAR, Nullable): OS platform details.
  - `is_emulator` (BOOLEAN): Flags emulator detection tools.
  - `location_lat` (NUMERIC(9,6), Nullable): Geographic latitude coordinates.
  - `location_long` (NUMERIC(9,6), Nullable): Geographic longitude coordinates.
  - `created_at` (TIMESTAMP): Creation timestamp.

#### 11. `transactions`
* **Purpose**: Log of transaction requests evaluated by the system.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `account_id` (UUID, FK to `accounts.id`, Index): Origin account.
  - `beneficiary_id` (UUID, FK to `beneficiaries.id`, Nullable, Index): Recipient details.
  - `merchant_id` (UUID, FK to `merchants.id`, Nullable, Index): Merchant details.
  - `branch_id` (UUID, FK to `branches.id`, Nullable, Index): Location details.
  - `device_id` (UUID, FK to `devices.id`, Nullable, Index): Ingested device details.
  - `amount` (NUMERIC(15,2)): Transaction monetary value.
  - `currency` (VARCHAR): Currency code.
  - `transaction_type` (VARCHAR, Indexed): Transaction code ('transfer', 'withdrawal').
  - `status` (VARCHAR, Indexed): Status ('pending', 'approved', 'declined', 'under_review').
  - `reference_number` (VARCHAR, Unique, Indexed): Ledger reference ID.
  - `initiated_at` (TIMESTAMP): Time proposed.
  - `completed_at` (TIMESTAMP, Nullable): Time final execution confirmed.

---

### Group 4: Machine Learning & Agents

#### 12. `ai_agents`
* **Purpose**: Active machine learning model classifications mapping parameters.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `name` (VARCHAR, Unique, Indexed): Agent identifier.
  - `description` (VARCHAR, Nullable): Description.
  - `status` (VARCHAR): Active state ('active', 'inactive').
  - `created_at` (TIMESTAMP): Creation timestamp.
  - `updated_at` (TIMESTAMP): Last configuration update.

#### 13. `model_versions`
* **Purpose**: Specific model parameter details deployed inside the pipeline.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `agent_id` (UUID, FK to `ai_agents.id`, Index): Parent model.
  - `version_string` (VARCHAR, Indexed): Version indicator string.
  - `parameters_hash` (VARCHAR): Config parameters hash.
  - `accuracy_benchmark` (FLOAT): Score on training evaluation datasets.
  - `is_active` (BOOLEAN): Status toggle.
  - `deployed_at` (TIMESTAMP): Date activated in production.

#### 14. `predictions`
* **Purpose**: Raw inference logs generated during transaction evaluation.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `transaction_id` (UUID, FK to `transactions.id`, Index): Context transaction.
  - `model_version_id` (UUID, FK to `model_versions.id`, Index): Executed parameters profile.
  - `prediction_output` (JSONB): Raw JSON model result keys.
  - `confidence_score` (FLOAT): Model certainty value.
  - `latency_ms` (FLOAT): Inference runtime duration.
  - `created_at` (TIMESTAMP): Inference timestamp.

---

### Group 5: Governance, Audit & Operations

#### 15. `consensus_votes`
* **Purpose**: Aggregates separate domain classifications to resolve split results.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `transaction_id` (UUID, FK to `transactions.id`, Index): Transaction context.
  - `decision_verdict` (VARCHAR, Indexed): Consensus verdict ('approve', 'decline').
  - `vote_details` (JSONB): Vote counts map.
  - `consensus_score` (FLOAT): Weighted agreement score (0.0 to 1.0).
  - `created_at` (TIMESTAMP): Record timestamp.

#### 16. `trust_scores`
* **Purpose**: Aggregated safety index generated for the transaction.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `transaction_id` (UUID, FK to `transactions.id`, Index): Transaction context.
  - `score` (INTEGER, Indexed): 0 to 100 trust rating.
  - `weights_configuration` (JSONB): Weight values used in calculation.
  - `reasons` (JSONB): Key factors contributing to score reductions.
  - `created_at` (TIMESTAMP): Evaluation timestamp.

#### 17. `policy_checks`
* **Purpose**: Rules results comparing parameters against legal parameters.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `transaction_id` (UUID, FK to `transactions.id`, Index): Transaction context.
  - `rule_id` (VARCHAR, Indexed): Policy code.
  - `status` (VARCHAR, Indexed): Result ('pass', 'fail', 'warn').
  - `details` (JSONB): Violations logs list.
  - `executed_at` (TIMESTAMP): Evaluation timestamp.

#### 18. `explanations`
* **Purpose**: Human-readable rationales explaining prediction outcomes.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `prediction_id` (UUID, FK to `predictions.id`, Index): Inference context.
  - `explanation_text` (VARCHAR(1000)): Plain text description.
  - `feature_attributions` (JSONB): SHAP key-value map.
  - `explanation_vector` (DOUBLE PRECISION[]): Floating-point array mapping dimensions for semantic search.
  - `created_at` (TIMESTAMP): Generation timestamp.

#### 19. `human_reviews`
* **Purpose**: Auditor manual reviews for low trust transactions.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `transaction_id` (UUID, FK to `transactions.id`, Index): Transaction context.
  - `reviewer_id` (UUID, FK to `users.id`, Nullable, Index): Auditor assigned.
  - `status` (VARCHAR, Indexed): Review status ('pending', 'approved', 'declined').
  - `comments` (VARCHAR(1000), Nullable): Audit notes.
  - `assigned_at` (TIMESTAMP): Assigned timestamp.
  - `reviewed_at` (TIMESTAMP, Nullable): Action resolved timestamp.

#### 20. `audit_logs`
* **Purpose**: Immutable activity logging checking data modifications.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `actor_id` (UUID, FK to `users.id`, Nullable, Index): Auditor ID initiating change.
  - `action_type` (VARCHAR, Indexed): Event classification (e.g. 'override_limit', 'policy_update').
  - `description` (VARCHAR(500)): Explanatory notes.
  - `resource_id` (VARCHAR, Nullable, Indexed): ID of modified object.
  - `metadata` (JSONB, Nullable): Action detail maps.
  - `ledger_hash` (VARCHAR(64)): SHA-256 chain tracking log record validity.
  - `created_at` (TIMESTAMP): Logging timestamp.

#### 21. `compliance_reports`
* **Purpose**: Compiled compliance profiles mapping regulatory checks.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `generated_by_id` (UUID, FK to `users.id`, Index): Operator requesting compilation.
  - `report_type` (VARCHAR, Indexed): Report configuration category ('SOC2', 'GDPR').
  - `file_path` (VARCHAR): Link target in storage bucket.
  - `metadata` (JSONB, Nullable): Compilation metrics details map.
  - `created_at` (TIMESTAMP): Compilation timestamp.

---

### Group 6: Operational Alerts & Chaos

#### 22. `chaos_tests`
* **Purpose**: Failure simulations evaluating stability.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `scenario_id` (VARCHAR, Indexed): Chaos scenario configuration key.
  - `target_agent_id` (UUID, FK to `ai_agents.id`, Index): Target agent microservice.
  - `parameters` (JSONB): Execution boundaries (latency, drift percentage).
  - `status` (VARCHAR): Execution state ('active', 'completed', 'failed').
  - `started_at` (TIMESTAMP): Simulation start time.
  - `completed_at` (TIMESTAMP, Nullable): Simulation stop time.

#### 23. `alerts`
* **Purpose**: System warnings triggered by model failures or validation violations.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `transaction_id` (UUID, FK to `transactions.id`, Nullable, Index): Transaction context if applicable.
  - `severity` (VARCHAR, Indexed): Alert severity ('low', 'medium', 'high', 'critical').
  - `message` (VARCHAR(255)): Message text.
  - `is_resolved` (BOOLEAN): Status flag.
  - `created_at` (TIMESTAMP): Ingestion timestamp.

#### 24. `incidents`
* **Purpose**: Compliance or infrastructure failures requiring operational investigations.
* **Columns**:
  - `id` (UUID, Primary Key): Unique identifier.
  - `alert_id` (UUID, FK to `alerts.id`, Nullable, Index): Root cause alert reference.
  - `description` (VARCHAR(500)): Explanatory notes.
  - `status` (VARCHAR, Indexed): Incident state ('open', 'investigating', 'resolved').
  - `severity` (VARCHAR, Indexed): Incident severity category.
  - `created_at` (TIMESTAMP): Creation timestamp.
  - `resolved_at` (TIMESTAMP, Nullable): Action resolved timestamp.
