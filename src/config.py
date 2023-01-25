from pathlib import Path
import tempfile

import pydantic


class Settings(pydantic.BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str = "abcdef"
    ALGORITHM: str = "HS256"
    UPLOAD_STORAGE = Path(tempfile.mkdtemp())
    SUPER_ADMIN_ID: int = -1
