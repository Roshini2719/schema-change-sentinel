import os

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "schema-sentinel-demo-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./schema_sentinel.db")
    DEMO_MODE: bool = True

settings = Settings()