import json
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.services.security_layer import security_service

logger = logging.getLogger("aegisai.prompt_firewall")

class PromptFirewallMiddleware(BaseHTTPMiddleware):
    """
    Prompt Firewall middleware intercepting incoming inference request prompts
    to scan for injection payloads, jailbreaks, leakages, and credentials.
    """

    def __init__(self, app) -> None:
        super().__init__(app)
        # Intercept copilot queries, agent valuations, and direct scans
        self.target_paths = {
            "/api/v1/copilot/query",
            "/api/v1/agents/evaluate",
            "/api/v1/compliance/check"
        }

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in self.target_paths or request.method not in ("POST", "PUT"):
            return await call_next(request)

        actor_ip = request.client.host if request.client else "127.0.0.1"

        try:
            # Buffer body content to inspect
            body_bytes = await request.body()
            
            # Allow Next.js/FastAPI router to read body again
            async def receive():
                return {"type": "http.request", "body": body_bytes, "more_body": False}
            request._receive = receive

            # Parse prompt parameter in JSON request
            body_str = body_bytes.decode("utf-8")
            if body_str:
                data = json.loads(body_str)
                # Scan typical keys containing prompt data
                prompt_content = data.get("prompt") or data.get("query") or data.get("message") or data.get("text")
                
                if prompt_content and isinstance(prompt_content, str):
                    is_blocked, rules, sanitized = security_service.scan_prompt(prompt_content, actor_ip)
                    
                    if is_blocked:
                        logger.warning(f"AI Security Firewall blocked request from {actor_ip}. Rules fired: {rules}")
                        return JSONResponse(
                            status_code=400,
                            content={
                                "detail": "Request blocked by AegisAI Security Layer.",
                                "rules_fired": rules,
                                "status": "blocked"
                            }
                        )

        except Exception as e:
            logger.error(f"Prompt firewall interception error: {e}")
            # Non-blocking on parse error to protect availability

        return await call_next(request)
