from django.urls import path
from .views import QueryView, ClientListView, ClientDetailView, ClientCreate, ClientUpdate, delete_phone_number, ClientDelete, PaymentFormView

clients_patterns = ([
    path('', ClientListView.as_view(), name='list'),
    path('<uuid:pk>/', ClientDetailView.as_view(), name='detail'),
    path('create/', ClientCreate.as_view(), name='create'),
    path('update/<uuid:pk>/', ClientUpdate.as_view(), name='update'),
    path('delete/<uuid:pk>/', ClientDelete.as_view(), name='delete'),
    path('delete-phone-number/<pk>/', delete_phone_number, name='delete_phone_number'),
    path('<pk>/payment', PaymentFormView.as_view(), name='payment'),
    path('query/', QueryView.as_view(), name ='query'),

], "clients")