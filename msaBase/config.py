# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import List, Optional

from msaDocModels.health import MSAHealthDefinition
from pydantic import BaseModel

from msaBase.models.settings import MSAAppSettings


class MSAServiceStatus(BaseModel):
    """
    **MSAServiceStatus** Pydantic Response Class
    """

    name: Optional[str] = "msaSDK Service"
    """Service Name."""
    healthy: Optional[str] = "None"
    """Health status"""
    message: Optional[str] = "None"
    """Optional Message Text"""


class MSAServiceDefinition(MSAAppSettings):
    """
    MSAApp Settings (Service Definitions)

    This class enables the configuration of your MSAApp instance through the use of environment variables.

    Any of the instance attributes can be overridden upon instantiation by either passing the desired value to the
    initializer, or by setting the corresponding environment variable.

    Attribute `xxx_yyy` corresponds to environment variable `API_XXX_YYY`. So, for example, to override
    `openapi_prefix`, you would set the environment variable `API_OPENAPI_PREFIX`.

    Note that assignments to variables are also validated, ensuring that even if you make runtime-modifications
    to the config, they should have the correct types.
    """

    name: str = "msaBase Service"
    """Service Name, also used as Title."""
    version: str = "0.0.0"
    """Version of the Service."""
    host: str = "127.0.0.1"
    """Host/IP which the service runs on."""
    port: int = 8090
    """Port which the service binds to."""
    tags: List[str] = []
    """Optional Metadata: Use this to carry some variables through the service instance."""
    allow_origins: List[str] = ["*"]
    """CORSMiddleware. List[str]. List of allowed origins (as strings) or all of them with the wildcard ``*`` ."""
    allow_credentials: bool = False
    """CORSMiddleware. Bool. Allow (False) Credentials (Authorization headers, Cookies, etc)."""
    allow_methods: List[str] = ["*"]
    """CORSMiddleware. List[str]. Specific HTTP methods (POST, PUT) or all of them with the wildcard ``*`` ."""
    allow_headers: List[str] = ["*"]
    """CORSMiddleware. List[str]. Specific HTTP headers or all of them with the wildcard ``*`` ."""
    healthdefinition: MSAHealthDefinition = MSAHealthDefinition()
    """Healthdefinition Instance."""
    uvloop: bool = True
    """Use UVLoop instead of asyncio loop."""
    sysrouter: bool = True
    """Enable the System Routes defined by router.system module (/sysinfo, /sysgpuinfo, /syserror, ...)."""
    servicerouter: bool = True
    """Enable the Service Routes defined by the MSAApp (/scheduler, /status, /defintion, /settings, /schema, /info, ...)."""
    starception: bool = True
    """Enable Starception Middleware."""
    validationception: bool = True
    """Enable Validation Exception Handler."""
    httpception: bool = True
    """Enable the HTTP Exception Handler, which provides HTML Error Pages instead of JSONResponse."""
    httpception_exclude: List[int] = [
        307,
    ]
    """List of HTTP Exception Codes which are excluded and just forwarded by the HTTP Exception Handler."""
    cors: bool = True
    """Enable CORS Middleware."""
    httpsredirect: bool = False
    """Enable HTTPS Redirect Middleware."""
    gzip: bool = False
    """Enable GZIP Middleware."""
    session: bool = False
    """Enable Session Middleware."""
    csrf: bool = False
    """Enable CSRF Forms Protection Middleware."""
    msgpack: bool = False
    """Enable Messagepack Negotiation Middleware."""
    instrument: bool = True
    """Enable Prometheus Instrumentation for the instance."""
    signal_middleware: bool = False
    """Enable MSASignal Middleware."""
    task_middleware: bool = False
    """Enable MSATask Middleware."""
    graphql: bool = False
    """Enable initiation of Strawberry GraphQLRouter (/graphql)."""
    context: bool = False
    """Enable Context Middleware."""
    profiler: bool = False
    """Enable Profiler Middleware."""
    profiler_output_type: str = "html"  # text or html
    """Set the Profiler Output Type, should be html or text, html is needed if you want to use the profiler on the Admin Site."""
    profiler_single_calls: bool = False
    """Enable to Track each Request by the Profiler."""
    profiler_url: str = "/profiler"
    """Set the URL to reach the profiler result html, /profiler."""
    timing: bool = False
    """Enables Timing Middleware, reports timing data at the granularity of individual endpoint calls."""
    limiter: bool = False
    """Enables Rate Limiter (slowapi)."""
    background_scheduler: bool = True
    "Enables Background Scheduler."
    asyncio_scheduler: bool = True
    "Enables Asyncio Scheduler."
    abstract_fs: bool = False
    """Enables internal Abstract Filesystem."""
    abstract_fs_url: str = "."
    """Set's Filesystem URL"""
    json_db: bool = False
    """Enables internal NoSQl/TinyDB DB."""
    json_db_memory_only: bool = False
    """JSON DB only in memory, don't store to file/db url"""
    json_db_url: str = "./msa_base.json"
    """Set's DB URL, compatibility with async and BaseModel/SQLAlchemy is required."""
    sqlite_db: bool = False
    """Enables internal Asynchron SQLite DB."""
    sqlite_db_debug: bool = False
    """Enables internal DB Debug output."""
    sqlite_db_crud: bool = False
    """Enables CRUD API creation of the provided BaseModels."""
    sqlite_db_meta_drop: bool = False
    """If True, all existing Data and Schemas in internal DB get's deleted at Startup."""
    sqlite_db_meta_create: bool = False
    """Enables internal DB Metadata creation from defined BaseModels at Startup."""
    sqlite_db_url: str = "sqlite+aiosqlite:///msa_base.sqlite_db?check_same_thread=True"
    """Set's DB URL, compatibility with async and BaseModel/SQLAlchemy is required."""


@lru_cache()
def get_msa_app_settings() -> MSAServiceDefinition:
    """
    This function returns a cached instance of the MSAServiceDefinition object.
    Note:
        Caching is used to prevent re-reading the environment every time the API settings are used in an endpoint.
    """
    return MSAServiceDefinition()
