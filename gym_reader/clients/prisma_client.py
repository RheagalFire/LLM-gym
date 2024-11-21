import threading
from prisma import Prisma


class PrismaClient:
    _instance = None
    _lock = threading.Lock()
    _connected = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.client = Prisma()
        return cls._instance

    async def get_client(self):
        if not self._connected:
            await self.client.connect()
            self._connected = True
        return self.client

    async def disconnect(self):
        if self._connected:
            await self.client.disconnect()
            self._connected = False


prisma_singleton = PrismaClient()
