from django.urls import path
from .views import *
clients_patterns = ([
    path('', ClientListView.as_view(), name='list'),
    path('<uuid:pk>/', ClientDetailView.as_view(), name='detail'),
    path('update/<pk>/', ClientUpdateView.as_view(), name='update'),
    path('delete/<uuid:pk>/', ClientDelete.as_view(), name='delete'),
    path('delete-phone-number/<pk>/', delete_phone_number, name='delete_phone_number'),
    path('query/', QueryView.as_view(), name ='query'),
], "clients")