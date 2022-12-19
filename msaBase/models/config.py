from msaBase.config import MSAServiceDefinition
from pydantic.main import BaseModel


class ConfigDTO(BaseModel):
    """
    DTO that contains needed attributes to be processed.
    Attributes:
        one_time: Flag indicating whether the configuration is applied only to one request.
        config: Service config.
    """

    one_time: bool = False
    config: MSAServiceDefinition


class ConfigInput(BaseModel):
    """
    Pydantic model to receive service configs from pub/sub.
    Attributes:
        data: Service config.
    """

    data: ConfigDTO


class ConfigDataDTO(BaseModel):
    """
    DTO that represents result of service work.
    Attributes:
        service_name: Service name to distinguish.
        config_dto: Service config.
    """

    service_name: str
    config_dto: ConfigDTO
