# -*- coding: utf-8 -*-
"""Main Service Module for MSAApp.

Initialize with a MSAServiceDefintion Instance to control the features and functions of the MSAApp.

"""
import json
import os
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Type, Union

import aiohttp
import sentry_sdk
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from dapr.clients import DaprClient, DaprInternalError
from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from fs.base import FS
from grpc._channel import _InactiveRpcError
from loguru import logger as logger_gruru
from msaBase.config import ConfigDTO, ConfigInput, MSAServiceDefinition, MSAServiceStatus, get_msa_app_settings
from msaBase.errorhandling import getMSABaseExceptionHandler
from msaBase.logger import init_logging
from msaBase.models.functionality import FunctionalityTypes
from msaBase.models.middlewares import MiddlewareTypes
from msaBase.models.sysinfo import MSASystemGPUInfo, MSASystemInfo
from msaBase.sysinfo import get_sysgpuinfo, get_sysinfo
from msaBase.utils.constants import PROGRESS_TOPIC, PUBSUB_NAME, REGISTRY_TOPIC, SERVICE_TOPIC
from msaDocModels.health import MSAHealthDefinition
from msaDocModels.openapi import MSAOpenAPIInfo
from msaDocModels.scheduler import MSASchedulerStatus, MSASchedulerTaskDetail, MSASchedulerTaskStatus
from msaDocModels.sdu import SDUVersion
from msaFilesystem.msafs import MSAFilesystem
from pyinstrument import Profiler
from slowapi import Limiter
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette_context import plugins


def get_secret_key() -> str:
    """
    Get Secret Key for Token creation from OS Environment Variable **SECRET_KEY_TOKEN**

    Returns:
        key: The SECRET_KEY_TOKEN.

    """
    key: str = os.getenv(
        "SECRET_KEY_TOKEN",
        "u2dmsaservicex_#M8A{1o3Bd?<ipwt^K},Z)OE<Fkj-X9IILWq|Cf`Y:HFI~&2L%Ion3}+p{T%",
    )
    return key


def get_secret_key_sessions() -> str:
    """
    Get Secret Key for Session Middleware from OS Environment Variable **SECRET_KEY_SESSIONS**

    Returns:
        key: The SECRET_KEY_SESSIONS.

    """
    key: str = os.getenv(
        "SECRET_KEY_SESSIONS",
        "u2dmsaserviceeP)zg5<g@4WJ0W8'?ad!T9UBvW1z2k|y~|Pgtewv=H?GY_Q]t~-~UUe'pJ0V[>!<)",
    )
    return key


def get_secret_key_csrf() -> str:
    """
    Get Secret Key for CSRF Middleware from OS Environment Variable **SECRET_KEY_CSRF**

    Returns:
        key: The SECRET_KEY_CSRF.

    """
    key: str = os.getenv(
        "SECRET_KEY_CSRF",
        "u2dmsaservicee_rJM'onkEV1trD=I7dci$flB)aSNW+raL4j]Ww=n~_BRg35*3~(E.>rx`1aTw:s",
    )
    return key


