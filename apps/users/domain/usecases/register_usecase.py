from ..repositories.auth_repository import AuthRepository


class RegisterUseCase:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def __call__(self, **kwargs):
        """Execute registration use case"""
        return await self.repository.register(**kwargs)
