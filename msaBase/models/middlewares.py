import enum


class MiddlewareTypes(enum.Enum):
    profiler = ("Middleware Profiler", True)
    """Profiler Middleware."""
    validationception = ("Handler ValidationError", True)
    """ValidationError Middleware."""
    httpception = ("Handler HTTPException", True)
    """HTTPException Middleware."""
    starception = ("Middleware Starception", True)
    """Starception Middleware."""
    cors = ("Middleware CORS", True)
    """CORS Middleware."""
    httpsredirect = ("Middleware HTTPSRedirect", True)
    """HTTPSRedirect Middleware."""
    gzip = ("Middleware GZip", True)
    """GZip Middleware."""
    session = ("Middleware Session", True)
    """Session Middleware."""
    csrf = ("Middleware CSRF", True)
    """CSRF Middleware."""
    msgpack = ("Middleware MSGPack", True)
    """MSGPack Middleware."""
    context = ("Middleware Context", True)
    """Context Middleware."""
    timing = ("Middleware Timing", True)
    """Timing Middleware."""
    limiter = ("Limiter Handler", True)
    """Handler Middleware."""

    def __init__(self, readable_name: str, need_restart: bool):
        self.readable_name = readable_name
        self.need_restart = need_restart
