from dataclasses import dataclass, field
from typing import List
import os

@dataclass
class DatabaseConfig:
    url: str = os.getenv("DATABASE_URL", "sqlite:///konkur_bot.db")
    echo: bool = False

@dataclass
class BotConfig:
    token: str = os.getenv("BOT_TOKEN", "8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8")
    admin_id: int = int(os.getenv("ADMIN_ID", "7703677187"))
    username: str = os.getenv("BOT_USERNAME", "VACcount_bot")
    admin_ids: List[int] = field(default_factory=lambda: [7703677187])  # ✅ درست شده

@dataclass
class ServerConfig:
    port: int = int(os.getenv("PORT", "5000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"

@dataclass
class SecurityConfig:
    secret_key: str = os.getenv("SECRET_KEY", "konkur1405_super_secret_key_2024_change_in_production")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "your_32_byte_encryption_key_here_change_me")

@dataclass
class Config:
    bot: BotConfig = field(default_factory=BotConfig)  # ✅ درست شده
    database: DatabaseConfig = field(default_factory=DatabaseConfig)  # ✅ درست شده
    server: ServerConfig = field(default_factory=ServerConfig)  # ✅ درست شده
    security: SecurityConfig = field(default_factory=SecurityConfig)  # ✅ درست شده

# ایجاد instance
config = Config()
