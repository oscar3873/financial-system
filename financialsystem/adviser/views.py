from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from .models import Adviser

# Create your views here.
class AdviserListView(ListView):
    model = Adviser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["count_advisers"] = Adviser.objects.all().count()
        context["advisers"] = Adviser.objects.all()
        return context
    

class AdviserDetailView(DetailView):
    model = Adviser
    
    def get_object(self):
        return get_object_or_404(Adviser, id=self.kwargs['pk'])

class AdviserUpdateView(UpdateView):
    pass

class AdviserDeleteView(DeleteView):
    pass

class AdviserCreateView(CreateView):
    pass