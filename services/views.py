from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from .models import Service, Category

def all_services(request):
    """ A view to show all services, including sorting and search queries """

    services = Service.objects.all()
    query = None
    categories = Category.objects.all()

    if request.GET:
        if 'category' in request.GET:
            category_names = request.GET.getlist('category')
            services = services.filter(category__name__in=category_names)
            categories = Category.objects.filter(name__in=category_names)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('services:all_services'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            services = services.filter(queries)

    context = {
        'services': services,
        'search_term': query,
        'current_categories': categories,
    }

    return render(request, 'services/services.html', context)


def service_detail(request, service_id):
    """ A view to show individual service details """

    service = get_object_or_404(Service, pk=service_id)

    context = {
        'service': service,
    }

    return render(request, 'services/service_detail.html', context)