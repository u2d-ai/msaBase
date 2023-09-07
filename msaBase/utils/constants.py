import os

SERVICE_TOPIC = "service-config"
REGISTRY_TOPIC = "registry-config"
PROGRESS_TOPIC = "progress"
DATABASE_UPDATE_TOPIC = "database-update"
PUBSUB_NAME = os.environ["DAPR_PUBSUB_COMPONENT_NAME"]

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
