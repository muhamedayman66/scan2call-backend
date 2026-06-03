from ....core.storage.secure_storage import SecureStorage
from ...domain.repositories.auth_repository import AuthRepository
from ..datasources.auth_remote_datasource import AuthRemoteDataSource


class AuthRepositoryImpl(AuthRepository):
    def __init__(self, remote_datasource: AuthRemoteDataSource, storage: SecureStorage):
        self.remote_datasource = remote_datasource
        self.storage = storage

    async def login(self, phone: str, password: str):
        response = await self.remote_datasource.login(phone, password)
        await self.storage.save_tokens(
            response["tokens"]["access"], response["tokens"]["refresh"]
        )
        return response

    async def register(self, **kwargs):
        response = await self.remote_datasource.register(**kwargs)
        await self.storage.save_tokens(
            response["tokens"]["access"], response["tokens"]["refresh"]
        )
        return response

    async def send_otp(self, phone: str, purpose: str):
        return await self.remote_datasource.send_otp(phone, purpose)

    async def verify_otp(self, phone: str, code: str, purpose: str):
        response = await self.remote_datasource.verify_otp(phone, code, purpose)
        if "tokens" in response:
            await self.storage.save_tokens(
                response["tokens"]["access"], response["tokens"]["refresh"]
            )
        return response

    async def logout(self):
        await self.storage.clear_tokens()
