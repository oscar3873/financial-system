from django.urls import path
from .views import *
from .utils import *

guarantor_patterns = ([
    path('', GuarantorListView.as_view(), name='list'),
    path('<uuid:pk>/', GuarantorDetailView.as_view(), name='detail'),
    path('create/', guarantorCreateView, name='create'),
    path('update/<uuid:pk>/', update_guarantor, name='update'),
    path('delete/<uuid:pk>/', delete_guarantor, name='delete'),
    path('search_guarantor/', search_guarantor, name='buscar_creditos'),
    path('delete/phonenumbers/<uuid:pk>/', delete_phone_number, name='delete_phone_number'),

], "guarantors")