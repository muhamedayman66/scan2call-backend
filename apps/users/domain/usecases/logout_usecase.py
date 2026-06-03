from ..repositories.auth_repository import AuthRepository


class LogoutUseCase:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def __call__(self):
        """Execute logout"""
        return await self.repository.logout()
