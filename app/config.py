from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    data_dir: str = "./data"
    chroma_collection: str = "documents"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 4

    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    refusal_message: str = "I can't answer that from the provided documents."


settings = Settings()
