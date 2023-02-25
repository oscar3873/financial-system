from django.urls import path
from .views import GuarantorListView, GuarantorDetailView, GuarantorUpdateView, GuarantorDeleteView, GuarantorCreateView

guarantor_patterns = ([
    path('', GuarantorListView.as_view(), name='list'),
    path('<int:pk>/', GuarantorDetailView.as_view(), name='detail'),
    path('create/', GuarantorCreateView.as_view(), name='create'),
    path('update/<int:pk>/', GuarantorUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', GuarantorDeleteView.as_view(), name='delete'),
], "guarantors")