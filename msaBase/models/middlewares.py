import enum


class MiddlewareTypes(enum.Enum):
    """
    Types of middlewares and whether they require a service reload when changed.

    Attributes:
        profiler: Profiler Middleware.
        validationception: ValidationError Middleware.
        httpception: HTTPException Middleware.
        starception: Starception Middleware.
        cors: CORS Middleware.
        httpsredirect: HTTPSRedirect Middleware.
        gzip: GZip Middleware.
        session: Session Middleware.
        csrf: CSRF Middleware.
        msgpack: MSGPack Middleware.
        context: Context Middleware.
        timing: Timing Middleware.
        limiter: Handler Middleware.
    """

    profiler = ("Middleware Profiler", True)
    validationception = ("Handler ValidationError", True)
    httpception = ("Handler HTTPException", True)
    starception = ("Middleware Starception", True)
    cors = ("Middleware CORS", True)
    httpsredirect = ("Middleware HTTPSRedirect", True)
    gzip = ("Middleware GZip", True)
    session = ("Middleware Session", True)
    csrf = ("Middleware CSRF", True)
    msgpack = ("Middleware MSGPack", True)
    context = ("Middleware Context", True)
    timing = ("Middleware Timing", True)
    limiter = ("Limiter Handler", True)
    """"""

    def __init__(self, readable_name: str, need_restart: bool):
        self.readable_name = readable_name
        self.need_restart = need_restart
