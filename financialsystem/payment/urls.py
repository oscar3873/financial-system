from django.urls import path
from .views import PaymentListView, PaymentUpdateView, PaymentDeleteView, PaymentCreateView

payment_patterns = ([
    path('', PaymentListView.as_view(), name='list'),
    path('create/<pk>', PaymentCreateView.as_view(), name='create'),
    path('update/<pk>/', PaymentUpdateView.as_view(), name='update'),
    path('delete/<pk>/', PaymentDeleteView.as_view(), name='delete'),
], "payments")