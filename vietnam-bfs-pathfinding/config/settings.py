import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

# class config cơ bản cho FastApi
class Settings(BaseSettings):

    # Application settings
    debug: bool = Field(default=True, description="Enable debug mode")
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )

    api_port: int = Field(
        default=8000,
        description="API server port"
    )
    
    # Data settings
    data_path: str = Field(
        default="./data",
        description="Path to data directory"
    )
    provinces_file: str = Field(
        default="provinces.json",
        description="Provinces data filename"
    )
    adjacency_file: str = Field(
        default="adjacency.json",
        description="Adjacency data filename"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_provinces_path(self) -> str:
        return os.path.join(self.data_path, self.provinces_file)
    
    def get_adjacency_path(self) -> str:
        return os.path.join(self.data_path, self.adjacency_file)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
