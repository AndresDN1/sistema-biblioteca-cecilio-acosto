import time

from flask import Blueprint, Response, current_app, g, request, session

hooks_bp = Blueprint("hooks", __name__)


@hooks_bp.before_app_request
def resolve_user_identity() -> None:
    g.user_id = session.get("user_id", None)
    g.user_role = session.get("role", "GUEST")
    g.request_start_time = time.time()

    current_app.logger.debug(
        "Request intercepted before app request",
        extra={
            "extra_context": {
                "path": request.path,
                "method": request.method,
                "active_identity_id": g.user_id,
                "role_context": g.user_role,
            }
        },
    )


@hooks_bp.after_app_request
def monitor_performance(res: Response) -> Response:
    if hasattr(g, "request_start_time"):
        duration = time.time() - g.request_start_time

        current_app.logger.info(
            "Request cycle finalized",
            extra={
                "extra_context": {
                    "url_path": request.path,
                    "http_method": request.method,
                    "status_code": res.status_code,
                    "latency_seconds": round(duration, 4),
                    "actor_id": g.user_id,
                }
            },
        )

    return res
