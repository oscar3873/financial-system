from django.urls import path
from django.contrib.auth import views as auth_views

from registration.views import SignupView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),

]