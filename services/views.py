from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Service, Category

def all_services(request):
    """ A view to show all services, including sorting and search queries """

    services = Service.objects.all()
    query = None
    sort = None
    direction = None
    categories = None

    if request.GET:
        if 'category' in request.GET:
            category_names = request.GET.getlist('category')
            if 'All' not in category_names:
                services = services.filter(category__name__in=category_names)
                categories = Category.objects.filter(name__in=category_names)
                request.session['selected_category'] = category_names
            else:
                request.session.pop('selected_category', None)
                categories = Category.objects.all()
        else:
            selected_category = request.session.get('selected_category', [])
            if selected_category:
                services = services.filter(category__name__in=selected_category)
                categories = Category.objects.filter(name__in=selected_category)
            else:
                categories = Category.objects.all()

        if 'sort' in request.GET:
            sort = request.GET['sort']
            direction = request.GET.get('direction', 'asc')
            if direction == 'desc':
                sort = f'-{sort}'
            services = services.order_by(sort)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query.strip():  
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('services:all_services'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            services = services.filter(queries)

    current_sorting = f'{sort}_{direction}' if sort and direction else None

    selected_category = request.session.get('selected_category', [])

    if 'All' in request.GET.getlist('category', []):
        selected_category = []
        categories = Category.objects.all()

   
    if not selected_category:
        categories = Category.objects.all()

    context = {
        'services': services,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
        'selected_category': selected_category,
    }

    return render(request, 'services/services.html', context)

def service_detail(request, service_id):
    """ A view to show individual service details """

    service = get_object_or_404(Service, pk=service_id)

    context = {
        'service': service,
    }

    return render(request, 'services/service_detail.html', context)

def service_detail(request, service_id):
    """ A view to show individual service details """

    service = get_object_or_404(Service, pk=service_id)

    context = {
        'service': service,
    }

    return render(request, 'services/service_detail.html', context)