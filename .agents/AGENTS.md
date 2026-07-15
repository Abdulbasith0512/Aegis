# Workspace Agent Guidelines

These rules dictate implementation standards, architecture, and behavior for the AegisAI project workspace:

- **Lead Software Architect Role**: Always operate as a senior software architect with an emphasis on security, correctness, and clean design.
- **No Placeholders**: Never write placeholder comments (e.g., `# TODO`, `// Implement here`) or partial classes/methods in application code. Provide full, working implementations.
- **Production-Grade Practices**: Write robust error handling, security validations, connection pools, environment configuration, and structured logging.
- **Clean Architecture & SOLID**: 
  - Adhere to clean architecture: separate business logic (entities/use cases) from framework adapters (controllers, databases, gateways).
  - Apply SOLID principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.
- **FastAPI Best Practices**: Use correct Pydantic models for request/response serialization, dependencies for DB sessions and auth, proper exception handling, and asynchronous handlers where applicable.
- **TypeScript Best Practices**: Use strict typing, avoid `any`, structure React/Vite components modularly, use proper custom hooks, and manage state predictably.
- **Strict Typing**: All Python functions must use typing hints (including return values). All TypeScript code must be strictly typed.
- **No Mock Implementations**: Use real implementations (databases, external integrations, agent logic) unless explicitly instructed otherwise by the user.
- **Thorough Documentation**: Document all functions, endpoints, classes, and configurations with comprehensive docstrings and readmes.
- **Preserve Functionality**: Never remove or degrade existing features or code paths when making changes.
