from django.urls import path

from registration.views import SignupView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
]