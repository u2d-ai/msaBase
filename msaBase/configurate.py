# -*- coding: utf-8 -*-
"""Main Service Module for MSAApp.

Initialize with a MSAServiceDefintion Instance to control the features and functions of the MSAApp.

"""
import os
from asyncio import Task
from datetime import datetime
from typing import List, Type, Union

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from loguru import logger as logger_gruru
from msaDocModels.health import MSAHealthDefinition, MSAHealthMessage
from msaDocModels.scheduler import (
    MSASchedulerStatus,
    MSASchedulerTaskDetail,
    MSASchedulerTaskStatus,
)
from msaDocModels.sdu import SDUVersion
from msaSDK.models.openapi import MSAOpenAPIInfo
from msaSDK.models.service import MSAServiceStatus
from sqlmodel import SQLModel
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette_context import plugins

from msaBase.config import MSAServiceDefinition
from msaBase.errorhandling import getMSABaseExceptionHandler
from msaBase.logger import init_logging
from msaBase.models.functionality import FunctionalityTypes
from msaBase.models.middlewares import MiddlewareTypes
from msaBase.models.sysinfo import MSASystemInfo
from msaBase.sysinfo import get_sysinfo


def getSecretKey() -> str:
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


def getSecretKeySessions() -> str:
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


def getSecretKeyCSRF() -> str:
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


