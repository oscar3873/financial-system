from django.urls import path
from .views import HomePageView
from clients.views import QueryView

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('consultas', QueryView.as_view(), name="query"),
]
