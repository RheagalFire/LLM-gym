from openai import OpenAI
from gym_reader.settings import get_settings

settings = get_settings()
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
