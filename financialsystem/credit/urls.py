from django.urls import path
from .views import *

credits_patterns = ([
    path('create_credit/', crear_credito, name='create_credit'),
    path('', CreditListView.as_view(), name='list'),
    path('<pk>/', CreditDetailView.as_view(), name='detail'),
    path('<pk>/create_credit/', CreditCreateTo.as_view(), name='associate_credit_for_customer'),
    path('create/', AssociateCreateView.as_view(), name='associate_credit'),
    path('update/<pk>/', CreditUpdateView.as_view(), name='update'),
    path('delete/<pk>/', CreditDeleteView.as_view(), name='delete'),
    path('refinancing/<pk>/', refinance_installment, name='refinance'),
    path('refinance_detail/<pk>/', RefinancingDetailView.as_view(), name='refinance_detail'),

], "credits")