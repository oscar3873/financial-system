from django.urls import path
from .views import *
from .utils import *

credits_patterns = ([
    path('create_credit/', crear_credito, name='create_credit'),
    path('', CreditListView.as_view(), name='list'),
    path('<uuid:pk>/', CreditDetailView.as_view(), name='detail'),
    path('<uuid:pk>/create_credit/', CreditCreateTo.as_view(), name='associate_credit_for_customer'),
    path('create/', AssociateCreateView.as_view(), name='associate_credit'),
    path('update/<uuid:pk>/', edit_credit, name='edit_credit'),
    path('delete/<uuid:pk>/', credit_delete, name='delete'),
    path('refinancing/<uuid:pk>/', refinance_installment, name='refinance'),
    path('refinance/update/<uuid:pk>/', RefinancingUpdateView.as_view(), name='refinance_update'),
    path('refinance/delete/<uuid:pk>/', refinancing_delete, name='refinance_delete'),
    path('installment/update/<uuid:pk>/', InstallmentUpdateView.as_view(), name='installment_update'),
    path('installment_refinanced/<uuid:pk>/update/', InstallmentRefUpdateView.as_view(), name='installmentRef_update'),

    path('search/', search_client, name='buscar_clientes'),
    path('search_credit/', search_credit, name='buscar_creditos'),


], "credits")