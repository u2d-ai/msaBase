import types

import uvicorn
from loguru import logger
from msaBase.config import get_msa_app_settings
from msaBase.configurate import MSAApp

setting = get_msa_app_settings()
app = MSAApp(settings=setting)


async def extend_startup_event(self) -> None:
    self.logger.info("You can extend the main startup")


async def extend_shutdown_event(self) -> None:
    self.logger.info("You can extend the main shutdown")


app.extend_startup_event = types.MethodType(extend_startup_event, app)
app.extend_shutdown_event = types.MethodType(extend_shutdown_event, app)

if __name__ == "__main__":
    logger.info("Starting Services...")
    uvicorn.run(
        app,
        host=app.settings.host,
        port=app.settings.port,
    )
