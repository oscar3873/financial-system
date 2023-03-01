from django.urls import path
from .views import QueryView, ClientListView, ClientDetailView, delete_phone_number, ClientDelete,update_client

clients_patterns = ([
    path('', ClientListView.as_view(), name='list'),
    path('<pk>/', ClientDetailView.as_view(), name='detail'),
    # path('create/', ClientCreate.as_view(), name='create'),
    path('update/<pk>/', update_client, name='update'),
    path('delete/<uuid:pk>/', ClientDelete.as_view(), name='delete'),
    path('delete-phone-number/<pk>/', delete_phone_number, name='delete_phone_number'),
    path('query/', QueryView.as_view(), name ='query'),
], "clients")