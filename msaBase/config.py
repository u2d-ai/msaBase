# -*- coding: utf-8 -*-
import json
import os
from typing import Any, Dict, List, Optional, Union

from msaBase.logger import logger
from msaBase.models.settings import MSAAppSettings
from msaDocModels.health import MSAHealthDefinition
from pydantic import BaseModel


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

    Attributes:
        name: Service Name, also used as Title.
        description: Description of the Service.
        version: Version of the Service.
        host: Host/IP which the service runs on.
        port: Port which the service binds to.
        dapr_http_port: Port http which  used dapr app.
        dapr_grpc_port: Port grpc which used dapr app.
        tags: Optional Metadata: Use this to carry some variables through the service instance.
        allow_origins: CORSMiddleware. List of allowed origins (as strings) or all of them with the wildcard "*".
        allow_credentials: CORSMiddleware. Allow (False) Credentials (Authorization headers, Cookies, etc).
        allow_methods: CORSMiddleware. Specific HTTP methods (POST, PUT) or all of them with the wildcard "*".
        allow_headers: CORSMiddleware. List[str]. Specific HTTP headers or all of them with the wildcard "*".
        healthdefinition: Healthdefinition Instance.
        uvloop: Use UVLoop instead of asyncio loop.
        sysrouter: Enable the System Routes defined by router.system module (/sysinfo, /sysgpuinfo, /syserror, ...).
        servicerouter: Enable the Service Routes defined by the MSAApp
        (/scheduler, /status, /defintion, /settings, /schema, /info, ...).
        starception: Enable Starception Middleware.
        validationception: Enable Validation Exception Handler.
        httpception: Enable the HTTP Exception Handler, which provides HTML Error Pages instead of JSONResponse.
        httpception_exclude: List of HTTP Exception Codes which are excluded and just
        forwarded by the HTTP Exception Handler.
        cors: Enable CORS Middleware.
        httpsredirect: Enable HTTPS Redirect Middleware.
        gzip: Enable GZIP Middleware.
        session: Enable Session Middleware.
        csrf: Enable CSRF Forms Protection Middleware.
        msgpack: Enable Messagepack Negotiation Middleware.
        instrument: Enable Prometheus Instrumentation for the instance.
        signal_middleware: Enable MSASignal Middleware.
        task_middleware: Enable MSATask Middleware.
        context: Enable Context Middleware.
        profiler: Enable Profiler Middleware.
        profiler_output_type: Set the Profiler Output Type, should be html or text,
        html is needed if you want to use the profiler on the Admin Site.
        profiler_single_calls: Enable to Track each Request by the Profiler.
        profiler_url: Set the URL to reach the profiler result html, /profiler.
        timing: Enables Timing Middleware, reports timing data at the granularity of individual endpoint calls.
        limiter: Enables Rate Limiter (slowapi).
        background_scheduler: Enables Background Scheduler.
        asyncio_scheduler: Enables Asyncio Scheduler.
        abstract_fs: Enables internal Abstract Filesystem.
        abstract_fs_url: Set's Filesystem URL.
        json_db_url: Set's DB URL, for nonlocal JSON DB.
        contact: Contacts of the service owner.
        progress_topic: Topic to which services send their progress.
    """

    name: str = "msaBase Service"
    description: str = ""
    version: str = "0.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    dapr_http_port: int = 6000
    dapr_grpc_port: int = 50001
    tags: List[str] = []
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = False
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]
    healthdefinition: MSAHealthDefinition = MSAHealthDefinition()
    uvloop: bool = True
    sysrouter: bool = True
    servicerouter: bool = True
    starception: bool = True
    validationception: bool = True
    httpception: bool = True
    httpception_exclude: List[int] = [307]
    cors: bool = True
    httpsredirect: bool = False
    gzip: bool = False
    session: bool = False
    csrf: bool = False
    msgpack: bool = False
    instrument: bool = True
    signal_middleware: bool = False
    task_middleware: bool = False
    context: bool = False
    profiler: bool = False
    profiler_output_type: str = "html"  # text or html
    profiler_single_calls: bool = False
    profiler_url: str = "/profiler"
    timing: bool = False
    limiter: bool = False
    background_scheduler: bool = False
    asyncio_scheduler: bool = False
    abstract_fs: bool = False
    abstract_fs_url: str = "."
    json_db_url: str = ""
    sql_db_url: str = ""
    contact: Dict[str, Union[str, Any]] = {
        "name": "Marcus Rostalski",
        "url": "https://www.sparkasse-bremen.de/",
        "email": "marcus.rostalski@sparkasse-bremen.de",
    }
    progress_topic: str = "spk-progress"

    def save_config(self) -> None:
        """
        Saves config to a JSON file
        """
        sa = self.copy(deep=True)
        with open("config.json", "w") as fp:
            json.dump(sa.dict(), fp, sort_keys=True, indent=4)

    @staticmethod
    def load_config():
        """
        Loads config from JSON file.

        Returns:
            MSAServiceDefinition config model
        """
        ret: MSAServiceDefinition = MSAServiceDefinition()
        if os.path.exists("config.json"):
            with open("config.json", "rb") as fp:
                intext = json.load(fp)
                ret = MSAServiceDefinition.parse_obj(intext)
            logger.info("Loaded config file")
        else:
            ret.save_config()
        return ret


def get_msa_app_settings() -> MSAServiceDefinition:
    """
    Returns a cached instance of the MSAServiceDefinition object.

    Note:
        Caching is used to prevent re-reading the environment every time the API settings are used in an endpoint.
    """
    return _msa_config


class ConfigDTO(BaseModel):
    """
    DTO that contains needed attributes to be processed.

    Attributes:
        one_time: Flag indicating whether the configuration is applied only to one request.
        config: Service config.
    """

    one_time: bool = False
    config: MSAServiceDefinition


class ConfigInput(BaseModel):
    """
    Pydantic model to receive service configs from pub/sub.

    Attributes:
        data: Service config.
    """

    data: ConfigDTO


class ConfigDataDTO(BaseModel):
    """
    DTO that represents result of service work.

    Attributes:
        service_name: Service name to distinguish.
        config_dto: Service config.
    """

    service_name: str
    config_dto: ConfigDTO


_msa_config: MSAServiceDefinition = MSAServiceDefinition.load_config()
