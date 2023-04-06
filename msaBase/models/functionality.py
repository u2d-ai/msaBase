import enum


class FunctionalityTypes(enum.Enum):
    """
    Types of functionalities and whether they require a service reload when changed.

    Attributes:
        uvloop: UVLoop.
        servicerouter: Servicerouter.
        healthdefinition: Healthcheck.
        instrument: Prometheus Instrument and Expose.
        background_scheduler: Background Scheduler.
        asyncio_scheduler: Asyncio Scheduler
        abstract_fs: Abstract Filesystem."""

    uvloop = ("UVLoop", True)
    servicerouter = ("Servicerouter", True)
    healthdefinition = ("Healthcheck", True)
    instrument = ("Prometheus Instrument and Expose", True)
    background_scheduler = ("Background Scheduler", False)
    asyncio_scheduler = ("Asyncio Scheduler", False)
    abstract_fs = ("Abstract Filesystem", False)

    def __init__(self, readable_name: str, need_restart: bool):
        self.readable_name = readable_name
        self.need_restart = need_restart
