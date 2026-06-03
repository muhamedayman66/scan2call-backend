from abc import ABC, abstractmethod


class AuthRepository(ABC):
    @abstractmethod
    async def login(self, phone: str, password: str):
        pass

    @abstractmethod
    async def register(self, **kwargs):
        pass

    @abstractmethod
    async def send_otp(self, phone: str, purpose: str):
        pass

    @abstractmethod
    async def verify_otp(self, phone: str, code: str, purpose: str):
        pass

    @abstractmethod
    async def logout(self):
        pass
