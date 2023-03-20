from django.urls import path
from .views import NoteListView, NoteDetailView, NoteUpdateView, NoteDeleteView, NoteCreateView

note_patterns = ([
    path('', NoteListView.as_view(), name='list'),
    path('<pk>/', NoteDetailView.as_view(), name='detail'),
    path('create/', NoteCreateView.as_view(), name='create'),
    path('update/<pk>/', NoteUpdateView.as_view(), name='update'),
    path('delete/<pk>/', NoteDeleteView.as_view(), name='delete'),
], "notes")