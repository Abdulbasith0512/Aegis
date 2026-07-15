from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Any, Dict

def customize_swagger(app: FastAPI) -> None:
    """
    Overrides FastAPI's default OpenAPI schema generation
    to inject custom branding, descriptions, and metadata.
    """
    if app.openapi_schema:
        return

    openapi_schema: Dict[str, Any] = get_openapi(
        title="AegisAI Governance Engine API",
        version=app.version,
        description=(
            "### AegisAI Control Plane API\n\n"
            "This API Gateway coordinates active supervision, real-time safety guardrails, "
            "explainability calculations, and compliance mapping for banking AI agents.\n\n"
            "* **Clean Architecture Boundaries**\n"
            "* **Strict Banking Governance Policies**\n"
            "* **mTLS & Ephemeral Runtimes Sandboxing Ready**"
        ),
        routes=app.routes,
    )

    # Inject custom branding/logos into Swagger details
    openapi_schema["info"]["x-logo"] = {
        "url": "https://aegisai.internal/assets/logo.png"
    }

    app.openapi_schema = openapi_schema
