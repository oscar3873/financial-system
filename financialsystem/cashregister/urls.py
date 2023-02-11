from django.urls import path
from .views import CashRegisterListView, MovementListView, MovementDetailView, MovementUpdateView, MovementDeleteView

cashregister_patterns = ([
    path('', CashRegisterListView.as_view(), name='home'),
    path('movements/', MovementListView.as_view(), name='list'),
    path('movements/<int:pk>/', MovementDetailView.as_view(), name='detail'),
    path('movements/update/<int:pk>/', MovementUpdateView.as_view(), name='update'),
    path('movements/delete/<int:pk>/', MovementDeleteView.as_view(), name='delete'),
], "cashregister")