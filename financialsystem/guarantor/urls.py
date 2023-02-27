from django.urls import path
from .views import GuarantorListView, GuarantorDetailView, GuarantorUpdateView, GuarantorDeleteView, GuarantorCreateView

guarantor_patterns = ([
    path('', GuarantorListView.as_view(), name='list'),
    path('<uuid:pk>/', GuarantorDetailView.as_view(), name='detail'),
    path('create/', GuarantorCreateView.as_view(), name='create'),
    path('update/<uuid:pk>/', GuarantorUpdateView.as_view(), name='update'),
    path('delete/<uuid:pk>/', GuarantorDeleteView.as_view(), name='delete'),
], "guarantors")