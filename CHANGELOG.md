# Changelog

All notable changes to the AegisAI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-19

### Added
- **Transaction Interceptor Pipeline**: Introduced API route `POST /api/v1/transactions/intercept` validating customer, beneficiary, amount and device fingerprint inputs.
- **Dynamic Consensus Engine**: Orchestrates real-time prediction voting mapping KYC, AML, Fraud and Behavior agent consensus weight matrices.
- **AI Research Lab Workspace**: Custom experiment configurations database manager with tabs visual displays under `/dashboard/research`.
- **Executive Decision Intelligence Platform**: Exposes weekly governance grades (A+ to F), maturity indices auditing, failure indexes logging, and dynamic leaderboards.
- **Reporting Engine**: Dynamic compiler outputting binary PDF summaries, CSV lists, and JSON parameter files.
- **System Performance Benchmarks**: Automated benchmarker script evaluating calculation latencies and memory limits.

### Changed
- **Pydantic v2 Migration**: Migrated all database schemas from class-based `class Config` to `model_config = ConfigDict(from_attributes=True)`.
- **FastAPI Endpoint Registry**: Added central endpoints prefix for research and intelligence controller routes.

### Fixed
- Fixed deprecation warnings mapping UTC timestamps.
- Refactored unmapped database attributes mappings inside the agent leaderboards loader.