class MSAApp(FastAPI):
    """Creates an application msaSDK instance.

    Note:
        As with FastApi the MSAApp provides two events:
        ``startup``: A list of callables to run on application startup. Startup handler callables do not take any arguments, and may be be either standard functions, or async functions.
        ``shutdown``: A list of callables to run on application shutdown. Shutdown handler callables do not take any arguments, and may be be either standard functions, or async functions.
        Those are also used internally, which are triggered before the external events.

        Do not include the `self` parameter in the ``Args`` section.

    Args:
        settings: MSAServiceDefinition (Must be provided), instance of a service definition with all settings
        sql_models: List of SQLModel Default None, provide list of your SQLModel Classes and the instance can create CRUD API and if site is enabled also UI for CRUD
        auto_mount_site: Default True, if site is enabled in settings and this is true, mounts the site in internal startup event.

    Attributes:
        logger: loguru logger instance
        auto_mount_site: bool auto_mount_site
        settings: MSAServiceDefinition settings instance.
        healthdefinition: MSAHealthDefinition settings.healthdefinition
        limiter: Limiter = None
        db_engine: AsyncEngine = Db Engine instance
        sql_models: List[SQLModel] = sql_models
        sql_cruds: List[MSASQLModelCrud] = []
        scheduler: MSAScheduler = None
        scheduler_task: The Task instance that runs the Scheduler in the Background
        ROOTPATH: str os.path.join(os.path.dirname(__file__))

    """

    def __init__(
        self,
        settings: MSAServiceDefinition,
        sql_models: List[SQLModel] = None,
        auto_mount_site: bool = True,
        *args,
        **kwargs,
    ) -> None:
        # call super class __init__
        super().__init__(*args, **settings.fastapi_kwargs)

        self.logger = logger_gruru
        init_logging()

        self.auto_mount_site: bool = auto_mount_site
        self.settings = settings
        self.SDUVersion = SDUVersion(
            version=self.settings.version, creation_date=datetime.utcnow().isoformat()
        )
        self.healthdefinition: MSAHealthDefinition = self.settings.healthdefinition
        self.limiter: "Limiter" = None
        self.sqlite_db_engine: "AsyncEngine" = None
        self.json_db_engine: "TinyDB" = None
        self.sql_models: List[SQLModel] = sql_models
        self.sql_cruds: List["MSASQLModelCrud"] = []
        self.background_scheduler: "BackgroundScheduler" = None
        self.asyncio_scheduler: "AsyncIOScheduler" = None
        self.site = None
        self._scheduler_task: Task = None
        self.ROOTPATH = os.path.join(os.path.dirname(__file__))
        self.abstract_fs: "MSAFilesystem" = None
        self.fs: "FS" = None
        self.healthcheck: "health.MSAHealthCheck" = None

        init_logging()
        self.add_middlewares()
        self.add_functionality()

        self.logger.info("Events - Add Internal Handlers")
        self.add_event_handler("shutdown", self.shutdown_event)
        self.add_event_handler("startup", self.startup_event)

    async def extend_startup_event(self) -> None:
        """You can extend the main shutdown"""

    async def startup_event(self) -> None:
        """Internal Startup Event Handler"""
        self.logger.info("msaSDK Internal Startup MSAUIEvent")
        await self.extend_startup_event()

        if self.settings.sqlite_db:
            async with self.sqlite_db_engine.begin() as conn:
                if self.settings.sqlite_db_meta_drop:
                    self.logger.info(
                        "SQLite DB - Drop Meta All: " + self.settings.sqlite_db_url
                    )
                    await conn.run_sync(SQLModel.metadata.drop_all)
                if self.settings.sqlite_db_meta_create:
                    self.logger.info(
                        "SQLite DB - Create Meta All: " + self.settings.sqlite_db_url
                    )
                    await conn.run_sync(SQLModel.metadata.create_all)
            await self.sqlite_db_engine.dispose()

    async def extend_shutdown_event(self) -> None:
        """You can extend the main shutdown"""

    async def shutdown_event(self) -> None:
        """Internal Shutdown event handler"""
        self.logger.info("msaSDK Internal Shutdown MSAUIEvent")
        await self.extend_shutdown_event()

        if self.settings.background_scheduler:
            self.logger.info("Stop Background Scheduler")
            self.background_scheduler.shutdown()

        if self.settings.asyncio_scheduler:
            self.logger.info("Stop Asyncio Scheduler")
            self.asyncio_scheduler.shutdown()

        if self.healthcheck:
            self.logger.info("Stopping Healthcheck Thread")
            await self.healthcheck.stop()
            self.healthcheck = None

        if self.settings.abstract_fs:
            try:
                self.logger.info("Closing Abstract Filesystem")
                self.fs.close()
            except Exception as ex:
                getMSABaseExceptionHandler().handle(
                    ex, "Error: Closing Abstract Filesystem failed:"
                )

        if self.settings.json_db:
            self.logger.info("JSON DB - Close: " + self.settings.sqlite_db_url)
            self.json_db_engine.close()

        if self.settings.sqlite_db:
            self.logger.info(
                "SQLite DB - Dispose Connections: " + self.settings.sqlite_db_url
            )
            await self.sqlite_db_engine.dispose()

    async def init_graphql(self, strawberry_schema) -> None:
        """
        Internal helper function to initialize the graphql router
        """
        if self.settings.graphql:
            from strawberry.fastapi import GraphQLRouter

            self.graphql_schema = strawberry_schema
            self.graphql_app = GraphQLRouter(self.graphql_schema, graphiql=True)
            self.include_router(self.graphql_app, prefix="/graphql", tags=["graphql"])

    async def get_healthcheck(self, request: Request) -> ORJSONResponse:
        """
        Get Healthcheck Status
        """
        self.logger.info("Called - get_healthcheck :" + str(request.url))
        msg: MSAHealthMessage = MSAHealthMessage()
        if not self.healthcheck:
            msg.message = "Healthcheck is disabled!"
        else:
            msg.healthy = self.healthcheck.is_healthy
            msg.message = await self.healthcheck.get_health()
            if len(self.healthcheck.error) > 0:
                msg.error = self.healthcheck.error

        return ORJSONResponse(content=jsonable_encoder(msg))

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
        if (
            not self.settings.background_scheduler
            or not self.settings.asyncio_scheduler
        ):
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
        if not self.healthcheck:
            sst.name = self.settings.name
            sst.healthy = "disabled:400"
            sst.message = "Healthcheck is disabled!"

        else:
            sst.name = self.settings.name
            sst.healthy = await self.healthcheck.get_health()
            sst.message = "Healthcheck is enabled!"

        return sst

    def get_services_definition(self, request: Request) -> MSAServiceDefinition:
        """
        Get Service Definition Info

        Args:
            request: The input http request object

        Returns:
            settings: MSAServiceDefinition Pydantic Response Model

        """
        self.logger.info("Called - get_services_definition :" + str(request.url))
        return self.settings

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

        Args:
            request: The input http request object

        Returns:
            openapi: ORJSONResponse openapi schema


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

    async def msa_exception_handler(
        self, request: Request, exc: HTTPException
    ) -> Response:
        """
        Handles all HTTPExceptions if enabled with HTML Response or forward error if the code is in the exclude settings list.

        Args:
            request: The input http request object
            exc : The HTTPException instance

        Returns:
            HTTPException

        """
        error_content = {
            "request": request.__dict__,
            "detail": exc.detail,
            "status": exc.status_code,
            "definitions": jsonable_encoder(self.settings),
        }
        self.logger.error("msa_exception_handler - " + str(error_content))
        return await http_exception_handler(request, exc)

    def get_sduversion(self) -> SDUVersion:
        """Get SDUVersion
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

    async def validation_exception_handler(
        self, request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        self.logger.error("validation_exception_handler - " + str(exc.errors()))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    async def msa_exception_handler_disabled(
        self, request: Request, exc: HTTPException
    ) -> JSONResponse:
        """
        Handles all HTTPExceptions if Disabled with JSON Response.

        Args:
            request: The input http request object

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

    def choose_functionality_configurator(
        self, middleware: FunctionalityTypes
    ) -> Type[unknown_functionality]:
        """
        Get the configurator by type of Functionality

        Returns:
            func: The configurator.

        """
        configurator_mappings = {
            FunctionalityTypes.uvloop: self.configure_event_loop,
            FunctionalityTypes.json_db: self.configure_json_db,
            FunctionalityTypes.sqlite_db: self.configure_sqlite_db,
            FunctionalityTypes.graphql: self.configure_graphql,
            FunctionalityTypes.healthdefinition: self.configure_healthdefinition,
            FunctionalityTypes.sysrouter: self.configure_sysrouter,
            FunctionalityTypes.servicerouter: self.configure_servicerouter,
            FunctionalityTypes.instrument: self.configure_prometheus_instrument,
            FunctionalityTypes.background_scheduler: self.configure_background_scheduler,
            FunctionalityTypes.asyncio_scheduler: self.configure_asyncio_scheduler,
            FunctionalityTypes.abstract_fs: self.configure_abstract_fs,
        }
        return configurator_mappings.get(middleware, self.unknown_middleware)

    def configure_json_db(self) -> None:
        """Create JSON DB"""
        self.logger.info("JSON DB - Init: " + self.settings.sqlite_db_url)
        from tinydb import TinyDB
        from tinydb.storages import MemoryStorage

        if self.settings.json_db_memory_only:
            self.json_db_engine = TinyDB(
                self.settings.json_db_url, storage=MemoryStorage
            )
        else:
            self.json_db_engine = TinyDB(
                self.settings.json_db_url, storage=TinyDB.default_storage_class
            )

    def configure_graphql(self) -> None:
        """Init Graphql"""
        self.logger.info("Init Graphql")
        from strawberry import schema
        from strawberry.fastapi import GraphQLRouter

        self.graphql_app: GraphQLRouter = None
        self.graphql_schema: schema = None

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
        self.add_api_route(
            "/status",
            self.get_services_status,
            tags=["service"],
            response_model=MSAServiceStatus,
        )
        self.add_api_route(
            "/definition",
            self.get_services_definition,
            tags=["service"],
            response_model=MSAServiceDefinition,
        )
        self.add_api_route(
            "/sys_info", get_sysinfo, tags=["service"], response_model=MSASystemInfo
        )
        self.add_api_route(
            "/", self.get_sduversion, tags=["service"], response_model=SDUVersion
        )
        self.add_api_route("/settings", self.get_services_settings, tags=["service"])
        self.add_api_route(
            "/schema", self.get_services_openapi_schema, tags=["openapi"]
        )
        self.add_api_route(
            "/info",
            self.get_services_openapi_info,
            tags=["openapi"],
            response_model=MSAOpenAPIInfo,
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
            self.msa_exception_handler
            if self.settings.httpception
            else self.msa_exception_handler_disabled
        )
        self.add_exception_handler(StarletteHTTPException, exception_handler)

    def configure_validation_handler(self) -> None:
        """Add Handler ValidationError"""
        self.logger.info("Add Handler ValidationError")
        self.add_exception_handler(
            RequestValidationError, self.validation_exception_handler
        )

    def configure_sqlite_db(self) -> None:
        """Create sqlite db connection and create crud in db by sql_model in Settings"""
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import DeclarativeMeta

        self.logger.info("SQLite DB - Init: " + self.settings.sqlite_db_url)
        self.Base: DeclarativeMeta = declarative_base()
        self.sqlite_db_engine = create_async_engine(
            self.settings.sqlite_db_url,
            echo=self.settings.sqlite_db_debug,
            future=True,
        )
        if self.settings.sqlite_db_crud and self.sql_models:
            self.configure_db_crud()

    def configure_db_crud(self) -> None:
        """Register all Models and the crud for them"""
        if self.settings.sqlite_db_crud and self.sql_models:
            self.logger.info(
                "SQLite DB - Register/CRUD SQL Models: " + str(self.sql_models)
            )
            from msaCRUD import MSASQLModelCrud

            for model in self.sql_models:
                new_crud: MSASQLModelCrud = MSASQLModelCrud(
                    model=model, engine=self.sqlite_db_engine
                ).register_crud()
                if self.settings.sqlite_db_crud:
                    self.include_router(new_crud.router)
                self.sql_cruds.append(new_crud)

    def configure_healthdefinition(self) -> None:
        self.logger.info("Init Healthcheck")
        from msaBase.healthcheck import MSAHealthCheck

        self.healthcheck = MSAHealthCheck(
            healthdefinition=self.healthdefinition,
            host=self.settings.host,
            port=self.settings.port,
        )
        self.logger.info("Start Healthcheck Thread")
        self.healthcheck.start()
        self.add_api_route(
            self.healthdefinition.path,
            self.get_healthcheck,
            response_model=MSAHealthMessage,
            tags=["service"],
        )

    def configure_sysrouter(self) -> None:
        """Enable Sysrouter"""
        self.logger.info("Include Sysrouter")
        from msaSDK.router.system import sys_router

        self.include_router(sys_router)

    def configure_abstract_fs(self) -> None:
        """Enable Abstract Filesystem"""
        self.logger.info("Enable Abstract Filesystem")
        from msaFilesystem.msafs import MSAFilesystem

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

        self.add_middleware(CSRFProtectMiddleware, csrf_secret=getSecretKeyCSRF())

    def configure_session_middleware(self) -> None:
        """Add Middleware Session"""
        self.logger.info("Add Middleware Session")
        from starlette.middleware.sessions import SessionMiddleware

        self.add_middleware(SessionMiddleware, secret_key=getSecretKeySessions())

    def configure_background_scheduler(self) -> None:
        """Add Background Scheduler"""
        self.logger.info("Add Background Scheduler")
        from apscheduler.schedulers.background import BackgroundScheduler

        self.background_scheduler = BackgroundScheduler()
        self.background_scheduler.start()

    def configure_asyncio_scheduler(self) -> None:
        """Add Asyncio Scheduler"""
        self.logger.info("Add Asyncio Scheduler")
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        self.asyncio_scheduler = AsyncIOScheduler()
        self.asyncio_scheduler.start()

    def configure_event_loop(self) -> None:
        """Enable UVLoop"""
        self.logger.info("Enable UVLoop")
        import uvloop

        uvloop.install()

    def configure_cors_middleware(self) -> None:
        """ "Add Middleware CORS"""
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

        add_timing_middleware(
            self, record=self.logger.info, prefix="app", exclude="untimed"
        )

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
