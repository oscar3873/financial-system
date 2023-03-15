from copy import copy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from django.urls import reverse_lazy

#CRUD Warranty
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from credit.utils import refresh_condition
from credit.models import Credit
from .models import Warranty
from .forms import WarrantyForm, SellForm, WarrantyUpdateForm
from .filters import ListingFilter
from .utils import all_properties_warranty

# Create your views here.
class WarrantyListView(LoginRequiredMixin, ListView):
    """
    Lista de empeños que se encuentran en la base de datos.
    """
    model = Warranty
    template_name = "warranty/warranty_list.html"
    paginate_by = 6
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        """
        Extrae los datos de los empeños que se encuentran en la base de datos para usarlo en el contexto.
        """
        refresh_condition()
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["form_sell"] = SellForm()
        context["count_warrantys"] = self.model.objects.all().count()
        context["warrantys"] = self.model.objects.all()
        context["listing_filter"] = ListingFilter(self.request.GET, queryset=context["warrantys"])
        context["properties"] = all_properties_warranty
        
        return context
    
    def get_queryset(self):
        """
        Devuelve los empeños que se encuentran en la busqueda del filtro.
        """
        queryset = super().get_queryset()
        return ListingFilter(self.request.GET, queryset=queryset).qs


#DETALLE DE EMPEÑO (FUNCION UTIL PARA EL FUTURO, CON IMAGENES DEL ESTADO DEL MOMENTO QUE SE REGISTRO)
class WarrantyDetailView(LoginRequiredMixin, DetailView):
    """
    Detalle de un empeño.
    """
    model = Warranty
    template_name = "warranty/warranty_detail.html"
    
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'
    
    def get_object(self):
        """
        Devuelve el empeño que se encuentra en la URL.
        """
        refresh_condition()
        return get_object_or_404(Warranty, id=self.kwargs['pk'])


#CREACION DE UNA NOTA
class WarrantyCreateView(CreateView):
    """
    Crea un nuevo empeño.
    """
    model = Warranty
    form_class = WarrantyForm
    template_name = "warranty/warranty_form.html"
    
    def get_success_url(self) -> str:
        """
        Devuelve la URL de la vista que se debe redireccionar a la lista.
        """
        messages.success(self.request, 'Articulo creado correctamente', "success")
        return  reverse_lazy('warrantys:list')

#BORRADO DE UNA NOTA
#------------------------------------------------------------------
class WarrantyDeleteView(DeleteView):
    """
    Borra un empeño.
    """
    model = Warranty
    
    def get_success_url(self) -> str:
        """
        Devuelve la URL de la vista que se debe redireccionar a la lista.
        """
        messages.success(self.request, 'Articulo eliminado correctamente', "danger")
        return  reverse_lazy('warrantys:list')

#ACTUALIZACION DE UN MOVIMIENTO
#------------------------------------------------------------------
class WarrantyUpdateView(UpdateView):
    """
    Actualiza un empeño.
    """	
    model = Warranty
    form_class = WarrantyUpdateForm
    template_name_suffix = '_update_form'

    def get_success_url(self) -> str:
        """
        Devuelve la URL de la vista que se debe redireccionar a la lista.
        """
        messages.success(self.request, 'Articulo actualizado satisfactoriamente', "info")
        return  reverse_lazy('warrantys:list')


#REALIZAR UNA VENTA DE UN ARTICULO
#------------------------------------------------------------------
def sell_article(request, pk):
    """
    Realiza una venta de un articulo.
    """
    article = get_object_or_404(Warranty, pk = pk)
    form = SellForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            selled = form.save(commit=False)
            selled.adviser = request.user.adviser
            selled.article = article
            
            article.is_selled = True
            article.save()
            selled.save()
        else:
            messages.error(request, 'No se pudo realizar la venta', "danger")
    return redirect('warrantys:list')
    