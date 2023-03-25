from django.urls import path
from .views import *

commission_patterns = ([
    path('', setting_parameters, name='settings'),
], "commissions")