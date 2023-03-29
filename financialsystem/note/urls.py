from django.urls import path
from .views import NoteListView, NoteDetailView, NoteUpdateView, NoteDeleteView, NoteCreateView

note_patterns = ([
    path('', NoteListView.as_view(), name='list'),
    path('int:<pk>/', NoteDetailView.as_view(), name='detail'),
    path('create/', NoteCreateView.as_view(), name='create'),
    path('update/int:<pk>/', NoteUpdateView.as_view(), name='update'),
    path('delete/int:<pk>/', NoteDeleteView.as_view(), name='delete'),
], "notes")