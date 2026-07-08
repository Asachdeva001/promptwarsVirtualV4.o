import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "StadiumOS"
    API_V1_STR: str = "/api"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    STADIUM_CAPACITY: int = 80000
    
    # Grid sizes for simulated map coordinates (100x100 stadium layout)
    STADIUM_WIDTH: int = 100
    STADIUM_HEIGHT: int = 100

settings = Settings()