async def load_config(url: str) -> None:
    """
    Get config.

    Parameters:

        url: request URL.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    config = MSAServiceDefinition.parse_obj(await resp.json())
                    new_config = get_msa_app_settings()
                    if new_config.dict(exclude={"version"}) == config.dict(exclude={"version"}):
                        return

                    with open("config.json", "w") as json_file:
                        json.dump(config.dict(), json_file, sort_keys=True, indent=4)

                    logger_gruru.info("New config saved to config.json")
                else:
                    logger_gruru.info("Config not found")
    except BaseException as ex:
        logger_gruru.error(ex)


class MSAApp(FastAPI):
    """Creates an application msaBase instance.

    Note:
        As with FastApi the MSAApp provides two events:
        ``startup``: A list of callables to run on application startup. Startup handler callables do not take
        any arguments, and may be be either standard functions, or async functions.
        ``shutdown``: A list of callables to run on application shutdown. Shutdown handler callables do not
        take any arguments, and may be be either standard functions, or async functions.
        Those are also used internally, which are triggered before the external events.

        Do not include the `self` parameter in the ``Args`` section.

    Args:
        settings: MSAServiceDefinition (Must be provided), instance of a service definition with all settings
        sql_models: List of SQLModel Default None, provide list of your SQLModel Classes and the instance can create
        CRUD API and if site is enabled also UI for CRUD auto_mount_site: Default True,
        if site is enabled in settings and this is true, mounts the site in internal startup event.

    Attributes:
        logger: loguru logger instance
        auto_mount_site: bool auto_mount_site
        settings: MSAServiceDefinition settings instance.
        limiter: Limiter = None
        ROOTPATH: str os.path.join(os.path.dirname(__file__))

    """

    def __init__(
        self,
        settings: MSAServiceDefinition,
        auto_mount_site: Optional[bool] = True,
        title: Optional[str] = None,
        description: Optional[str] = None,
        host: Optional[str] = None,
        version: Optional[str] = None,
        openapi_url: Optional[str] = None,
        redoc_url: Optional[str] = None,
        openapi_tags: Optional[List[Dict[str, Any]]] = None,
        terms_of_service: Optional[str] = None,
        contact: Optional[Dict[str, Union[str, Any]]] = None,
        license_info: Optional[Dict[str, Union[str, Any]]] = None,
        *args,
        **kwargs,
    ) -> None:
        # call super class __init__
        super().__init__(*args, **settings.fastapi_kwargs)
        self.profiler = None
        self.settings = settings

        self.previous_settings = None
        self.one_time_config = False
        self.logger = logger_gruru
        self.fastApi = FastAPI
        self.daprApp = DaprApp(self)
        self.title = title if title else self.settings.title
        self.description = description if description else self.settings.description
        self.host = host if host else self.settings.host

        self.version = version if version else self.settings.version
        self.openapi_url = openapi_url if openapi_url else self.settings.openapi_url
        self.redoc_url = redoc_url if redoc_url else self.settings.redoc_url
        self.auto_mount_site: bool = auto_mount_site
        self.SDUVersion = SDUVersion(version=self.settings.version, creation_date=datetime.utcnow().isoformat())
        self.license_info = license_info
        self.contact = contact if contact else self.settings.contact
        self.terms_of_service = terms_of_service
        self.openapi_tags = openapi_tags
        self.healthdefinition: MSAHealthDefinition = self.settings.healthdefinition
        self.limiter: Optional[Limiter] = None
        self.background_scheduler: Optional[BackgroundScheduler] = None
        self.asyncio_scheduler: Optional[AsyncIOScheduler] = None
        self.site = None
        self.ROOTPATH = os.path.join(os.path.dirname(__file__))
        self.abstract_fs: Optional[MSAFilesystem] = None
        self.fs: Optional[FS] = None
        self.logger.info_pub = self.logger_info

        init_logging()
        self.add_middlewares()
        self.add_functionality()
        self.add_event_handler("shutdown", self.shutdown_event)
        self.add_event_handler("startup", self.startup_event)
        self.create_dapr_endpoint()

    def create_dapr_endpoint(self):
        """
        Subscribes service to pubsub topic through which new configs will be received.
        """

        @self.daprApp.subscribe(pubsub=PUBSUB_NAME, topic=SERVICE_TOPIC)
        async def read_config(received_config: ConfigInput) -> None:
            """
            Receives new config and updates current settings with received data.

            Parameters:
                received_config: Data to update current config with.
            """
            try:
                self.logger.info(f"Received config from svcRegistry. Data: {received_config.data}")
                if received_config.data.config.name == self.settings.name:
                    reload_needed = self.update_settings(received_config.data.config, received_config.data.one_time)
                    if reload_needed:
                        self.logger.info("New config needs reload.")
                        with open("config.json", "w") as json_file:
                            json.dump(received_config.data.dict(), json_file)

                        self.logger.info("New config saved to config.json")

            except Exception as ex:
                self.logger.info(ex)

    @staticmethod
    def uses_temporary_config(function):
        """
        Makes an endpoint use one-time config whenever it is present.

        Parameters:
            function: an endpoint to wrap
        """

        @wraps(function)
        def decorator(self, *args, **kwargs):
            result = function(self, *args, **kwargs)
            if self.one_time_config:
                self.logger.info("One-time config used. Loading previous config...")
                self.update_settings(self.previous_settings)

                self.previous_settings = None
                self.one_time_config = False
            return result

        return decorator

    def model_block(self, func):
        """
        Block ML model while data in process.

        Parameters:
            func: an endpoint to wrap
        """

        @wraps(func)
        def decorator(*args, **kwargs):
            if not self.state.blocker.check_ml_model_availability():
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="The ML model is busy processing data and is not available at the moment."
                    "Please try later.",
                )
            try:
                self.state.blocker.set_ml_model_unavailable()
                return func(*args, **kwargs)
            except Exception as ex:
                raise ex
            finally:
                self.state.blocker.set_ml_model_available()

        return decorator

    def logger_info(self, message: str, service_name: str = "", topic_name: str = "") -> None:
        """
        Sends message to pubsub topic.

        Parameters:
            message: JSON message to send.
            topic_name: name of pubsub topic that needs this message.
            service_name: the name of the service from which the call was made
        """
        if topic_name:
            try:
                with DaprClient() as client:
                    client.publish_event(
                        pubsub_name=PUBSUB_NAME,
                        topic_name=topic_name,
                        data=f"[{service_name}]: " + message if service_name else message,
                        data_content_type="application/json",
                    )
            except (_InactiveRpcError, DaprInternalError):
                self.logger.info("Dapr is not available, switching to default logger")
        self.logger.info(message)

    async def extend_startup_event(self) -> None:
        """You can extend the main shutdown"""

    async def startup_event(self) -> None:
        """Internal Startup Event Handler"""
        self.logger.info("msaBase Internal Startup MSAUIEvent")
        await self.extend_startup_event()

    async def extend_shutdown_event(self) -> None:
        """You can extend the main shutdown"""

    async def shutdown_event(self) -> None:
        """Internal Shutdown event handler"""
        self.logger.info("msaBase Internal Shutdown MSAUIEvent")
        await self.extend_shutdown_event()

        self.stop_scheduler(self.background_scheduler, "Background")
        self.stop_scheduler(self.asyncio_scheduler, "Asyncio")

        if self.settings.abstract_fs:
            try:
                self.logger.info("Closing Abstract Filesystem")
                self.fs.close()
            except Exception as ex:
                getMSABaseExceptionHandler().handle(ex, "Error: Closing Abstract Filesystem failed:")

    def stop_scheduler(self, scheduler: Union[None, AsyncIOScheduler, BackgroundScheduler], name: str) -> None:
        if scheduler:
            self.logger.info(f"Stop {name} Scheduler")
            if scheduler.get_jobs():
                scheduler.shutdown()
            if isinstance(scheduler, AsyncIOScheduler):
                self.asyncio_scheduler = None
            else:
                self.background_scheduler = None

    async def get_system_info(self) -> MSASystemInfo:
        """Get System Nvidia GPU's Info
        Returns:
            sys_info: MSASystemGPUInfo Pydantic Model
        """
        sys_info = get_sysinfo(f"{self.settings.name} {self.settings.version}")
        return sys_info

    async def get_system_gpu_info(self) -> MSASystemGPUInfo:
        """Get System Nvidia GPU's Info
        Returns:
            sys_gpu_info: MSASystemGPUInfo Pydantic Model
        """
        sys_gpu_info = get_sysgpuinfo(f"{self.settings.name} {self.settings.version}")
        return sys_gpu_info

    @staticmethod
    async def get_healthcheck() -> int:
        """
        Get Healthcheck Status
        """
        return status.HTTP_200_OK

    async def get_scheduler_status(self, request: Request) -> MSASchedulerStatus:
        """
        Get Service Scheduler Status, with the registered Task's

        Args:
            request: The input http request object

        Returns:
            sst: MSASchedulerStatus Pydantic Response Model

        """
        self.logger.info("Called - get_scheduler_status :" + str(request.url))
        sst: MSASchedulerStatus = MSASchedulerStatus()
        if not self.settings.background_scheduler or not self.settings.asyncio_scheduler:
            sst.name = self.settings.name
            sst.message = "Schedulers is disabled!"

        else:
            sst.name = self.settings.name
            for task in self.background_scheduler.get_jobs():
                nt: MSASchedulerTaskStatus = MSASchedulerTaskStatus()
                nt.name = task.name
                nt.detail = MSASchedulerTaskDetail.parse_obj(task)
                sst.tasks.append(nt)
            for task in self.asyncio_scheduler.get_jobs():
                nt: MSASchedulerTaskStatus = MSASchedulerTaskStatus()
                nt.name = task.name
                nt.detail = MSASchedulerTaskDetail.parse_obj(task)
                sst.tasks.append(nt)
            sst.message = "Scheduler is enabled!"

        return sst

    async def get_services_status(self, request: Request) -> MSAServiceStatus:
        """
        Get Service Status Info

        Args:
            request: The input http request object

        Returns:
            sst: MSAServiceStatus Pydantic Response Model

        """
        self.logger.info("Called - get_services_status :" + str(request.url))
        sst: MSAServiceStatus = MSAServiceStatus()
        if not self.settings.healthdefinition.enabled:
            sst.name = self.settings.name
            sst.healthy = "disabled:400"
            sst.message = "Healthcheck is disabled!"

        else:
            sst.name = self.settings.name
            sst.healthy = await self.get_healthcheck()
            sst.message = "Healthcheck is enabled!"

        return sst

    def get_services_settings(self, request: Request) -> ORJSONResponse:
        """
        Get Service OpenAPI Schema

        Args:
            request: The input http request object

        Returns:
            settings: ORJSONResponse

        """
        self.logger.info("Called - get_services_settings :" + str(request.url))

        def try_get_json():
            try:

                return jsonable_encoder(self.settings)

            except Exception as e:
                return {"status": "error:400", "error": e.__str__()}

        return ORJSONResponse(
            {
                self.settings.name: try_get_json(),
            }
        )

    def get_services_openapi_schema(self, request: Request) -> ORJSONResponse:
        """
        Get Service OpenAPI Schema

        Parameters:
            request: The input http request object

        Returns:
            ORJSONResponse openapi schema
        """
        self.logger.info("Called - get_services_openapi_schema :" + str(request.url))

        def try_get_json():
            try:

                return jsonable_encoder(self.openapi())

            except Exception as e:
                return {"status": "error:400", "error": e.__str__()}

        return ORJSONResponse(
            {
                self.settings.name: try_get_json(),
            }
        )

    async def msa_exception_handler(self, request: Request, exc: HTTPException) -> Response:
        """
        Handles all HTTPExceptions if enabled with HTML
        Response or forward error if the code is in the exclude settings list.

        Parameters:
            request: The input http request object
            exc : The HTTPException instance

        Returns:
            HTTPResponse: response with status code corresponding to the handled exception.
        """
        error_content = {
            "request": request.__dict__,
            "detail": exc.detail,
            "status": exc.status_code,
            "definitions": jsonable_encoder(self.settings),
        }
        if exc.status_code not in self.settings.httpception_exclude:
            sentry_sdk.capture_exception(exc)
        self.logger.error("msa_exception_handler - " + str(error_content))
        return await http_exception_handler(request, exc)

    def get_sduversion(self) -> SDUVersion:
        """
        Get SDUVersion

        Returns:
            sdu_version: Pydantic Version Info Model.
        """
        return self.SDUVersion

    def get_services_openapi_info(self, request: Request) -> MSAOpenAPIInfo:
        """
        Get Service OpenAPI Info

        Args:
            request: The input http request object

        Returns:
            oai: MSAOpenAPIInfo Paydantic Response Model

        """
        self.logger.info("Called - get_services_openapi_info :" + str(request.url))
        oai: MSAOpenAPIInfo = MSAOpenAPIInfo()

        try:
            oai.name = self.title
            oai.version = self.openapi_version
            oai.url = self.openapi_url
            oai.tags = self.openapi_tags
        except Exception as e:
            oai.tags = ["error:400 error" + e.__str__()]

        return oai

    def get_profiler(self, request: Request) -> HTMLResponse:
        """
        Get Profiler

        Parameters:
            request: The input http request object

        Returns:
            HTMLResponse: response with html code of profiler
        """
        self.profiler.start()
        self.profiler.stop()
        html = self.profiler.output_html()
        service_name = f"Profiler for {self.settings.name} {self.settings.version} was disabled"
        html_code = html.replace("pyinstrument", service_name).replace("Pyinstrument", service_name)
        return HTMLResponse(html_code)

    async def validation_exception_handler(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handles validation error exception and returns exception info as a JSON.

        Parameters:
            request: Request that raised the exception
            exc: exception to handle
        Returns:
            response: JSONResponse that represents the exception
        """
        self.logger.error("validation_exception_handler - " + str(exc.errors()))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    async def msa_exception_handler_disabled(self, request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handles all HTTPExceptions if Disabled with JSON Response.

        Args:
            request: The input http request object
            exc: exception to handle

        Returns:
            HTTPException: as JSONResponse

        """

        error_content = jsonable_encoder(
            {
                "status_code": exc.status_code,
                "detail": exc.detail,
                "args": exc.args,
                "headers": exc.headers,
                "request": request.url,
            }
        )
        self.logger.error("msa_exception_handler_disabled - " + str(error_content))
        return JSONResponse(
            status_code=exc.status_code,
            content=error_content,
        )

    def add_middlewares(self) -> None:
        """
        Add Middleware, by values in Settings
        """
        for middleware in MiddlewareTypes:
            try:
                status_middleware = getattr(self.settings, middleware.name, None)
                if status_middleware:
                    self.choose_middleware_configurator(middleware)()
                else:
                    self.logger.info(f"Excluded {middleware.readable_name}")
            except Exception as ex:
                getMSABaseExceptionHandler().handle(ex)

    def add_functionality(self) -> None:
        """
        Add Functionality, by values in Settings
        """
        for functionality in FunctionalityTypes:
            try:
                status_middleware = getattr(self.settings, functionality.name, None)
                if status_middleware:
                    self.choose_functionality_configurator(functionality)()
                else:
                    self.logger.info(f"Excluded {functionality.readable_name}")
            except Exception as ex:
                getMSABaseExceptionHandler().handle(ex)

    def update_settings(self, new_config: MSAServiceDefinition, one_time=False) -> bool:
        """
        Updates app configuration.

        Parameters:
            new_config: MSAServiceDefinition. Config received from svcRegistry.
            one_time: a flag for using the config only one time.
        Returns:
            bool. True if app reload is needed, False otherwise.
        """
        if one_time:
            self.previous_settings = self.settings

        for middleware in MiddlewareTypes:
            current_middleware = getattr(self.settings, middleware.name, None)

            new_middleware = getattr(new_config, middleware.name, None)

            if (current_middleware is not None and new_middleware is not None) and (
                current_middleware != new_middleware
            ):
                return True

        for functionality in FunctionalityTypes:
            current_functionality = getattr(self.settings, functionality.name, None)

            new_functionality = getattr(new_config, functionality.name, None)
            reload_needed = functionality.need_restart

            if (current_functionality is not None and new_functionality is not None) and (
                current_functionality != new_functionality
            ):

                if reload_needed:
                    return True

                setattr(self.settings, functionality.name, new_functionality)
                self.choose_functionality_configurator(functionality)()

        return False

    def unknown_middleware(self) -> None:
        """
        Unknown Middleware, doing nothing
        """
        self.logger.info("Unknown Middleware")

    def unknown_functionality(self) -> None:
        """
        Unknown Functionality, doing  nothing
        """
        self.logger.info("Unknown Functionality")

    def choose_middleware_configurator(
        self, middleware: Union[MiddlewareTypes, FunctionalityTypes]
    ) -> Type[unknown_middleware]:
        """
        Get the configurator by type of Middleware

        Returns:
            func: The configurator.
        """
        configurator_mappings = {
            MiddlewareTypes.profiler: self.configure_profiler_middleware,
            MiddlewareTypes.validationception: self.configure_validation_handler,
            MiddlewareTypes.httpception: self.configure_httpexception_handler,
            MiddlewareTypes.starception: self.configure_starception_middleware,
            MiddlewareTypes.cors: self.configure_cors_middleware,
            MiddlewareTypes.httpsredirect: self.configure_httpsredirect_middleware,
            MiddlewareTypes.gzip: self.configure_gzip_middleware,
            MiddlewareTypes.session: self.configure_session_middleware,
            MiddlewareTypes.csrf: self.configure_csrf_middleware,
            MiddlewareTypes.msgpack: self.configure_msgpack_middleware,
            MiddlewareTypes.context: self.configure_context_middleware,
            MiddlewareTypes.timing: self.configure_timing_middleware,
            MiddlewareTypes.limiter: self.configure_limiter_handler,
        }
        return configurator_mappings.get(middleware, self.unknown_middleware)

    def choose_functionality_configurator(self, middleware: FunctionalityTypes) -> Type[unknown_functionality]:
        """
        Get the configurator by type of Functionality

        Returns:
            func: The configurator.
        """
        configurator_mappings = {
            FunctionalityTypes.uvloop: self.configure_event_loop,
            FunctionalityTypes.healthdefinition: self.configure_healthdefinition,
            FunctionalityTypes.servicerouter: self.configure_servicerouter,
            FunctionalityTypes.instrument: self.configure_prometheus_instrument,
            FunctionalityTypes.background_scheduler: self.configure_background_scheduler,
            FunctionalityTypes.asyncio_scheduler: self.configure_asyncio_scheduler,
            FunctionalityTypes.abstract_fs: self.configure_abstract_fs,
        }
        return configurator_mappings.get(middleware, self.unknown_middleware)

    def configure_starception_middleware(self) -> None:
        """Add Middleware Starception"""
        self.logger.info("Add Middleware Starception")
        from starception import StarceptionMiddleware

        self.add_middleware(StarceptionMiddleware)

    def configure_servicerouter(self) -> None:
        """Add service routers"""
        self.logger.info("Include Servicerouter")
        if self.settings.background_scheduler or self.settings.asyncio_scheduler:
            self.add_api_route(
                "/scheduler",
                self.get_scheduler_status,
                tags=["service"],
                response_model=MSASchedulerStatus,
            )
        self.add_api_route("/", self.get_sduversion, tags=["service"], response_model=SDUVersion)
        self.add_api_route("/sysinfo", self.get_system_info, tags=["service"], response_model=MSASystemInfo)
        self.add_api_route(
            "/sysgpuinfo",
            self.get_system_gpu_info,
            tags=["service"],
            response_model=MSASystemGPUInfo,
        )
        self.add_api_route("/settings", self.get_services_settings, tags=["service"])
        self.add_api_route(
            "/status",
            self.get_services_status,
            tags=["service"],
            response_model=MSAServiceStatus,
        )
        self.add_api_route("/schema", self.get_services_openapi_schema, tags=["openapi"])
        self.add_api_route(
            "/info",
            self.get_services_openapi_info,
            tags=["openapi"],
            response_model=MSAOpenAPIInfo,
        )
        if not self.settings.profiler:
            self.profiler = Profiler()
            self.add_api_route(
                self.settings.profiler_url, self.get_profiler, tags=["service"], response_model=MSAOpenAPIInfo
            )

    def configure_limiter_handler(self) -> None:
        """Add Limiter Handler"""
        self.logger.info("Add Limiter Handler")
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.errors import RateLimitExceeded
        from slowapi.util import get_remote_address

        self.limiter = Limiter(key_func=get_remote_address)
        self.state.limiter = self.limiter
        self.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    def configure_profiler_middleware(self) -> None:
        """Add Middleware Profiler"""
        self.logger.info("Add Middleware Profiler")
        from msaBase.profiler import MSAProfilerMiddleware

        self.add_middleware(
            MSAProfilerMiddleware,
            profiler_output_type=self.settings.profiler_output_type,
            track_each_request=self.settings.profiler_single_calls,
            msa_app=self,
        )

    def configure_httpexception_handler(self) -> None:
        """Add Handler HTTPException"""
        self.logger.info("Add Handler HTTPException")
        exception_handler = (
            self.msa_exception_handler if self.settings.httpception else self.msa_exception_handler_disabled
        )
        self.add_exception_handler(StarletteHTTPException, exception_handler)

    def configure_validation_handler(self) -> None:
        """Add Handler ValidationError"""
        self.logger.info("Add Handler ValidationError")
        self.add_exception_handler(RequestValidationError, self.validation_exception_handler)

    def configure_healthdefinition(self) -> None:
        """Configure health definition and start healthcheck thread."""
        self.logger.info("Init Healthcheck")
        if self.settings.healthdefinition.enabled:
            self.add_api_route(
                self.healthdefinition.path,
                self.get_healthcheck,
                status_code=status.HTTP_200_OK,
                tags=["service"],
            )

    def configure_abstract_fs(self) -> None:
        """Enable Abstract Filesystem"""
        self.logger.info("Enable Abstract Filesystem")
        from msaFilesystem.msafs import MSAFilesystem

        if self.settings.abstract_fs:
            try:
                self.logger.info("Closing Abstract Filesystem")
                self.fs.close()
            except Exception as ex:
                getMSABaseExceptionHandler().handle(ex, "Error: Closing Abstract Filesystem failed:")
        else:
            self.abstract_fs = MSAFilesystem(fs_url=self.settings.abstract_fs_url)
            self.fs = self.abstract_fs.fs

    def configure_msgpack_middleware(self) -> None:
        """Add Middleware MSGPack"""
        self.logger.info("Add Middleware MSGPack")
        from msgpack_asgi import MessagePackMiddleware

        self.add_middleware(MessagePackMiddleware)

    def configure_context_middleware(self) -> None:
        """Add Middleware Context"""
        self.logger.info("Add Middleware Context")
        from starlette_context.middleware import RawContextMiddleware

        self.add_middleware(
            RawContextMiddleware,
            plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
        )

    def configure_prometheus_instrument(self) -> None:
        """Add Prometheus Instrument and Expose App"""
        self.logger.info("Prometheus Instrument and Expose App")
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app=self).expose(
            app=self,
            include_in_schema=True,
            tags=["service"],
            response_class=HTMLResponse,
        )

    def configure_csrf_middleware(self) -> None:
        """Add Middleware CSRF"""
        self.logger.info("Add Middleware CSRF")
        from starlette_wtf import CSRFProtectMiddleware

        self.add_middleware(CSRFProtectMiddleware, csrf_secret=get_secret_key_csrf())

    def configure_session_middleware(self) -> None:
        """Add Middleware Session"""
        self.logger.info("Add Middleware Session")
        from starlette.middleware.sessions import SessionMiddleware

        self.add_middleware(SessionMiddleware, secret_key=get_secret_key_sessions())

    def configure_background_scheduler(self) -> None:
        """Add Background Scheduler"""
        self.logger.info("Add Background Scheduler")
        from apscheduler.schedulers.background import BackgroundScheduler

        if self.settings.background_scheduler and not self.background_scheduler:
            self.background_scheduler = BackgroundScheduler()
        elif not self.settings.background_scheduler:
            self.stop_scheduler(self.background_scheduler, "Asyncio")

    def configure_asyncio_scheduler(self) -> None:
        """Add Asyncio Scheduler"""
        self.logger.info("Add Asyncio Scheduler")
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        if self.settings.asyncio_scheduler and not self.asyncio_scheduler:
            self.asyncio_scheduler = AsyncIOScheduler()
        elif not self.settings.asyncio_scheduler:
            self.stop_scheduler(self.asyncio_scheduler, "Asyncio")

    def configure_event_loop(self) -> None:
        """Enable UVLoop"""
        self.logger.info("Enable UVLoop")
        import uvloop

        uvloop.install()

    def configure_cors_middleware(self) -> None:
        """Add Middleware CORS"""
        self.logger.info("Add Middleware CORS")
        from starlette.middleware.cors import CORSMiddleware

        self.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.allow_origins,
            allow_credentials=self.settings.allow_credentials,
            allow_methods=self.settings.allow_methods,
            allow_headers=self.settings.allow_headers,
        )

    def configure_timing_middleware(self) -> None:
        """Add Middleware Timing"""
        self.logger.info("Add Middleware Timing")
        from fastapi_utils.timing import add_timing_middleware

        add_timing_middleware(self, record=self.logger.info, prefix="app", exclude="untimed")

    def configure_gzip_middleware(self) -> None:
        """Add Middleware GZip"""
        self.logger.info("Add Middleware GZip")
        from starlette.middleware.gzip import GZipMiddleware

        self.add_middleware(GZipMiddleware)

    def configure_httpsredirect_middleware(self) -> None:
        """Add Middleware HTTPSRedirectMiddleware"""
        from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

        self.logger.info("Add Middleware HTTPSRedirect")
        self.add_middleware(HTTPSRedirectMiddleware)

    def send_config(self) -> None:
        """
        Sends current config to pubsub registry topic.
        """
        try:
            self.logger.info("Start send config to pubsub")
            with open("config.json") as json_file:
                config = MSAServiceDefinition.parse_obj(json.load(json_file))
                data = ConfigDTO(config=config, one_time=False)
            self.logger_info(data.json(), topic_name=REGISTRY_TOPIC)
            self.logger.info(f"Sent config to pubsub, {data}")
        except Exception as ex:
            self.logger.error(f"An error occurred while trying to send config to svcRegistry. Exception: {ex}")

    def info_pub_logger(self, message: str) -> None:
        """Sending progress to the topic

        Parameters:

            message: message with status
        """
        if self.settings.debug:
            self.logger.info(message)
        else:
            self.logger.info_pub(
                message,
                topic_name=PROGRESS_TOPIC,
                service_name=self.settings.name,
            )

    def init_sentry(self, sentry_dsn: str) -> None:
        """Sending progress to the topic

        Parameters:

            sentry_dsn: dsn to sentry project
        """
        if not self.settings.debug:
            sentry_sdk.init(
                dsn=sentry_dsn,
                traces_sample_rate=1.0,
                environment=os.getenv("STAGE_ENV","local"),
            )


class AvailabilityML:
    def __init__(self, app: MSAApp):
        self.in_process = False
        self._app = app

    def set_ml_model_unavailable(self) -> None:
        """
        Blocks the endpoint while data is being processed.
        """
        self.in_process = True
        self._app.info_pub_logger("The model is processing the data and is not available.")

    def set_ml_model_available(self) -> None:
        """
        Unblocks the endpoint.
        """
        self.in_process = False
        self._app.info_pub_logger("The model has finished to process the data and is available.")

    def check_ml_model_availability(self) -> bool:
        """
        Return True if service

        Returns:

            False if model is not available
        """
        return False if self.in_process else True
