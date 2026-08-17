from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    @property
    def database_url(self):
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @database_url.setter
    def database_url(self, url: str):
        scheme, rest = url.split("://")
        creds, host_db = rest.split("@")
        user, password = creds.split(":")
        host_port, db_name = host_db.split("/")
        host, port = host_port.split(":")
        self.db_user = user
        self.db_password = password
        self.db_host = host
        self.db_port = int(port)
        self.db_name = db_name


settings = Settings()  # type: ignore
