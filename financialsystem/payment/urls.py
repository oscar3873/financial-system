from django.urls import path
from .views import *

payment_patterns = ([
    path('', PaymentListView.as_view(), name='list'),
    path('pay/<pk>', make_payment_installment, name='make_paid'),
    path('update/<pk>/', PaymentUpdateView.as_view(), name='update'),
    path('delete/<pk>/', PaymentDeleteView.as_view(), name='delete'),
], "payments")