from django.urls import path
from .views import *

advisers_patterns = ([
    path('', AdviserListView.as_view(), name='list'),
    path('<pk>/', AdviserDetailView.as_view(), name='detail'),
    path('update/<pk>/', update_user, name='update'),
    path('delete/<pk>/', AdviserDeleteView.as_view(), name='delete'),
    path('pay_commission/<pk>/', pay_commission, name='pay_commission'),
], "advisers")