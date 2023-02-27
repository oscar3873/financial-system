from django.urls import path
from .views import WarrantyListView, WarrantyDetailView, WarrantyUpdateView, WarrantyDeleteView, WarrantyCreateView

warranty_patterns = ([
    path('', WarrantyListView.as_view(), name='list'),
    path('<pk>/', WarrantyDetailView.as_view(), name='detail'),
    path('create/', WarrantyCreateView.as_view(), name='create'),
    path('update/<pk>/', WarrantyUpdateView.as_view(), name='update'),
    path('delete/<pk>/', WarrantyDeleteView.as_view(), name='delete'),
], "warrantys")