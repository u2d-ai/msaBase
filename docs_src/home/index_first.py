import types

import uvicorn
from msaBase.config import get_msa_app_settings
from msaBase.configurate import MSAApp

settings = get_msa_app_settings()
app = MSAApp(settings=settings)


async def extend_startup_event(self) -> None:
    self.logger.info("You can extend the main startup")


async def extend_shutdown_event(self) -> None:
    self.logger.info("You can extend the main shutdown")


app.extend_startup_event = types.MethodType(extend_startup_event, app)
app.extend_shutdown_event = types.MethodType(extend_shutdown_event, app)

if __name__ == "__main__":
    app.logger.info("Starting Services...")
    app.send_config()
    uvicorn.run(
        app,
        host=app.settings.host,
        port=app.settings.port,
    )
