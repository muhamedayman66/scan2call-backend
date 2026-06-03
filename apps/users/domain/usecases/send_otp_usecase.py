from ..repositories.auth_repository import AuthRepository


class SendOtpUseCase:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def __call__(self, phone: str, purpose: str):
        """Send OTP to phone number"""
        return await self.repository.send_otp(phone, purpose)
