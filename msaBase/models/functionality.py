import enum


class FunctionalityTypes(enum.Enum):
    uvloop = ("UVLoop", True)
    """UVLoop."""
    json_db = ("JSON DB", False)
    """JSON DB."""
    sqlite_db = ("SQLiteDB", False)
    """SQLiteDB"""
    graphql = ("Graphql", True)
    """Graphql."""
    sysrouter = ("Sysrouter", True)
    """Sysrouter."""
    servicerouter = ("Servicerouter", True)
    """Servicerouter."""
    healthdefinition = ("Healthcheck", True)
    """Healthcheck."""
    instrument = ("Prometheus Instrument and Expose", True)
    """Prometheus Instrument and Expose."""
    background_scheduler = ("Asyncio Scheduler", False)
    """Asyncio Scheduler"""
    asyncio_scheduler = ("Background Scheduler", False)
    "Background Scheduler"
    abstract_fs = ("Abstract Filesystem", False)
    """Abstract Filesystem."""

    def __init__(self, readable_name: str, need_restart: bool):
        self.readable_name = readable_name
        self.need_restart = need_restart
