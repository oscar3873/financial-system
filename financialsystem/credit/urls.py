from django.urls import path
from .views import CreditListView, CreditDetailView, CreditUpdateView, CreditDeleteView, CreditCreateView, crear_credito

credits_patterns = ([
    path('createcredit/', crear_credito, name='create_credit'),
    path('', CreditListView.as_view(), name='list'),
    path('<uuid:pk>/', CreditDetailView.as_view(), name='detail'),
    path('create/', CreditCreateView.as_view(), name='create'),
    path('update/<pk>/', CreditUpdateView.as_view(), name='update'),
    path('delete/<pk>/', CreditDeleteView.as_view(), name='delete'),
], "credits")