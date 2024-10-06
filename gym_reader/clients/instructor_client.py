import instructor
from openai import OpenAI
from gym_reader.settings import get_settings

settings = get_settings()
client_instructor = instructor.from_openai(OpenAI(api_key=settings.OPENAI_API_KEY))
