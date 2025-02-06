from typing import Optional

from pydantic import BaseModel, Field

from ..utils import LLMRequestType

__all__ = [
    "SimConfig",
]


class LLMRequestConfig(BaseModel):
    request_type: LLMRequestType = Field(
        ..., description="The type of the request or provider"
    )
    api_key: list[str] = Field(..., description="API key for accessing the service")
    model: str = Field(..., description="The model to use")

    @classmethod
    def create(
        cls, request_type: LLMRequestType, api_key: list[str], model: str
    ) -> "LLMRequestConfig":
        return cls(request_type=request_type, api_key=api_key, model=model)


class MQTTConfig(BaseModel):
    server: str = Field(..., description="MQTT server address")
    port: int = Field(..., description="Port number for MQTT connection")
    password: Optional[str] = Field(None, description="Password for MQTT connection")
    username: Optional[str] = Field(None, description="Username for MQTT connection")

    @classmethod
    def create(
        cls,
        server: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> "MQTTConfig":
        return cls(server=server, username=username, port=port, password=password)


class SimulatorRequestConfig(BaseModel):
    task_name: str = Field("citysim", description="Name of the simulation task")
    max_day: int = Field(1000, description="Maximum number of days to simulate")
    start_step: int = Field(28800, description="Starting step of the simulation")
    total_step: int = Field(
        24 * 60 * 60 * 365, description="Total number of steps in the simulation"
    )
    log_dir: str = Field("./log", description="Directory path for saving logs")
    min_step_time: int = Field(
        1000, description="Minimum time (in seconds) between simulation steps"
    )
    primary_node_ip: str = Field(
        "localhost", description="Primary node IP address for distributed simulation"
    )

    @classmethod
    def create(
        cls,
        task_name: str = "citysim",
        max_day: int = 1000,
        start_step: int = 28800,
        total_step: int = 24 * 60 * 60 * 365,
        log_dir: str = "./log",
        min_step_time: int = 1000,
        primary_node_ip: str = "localhost",
    ) -> "SimulatorRequestConfig":
        return cls(
            task_name=task_name,
            max_day=max_day,
            start_step=start_step,
            total_step=total_step,
            log_dir=log_dir,
            min_step_time=min_step_time,
            primary_node_ip=primary_node_ip,
        )


class MapRequestConfig(BaseModel):
    file_path: str = Field(..., description="Path to the map file")

    @classmethod
    def create(cls, file_path: str) -> "MapRequestConfig":
        return cls(file_path=file_path)


class MlflowConfig(BaseModel):
    username: Optional[str] = Field(None, description="Username for MLflow")
    password: Optional[str] = Field(None, description="Password for MLflow")
    mlflow_uri: str = Field(..., description="URI for MLflow server")

    @classmethod
    def create(cls, username: str, password: str, mlflow_uri: str) -> "MlflowConfig":
        return cls(username=username, password=password, mlflow_uri=mlflow_uri)


class PostgreSQLConfig(BaseModel):
    enabled: Optional[bool] = Field(
        True, description="Whether PostgreSQL storage is enabled"
    )
    dsn: str = Field(..., description="Data source name for PostgreSQL")

    @classmethod
    def create(cls, dsn: str, enabled: bool = False) -> "PostgreSQLConfig":
        return cls(dsn=dsn, enabled=enabled)


class AvroConfig(BaseModel):
    enabled: Optional[bool] = Field(False, description="Whether Avro storage is enabled")
    path: str = Field(..., description="Avro file storage path")

    @classmethod
    def create(cls, path: Optional[str] = None, enabled: bool = False) -> "AvroConfig":
        return cls(enabled=enabled, path=path)


class MetricRequest(BaseModel):
    mlflow: Optional[MlflowConfig] = Field(None)


class SimStatus(BaseModel):
    simulator_activated: bool = False


class SimConfig(BaseModel):
    llm_request: Optional["LLMRequestConfig"] = None
    simulator_request: Optional["SimulatorRequestConfig"] = None
    mqtt: Optional["MQTTConfig"] = None
    map_request: Optional["MapRequestConfig"] = None
    metric_request: Optional[MetricRequest] = None
    pgsql: Optional["PostgreSQLConfig"] = None
    avro: Optional["AvroConfig"] = None
    simulator_server_address: Optional[str] = None
    status: Optional["SimStatus"] = SimStatus()

    @property
    def prop_llm_request(self) -> "LLMRequestConfig":
        return self.llm_request  # type:ignore

    @property
    def prop_status(self) -> "SimStatus":
        return self.status  # type:ignore

    @property
    def prop_simulator_request(self) -> "SimulatorRequestConfig":
        return self.simulator_request  # type:ignore

    @property
    def prop_mqtt(self) -> "MQTTConfig":
        return self.mqtt  # type:ignore

    @property
    def prop_map_request(self) -> "MapRequestConfig":
        return self.map_request  # type:ignore

    @property
    def prop_avro_config(self) -> "AvroConfig":
        return self.avro  # type:ignore

    @property
    def prop_postgre_sql_config(self) -> "PostgreSQLConfig":
        return self.pgsql  # type:ignore

    @property
    def prop_simulator_server_address(self) -> str:
        return self.simulator_server_address  # type:ignore

    @property
    def prop_metric_request(self) -> MetricRequest:
        return self.metric_request  # type:ignore

    def SetLLMRequest(
        self, request_type: LLMRequestType, api_key: list[str], model: str
    ) -> "SimConfig":
        self.llm_request = LLMRequestConfig.create(request_type, api_key, model)
        return self

    def SetSimulatorRequest(
        self,
        task_name: str = "citysim",
        max_day: int = 1000,
        start_step: int = 28800,
        total_step: int = 24 * 60 * 60 * 365,
        log_dir: str = "./log",
        min_step_time: int = 1000,
        primary_node_ip: str = "localhost",
    ) -> "SimConfig":
        self.simulator_request = SimulatorRequestConfig.create(
            task_name=task_name,
            max_day=max_day,
            start_step=start_step,
            total_step=total_step,
            log_dir=log_dir,
            min_step_time=min_step_time,
            primary_node_ip=primary_node_ip,
        )
        return self

    def SetMQTT(
        self,
        server: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> "SimConfig":
        self.mqtt = MQTTConfig.create(server, port, username, password)
        return self

    def SetMapRequest(self, file_path: str) -> "SimConfig":
        self.map_request = MapRequestConfig.create(file_path)
        return self

    def SetMetricRequest(
        self, username: str, password: str, mlflow_uri: str
    ) -> "SimConfig":
        self.metric_request = MetricRequest(
            mlflow=MlflowConfig.create(username, password, mlflow_uri)
        )
        return self

    def SetAvro(self, path: str, enabled: bool = False) -> "SimConfig":
        self.avro = AvroConfig.create(path, enabled)
        return self

    def SetPostgreSql(self, path: str, enabled: bool = False) -> "SimConfig":
        self.pgsql = PostgreSQLConfig.create(path, enabled)
        return self

    def SetServerAddress(self, simulator_server_address: str) -> "SimConfig":
        self.simulator_server_address = simulator_server_address
        return self

    def model_dump(self, *args, **kwargs):
        exclude_fields = {
            "status",
        }
        data = super().model_dump(*args, **kwargs)
        return {k: v for k, v in data.items() if k not in exclude_fields}


if __name__ == "__main__":
    config = (
        SimConfig()
        .SetLLMRequest("openai", "key", "model")  # type:ignore
        .SetMQTT("server", 1883, "username", "password")
        .SetMapRequest("./path/to/map")
        .SetMetricRequest("username", "password", "uri")
        .SetPostgreSql("dsn", True)
    )
    print(config.llm_request)
