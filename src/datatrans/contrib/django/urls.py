from django.urls import path

from . import views

app_name = "djdatatrans"

urlpatterns = [
    path("webhook/", views.webhook_view, name="webhook"),
]
