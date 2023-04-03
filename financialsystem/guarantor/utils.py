from django.http import JsonResponse
from credit.models import Credit
from django.db.models import Q

from guarantor.models import Guarantor


def search_guarantor(request):
    search_terms = request.GET.get('search_term_g').split()

    guarantors=Guarantor.objects.all()
    if search_terms:
        for term in search_terms:
            q_objects = Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(dni__icontains=term)
            guarantors = guarantors.filter(q_objects)
        
        data = {
            'guarantors': [
                {
                    'id': guarantor.id,
                    'full_name': f'{guarantor}',
                    'dni': guarantor.dni,
                } for guarantor in guarantors
            ]
        }
    else:
        data = {'guarantors': []}

    return JsonResponse(data)