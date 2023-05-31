# -*- coding: utf-8 -*-

from threading import Timer

import httpx
from msaDocModels.health import MSAHealthDefinition
from starlette import status


class MSAHealthCheck:
    def __init__(self, healthdefinition: MSAHealthDefinition, host: str, port: int):
        """MSAHealthCheckObject, provides a thread to give a healthcheck.

        Parameters:
            healthdefinition: The MSAHealthDefinition instance
            host: IP/URl to call the healtcheck endpoint
            port: Port of the healtcheck endpoint server listener/endpoint
        """
        super().__init__()
        self.url = "http://{}:{}/".format(host, port)
        self._is_running = True
        self.healthy: str = "No Healthcheck executed yet:400"
        self.is_healthy: bool = False
        self.error: str = ""
        self.status = status.HTTP_200_OK
        self.timer = Timer(healthdefinition.interval, self.run)

    async def get_health(self) -> str:
        """
        Get the last health check result

        Returns:
            string "positiv: status_code" or "negative: status_code"
        """
        return self.healthy

    async def get_status(self) -> str:
        """
        Get the status code of check result

        Returns:
            status code
        """
        return self.status

    def start(self):
        self.timer.start()

    def run(self):
        """
        Run the Healthcheck Thread

        Sleeps by the interval provided by the MSAHealthDefinition.

        Uses httpx to call the healthcheck endpoint which is http://{}:{}/".format(host, port)

        Any 200 <= response.status_code < 300 is healthy, rest is not healthy
        """
        try:
            self.error = ""
            resp = httpx.get(url=self.url, timeout=3.0)
            if status.HTTP_200_OK <= resp.status_code < status.HTTP_300_MULTIPLE_CHOICES:
                self.is_healthy = True
                self.status = status.HTTP_200_OK
            else:
                self.is_healthy = False
                self.status = status.HTTP_503_SERVICE_UNAVAILABLE
        except Exception as e:
            self.status = status.HTTP_503_SERVICE_UNAVAILABLE
            self.is_healthy = False
            self.error = e.__str__()

        self.healthy = (
            "positiv:" + str(self.status) if (200 <= self.status < 300) else "negativ:" + str(self.status)
        )

    def stop(self):
        """Stops the Healthcheck Thread."""
        self.timer.cancel()
