from pathlib import Path
from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_mail import ConnectionConfig
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv


BASEDIR = Path().cwd() / 'core' / '.env'

load_dotenv(BASEDIR)
class Settings(BaseSettings):
    MODE: str
    
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    
    POSTGRES_DB: Union[str, None] = None
    POSTGRES_USER: Union[str, None] = None
    POSTGRES_PASSWORD: Union[str, None] = None
    
    MY_MAIL_USERNAME:str
    MY_MAIL_PASSWORD: str
    MY_MAIL_FROM: str
    
    SECRET_KEY:str
    
    REDIS_HOST:str
    REDIS_PORT:int
    
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_NODE_PORT: int
    RABBITMQ_DEFAULT_VHOST: str
    HOST_NAME_RABBIT: str
    
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_DIR: str
    LOG_FILENAME: str
    
    MEDIA:str
    
    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def REDIS_URL(self):
        redis_backend = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
        return redis_backend
    
    @property
    def RABBITMQ_URL(self):
        rabbitmq_broker = f'amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@{self.HOST_NAME_RABBIT}:{self.RABBITMQ_NODE_PORT}/{self.RABBITMQ_DEFAULT_VHOST}'
        return rabbitmq_broker
    
    @property
    def mail_conf(self):
        mail_conf = ConnectionConfig(
        MAIL_USERNAME = self.MY_MAIL_USERNAME,
        MAIL_PASSWORD =self.MY_MAIL_PASSWORD,
        MAIL_FROM = self.MY_MAIL_FROM,
        MAIL_PORT = 465,
        MAIL_SERVER = "smtp.mail.ru",
        MAIL_FROM_NAME= self.MY_MAIL_USERNAME,
        MAIL_STARTTLS = False,
        MAIL_SSL_TLS = True,
        USE_CREDENTIALS = True,
        VALIDATE_CERTS = True
        )
        return mail_conf
    
    @property
    def MEDIA_URL(self):
        return Path(self.MEDIA)
    
    model_config = SettingsConfigDict(env_file="core/.env")


settings = Settings()


templates = Jinja2Templates(directory='templates')
TemplateResponse = templates.TemplateResponse
