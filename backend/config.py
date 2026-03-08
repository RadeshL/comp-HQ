import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = "sqlite:///./comp_hq.db"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Scraping
    REQUEST_TIMEOUT: int = 10
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # Ranking
    TOP_PRODUCTS_COUNT: int = 3
    
    # File paths
    OUTPUT_DIR: str = "outputs"
    
    # Search engines/retailers to scrape
    SEARCH_SOURCES: list = [
        "amazon",
        "digikey", 
        "mouser",
        "sparkfun",
        "adafruit"
    ]

settings = Settings()
