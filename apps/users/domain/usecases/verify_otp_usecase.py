from ..repositories.auth_repository import AuthRepository


class VerifyOtpUseCase:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def __call__(self, phone: str, code: str, purpose: str):
        """Verify OTP code"""
        return await self.repository.verify_otp(phone, code, purpose)
