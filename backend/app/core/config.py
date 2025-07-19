from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Lecture Quiz System"
    admin_email: str = "admin@example.com"
    database_url: str = "sqlite:///./lecture_quiz.db"
    openai_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()