import uuid

from starlette.config import Config

config = Config(".env")


PRODUCER_CONFIG = {
    "bootstrap.servers": config("BOOTSTRAP_SERVICE", default="localhost:9092", cast=str),
}

CONSUMER_CONFIG = {
    "bootstrap.servers": config("BOOTSTRAP_SERVICE", default="localhost:9092", cast=str),
    "group.id": config("CONSUMER_GROUP_ID", default=str(uuid.uuid4())),
    "auto.offset.reset": config("AUTO_OFFSET_RESET", default="earliest", cast=str),
}


SERVICE_TOPIC = config(
    "SERVICE_TOPIC",
    default="service-config",
)
REGISTRY_TOPIC = config(
    "REGISTRY_TOPIC",
    default="registry-config",
)
PROGRESS_TOPIC = config(
    "PROGRESS_TOPIC",
    default="progress",
)
DATABASE_UPDATE_TOPIC = config(
    "DATABASE_UPDATE_TOPIC",
    default="database-update",
)
HTTPCEPTION_EXCLUDE_STATUS_CODES = [
    300,
    301,
    302,
    303,
    304,
    305,
    306,
    307,
    308,
    400,
    401,
    402,
    403,
    404,
    405,
    406,
    407,
    408,
    409,
    410,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    418,
    421,
    422,
    423,
    424,
    425,
    426,
    427,
    428,
    429,
    431,
    451,
]
