import redis
from gym_reader.settings import get_settings

settings = get_settings()


class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        self.client = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            username="default",
            password=settings.REDIS_PASSWORD,
        )

    def get_client(self):
        return self.client


redis_client = RedisClient().get_client()

if __name__ == "__main__":
    print(redis_client.get("asda"))
