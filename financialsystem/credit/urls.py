from django.urls import path
from .views import *

credits_patterns = ([
    path('create_credit/', crear_credito, name='create_credit'),
    path('', CreditListView.as_view(), name='list'),
    path('<uuid:pk>/', CreditDetailView.as_view(), name='detail'),
    path('<uuid:pk>/create_credit/', CreditCreateTo.as_view(), name='associate_credit_for_customer'),
    path('create/', AssociateCreateView.as_view(), name='associate_credit'),

    # path('update/<uuid:pk>/', CreditUpdateView.as_view(), name='update'),
    path('credits/edit/<uuid:pk>/', edit_credit, name='edit_credit'),#------------------------------------------------------------------   NUEVOOOO

    path('delete/<uuid:pk>/', client_delete, name='delete'),
    path('refinancing/<uuid:pk>/', refinance_installment, name='refinance'),
    path('refinance_detail/<uuid:pk>/', RefinancingDetailView.as_view(), name='refinance_detail'),
    path('installment/<uuid:pk>/update/', InstallmentUpdateView.as_view(), name='installment_update'),
    path('installment_refinanced/<uuid:pk>/update/', InstallmentRefUpdateView.as_view(), name='installmentRef_update'),
    path('search/', buscar_clientes_view, name='buscar_clientes'),


], "credits")