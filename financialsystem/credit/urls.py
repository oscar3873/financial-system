from django.urls import path
from .views import CreditListView, CreditDetailView, CreditUpdateView, CreditDeleteView, CreditCreateView

credits_patterns = ([
    path('', CreditListView.as_view(), name='list'),
    path('<uuid:pk>/', CreditDetailView.as_view(), name='detail'),
    path('create/', CreditCreateView.as_view(), name='create'),
    path('update/<pk>/', CreditUpdateView.as_view(), name='update'),
    path('delete/<pk>/', CreditDeleteView.as_view(), name='delete'),
], "credits")