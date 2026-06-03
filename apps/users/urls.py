from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("otp/send/", views.send_otp, name="send-otp"),
    path("otp/verify/", views.verify_otp, name="verify-otp"),
    path("password/reset/", views.reset_password, name="reset-password"),
    path("me/", views.UserProfileView.as_view(), name="user-profile"),
    path("me/photo/", views.upload_profile_photo, name="upload-photo"),
    path("me/fcm-token/", views.update_fcm_token, name="update-fcm-token"),
    path("logout/", views.delete_account, name="delete-account"),
    path("", include(router.urls)),
]
