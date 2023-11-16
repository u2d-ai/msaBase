import uuid

from starlette.config import Config

config = Config(".env")


STAGE_ENV = config("STAGE_ENV", default="local", cast=str)
PRODUCER_CONFIG = {
    "bootstrap.servers": config("BOOTSTRAP_SERVICE", default="localhost:9092", cast=str),
}
CONSUMER_CONFIG = {
    "bootstrap.servers": config("BOOTSTRAP_SERVICE", default="localhost:9092", cast=str),
    "group.id": config("CONSUMER_GROUP_ID", default=str(uuid.uuid4())),
    "auto.offset.reset": config("AUTO_OFFSET_RESET", default="earliest", cast=str),
}

if STAGE_ENV != "local":
    AUTH_EXTENDED_CONFIG = {
        "security.protocol": config("KAFKA_PROTOCOL", default="", cast=str),
        "sasl.mechanism": config("KAFKA_SASL_MECHANISM", default="", cast=str),
        "sasl.username": config("SASL_USERNAME", default="", cast=str),
        "sasl.password": config("SASL_PASSWORD", default="", cast=str),
    }
    PRODUCER_CONFIG.update(AUTH_EXTENDED_CONFIG)
    CONSUMER_CONFIG.update(AUTH_EXTENDED_CONFIG)


KAFKA_TIMEOUT = config("KAFKA_TIMEOUT", default=3, cast=int)
ENABLE_MESSAGE_QUEUE = config("ENABLE_MESSAGE_QUEUE", default=True, cast=bool)
SAVE_ALL_MESSAGES_IN_QUEUE = config("SAVE_ALL_MESSAGES_IN_QUEUE", default=True, cast=bool)
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
