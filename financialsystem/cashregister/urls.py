from django.urls import path
from .views import CashRegisterListView, MovementListView, MovementDetailView, MovementUpdateView, MovementDeleteView, change_password

cashregister_patterns = ([
    path('', CashRegisterListView.as_view(), name='home'),
    # path('movements/', MovementListView.as_view(), name='list'),
    path('movements/<pk>/', MovementDetailView.as_view(), name='detail'),
    path('movements/update/<pk>/', MovementUpdateView.as_view(), name='update'),
    path('movements/delete/<pk>/', MovementDeleteView.as_view(), name='delete'),
    path('change/password', change_password, name= 'change_password'),
], "cashregister")