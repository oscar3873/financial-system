from django.urls import path
from .views import ClientListView, ClientDetailView, ClientCreate, ClientUpdate, delete_phone_number, ClientDelete

clients_patterns = ([
    path('', ClientListView.as_view(), name='list'),
    path('<int:pk>/', ClientDetailView.as_view(), name='detail'),
    path('create/', ClientCreate.as_view(), name='create'),
    path('update/<int:pk>/', ClientUpdate.as_view(), name='update'),
    path('delete/<int:pk>/', ClientDelete.as_view(), name='delete'),
    path('delete-phone-number/<int:pk>/', delete_phone_number, name='delete_phone_number'),
], "clients")