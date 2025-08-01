from langchain.chat_models import init_chat_model
from src.core.config import settings 


llm_model_openai41_creative = init_chat_model(
    model="gpt-4.1",
    model_provider="openai",
    temperature=0.7,
    api_key=settings.OPENAI_API_KEY,
    max_tokens=settings.MAX_TOKENS,
    max_retries=settings.MAX_RETRIES,
)