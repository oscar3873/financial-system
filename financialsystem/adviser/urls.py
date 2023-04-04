from django.urls import path
from .views import *
from commissions.views import *

advisers_patterns = ([
    path('', AdviserListView.as_view(), name='list'),
    path('<pk>/', AdviserDetailView.as_view(), name='detail'),
    path('update/<pk>/', AdviserUpdateView.as_view(), name='update'),
    path('delete/<pk>/', AdviserDeleteView.as_view(), name='delete'),
    path('delete/commission/<pk>/', delete_commission, name='delete_commission'),
    path('pay_commission/<pk>/', pay_commission, name='pay_commission'),
], "advisers")