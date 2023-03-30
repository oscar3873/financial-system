from django.urls import path
from .views import *

guarantor_patterns = ([
    path('', GuarantorListView.as_view(), name='list'),
    path('<uuid:pk>/', GuarantorDetailView.as_view(), name='detail'),
    path('create/', guarantorCreateView, name='create'),
    path('update/<uuid:pk>/', GuarantorUpdateView.as_view(), name='update'),
    path('delete/<uuid:pk>/', delete_guarantor, name='delete'),
], "guarantors")