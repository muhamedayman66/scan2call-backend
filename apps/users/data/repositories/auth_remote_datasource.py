from abc import ABC, abstractmethod


class AuthRemoteDataSource(ABC):
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


class AuthRemoteDataSourceImpl(AuthRemoteDataSource):
    def __init__(self, api_service):
        self.api_service = api_service

    async def login(self, phone: str, password: str):
        return await self.api_service.login({"phone": phone, "password": password})

    async def register(self, **kwargs):
        return await self.api_service.register(kwargs)

    async def send_otp(self, phone: str, purpose: str):
        return await self.api_service.send_otp({"phone": phone, "purpose": purpose})

    async def verify_otp(self, phone: str, code: str, purpose: str):
        return await self.api_service.verify_otp(
            {"phone": phone, "code": code, "purpose": purpose}
        )
