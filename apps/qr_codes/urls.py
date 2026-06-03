from django.urls import path

from . import views

urlpatterns = [
    path("<str:qr_hash>/", views.qr_page_view, name="qr-page"),
]
