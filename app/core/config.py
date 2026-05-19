# core/config.py

#region imports

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

#endregion

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file = ".env", extra = "ignore")

    # Брокер для Taskiq
    BROKER_URL: str = Field(..., env = "BROKER_URL", description = "Ссылка на брокер")
    API_URL: str = Field(..., env = "API_URL", description = "Ссылка на целевой API")
    API_TOKEN: str = Field(..., env = "API_TOKEN", description = "Токен для целевого API")

    # Логины и пароли для ЛК Билайн
    LK_FINANCE_LOGIN: str = Field(..., env = "LK_FINANCE_LOGIN", description = "Логин для ЛК Финансы")
    LK_FINANCE_PASSWORD: str = Field(..., env = "LK_FINANCE_PASSWORD", description = "Пароль для ЛК Финансы")
    
    LK_ITSK_LOGIN: str = Field(..., env = "LK_ITSK_LOGIN", description = "Логин для ЛК ИТС")
    LK_ITSK_PASSWORD: str = Field(..., env = "LK_ITSK_PASSWORD", description = "Пароль для ЛК ИТС")
    
    LK_TECHNOLOGY_LOGIN: str = Field(..., env = "LK_TECHNOLOGY_LOGIN", description = "Логин для ЛК Технология")
    LK_TECHNOLOGY_PASSWORD: str = Field(..., env = "LK_TECHNOLOGY_PASSWORD", description = "Пароль для ЛК Технология")


settings = Settings()
