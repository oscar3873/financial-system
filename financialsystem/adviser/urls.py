from django.urls import path
from .views import AdviserListView, AdviserDetailView, AdviserUpdateView, AdviserDeleteView, AdviserCreateView

advisers_patterns = ([
    path('', AdviserListView.as_view(), name='list'),
    path('<int:pk>/', AdviserDetailView.as_view(), name='detail'),
    path('create/', AdviserCreateView.as_view(), name='create'),
    path('update/<int:pk>/', AdviserUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', AdviserDeleteView.as_view(), name='delete'),
], "advisers")