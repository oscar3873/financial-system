from django.urls import path
from .views import CashRegisterListView, MovementDetailView, MovementCreateView

cashregister_patterns = ([
    path('', CashRegisterListView.as_view(), name='list'),
    path('movement/', MovementCreateView.as_view(), name='movement'),
    path('<id>/', MovementDetailView.as_view(), name='detail'),
], "cashregister")