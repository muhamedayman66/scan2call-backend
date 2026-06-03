from ...data.models.login_request import LoginRequest
from ..repositories.auth_repository import AuthRepository


class LoginUseCase:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def __call__(self, phone: str, password: str):
        """Execute login use case"""
        return await self.repository.login(phone, password)
