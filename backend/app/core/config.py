from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///./sdirs_dev.sqlite"

    # JWT - Generate a secure key with: python -c "import secrets; print(secrets.token_hex(32))"
    jwt_secret_key: str = ""  # REQUIRED: Set in environment variable

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # External APIs
    google_maps_api_key: str = ""
    openweathermap_api_key: str = ""

    # ThingSpeak IoT Sensors
    thingspeak_channel_id: str = ""
    thingspeak_read_key: str = ""

    # HuggingFace NLP
    hf_token: str = ""

    # Twitter API (Social Media)
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_bearer_token: str = ""

    # Firebase (FCM)
    firebase_service_account_path: Optional[str] = None

    # Twilio (SMS/Voice)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_number: Optional[str] = None

    # Admin Account (Seed)
    admin_email: str = "admin@sdirs.app"
    admin_password: str = "admin123"

    # Security
    allowed_origins: str = "http://localhost:3000,http://localhost:8081"  # Comma-separated list
    environment: str = "development"
    log_level: str = "INFO"

    # Upload settings
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "./static/uploads"

    # AI/ML
    enable_ai_verification: bool = True
    model_path: str = "./models"
    cv_model_path: str = "yolov8n.pt"
    cv_confidence_threshold: float = 0.35

    # Socket.io
    socket_cors_origin: str = "http://localhost:3000,http://localhost:8081"

    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v):
        env = os.getenv('ENVIRONMENT', 'development')
        if not v:
            if env == 'production':
                raise ValueError("JWT_SECRET_KEY must be set in production environment")
            # Generate a secure fallback key for development
            print("WARNING: JWT_SECRET_KEY is not set. Generating a temporary random key for development.")
            return secrets.token_hex(32)
        return v

    @field_validator('allowed_origins')
    @classmethod
    def validate_allowed_origins(cls, v):
        env = os.getenv('ENVIRONMENT', 'development')
        if env == 'production':
            if v == '*' or '*' in v.split(","):
                 raise ValueError("CRITICAL SECURITY ERROR: ALLOWED_ORIGINS cannot contain '*' in production.")
        return v
    
    @field_validator('socket_cors_origin')
    @classmethod
    def validate_socket_cors(cls, v):
        env = os.getenv('ENVIRONMENT', 'development')
        if env == 'production':
            if v == '*' or '*' in v.split(","):
                 raise ValueError("CRITICAL SECURITY ERROR: SOCKET_CORS_ORIGIN cannot contain '*' in production.")
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


# Create a singleton instance
settings = Settings()
