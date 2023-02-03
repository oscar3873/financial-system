from django.urls import path
from .views import ClientListView, ClientDetailView

clients_patterns = ([
    path('', ClientListView.as_view(), name='list'),
    path('<id>/', ClientDetailView.as_view(), name='detail'),
], "clients")