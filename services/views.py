from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Service, Category, Booking
from django.http import JsonResponse
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import ServiceForm
from reviews.models import Review
from django.db.models import Avg


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
            if sort == 'rating':
                services = services.annotate(avg_rating=Avg('review__rating'))
                sort = 'avg_rating'
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

    services_with_ratings = []
    for service in services:
        reviews = Review.objects.filter(service=service)
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        rounded_rating = round(average_rating) if average_rating is not None else None
        services_with_ratings.append({
            'service': service,
            'rounded_rating': rounded_rating,
        })

    context = {
        'services_with_ratings': services_with_ratings,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
        'selected_category': selected_category,
        'selected_category_names': selected_category,
    }

    return render(request, 'services/services.html', context)


def service_detail(request, service_id):
    """A view to show individual service details and handle booking"""

    service = get_object_or_404(Service, pk=service_id)
    additional_services = Service.objects.exclude(pk=service_id)

    if request.method == 'POST':
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')

        existing_bookings = Booking.objects.filter(service=service, date=booking_date, time=booking_time)
        if existing_bookings.exists():
            messages.error(request, f'The time slot {booking_time} on {booking_date} is already booked. Please choose another time.')
        else:
            Booking.objects.create(
                user=request.user,
                service=service,
                date=booking_date,
                time=booking_time
            )
            messages.success(request, 'Your booking has been confirmed!')
            return redirect('services:service_detail', service_id=service_id)

    if request.method == 'GET':
        booking_date = request.GET.get('booking_date')
        if not booking_date:
            booking_date = datetime.now().date()

    available_times = service.get_available_times(booking_date)

    reviews = Review.objects.filter(service=service)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    rounded_rating = round(average_rating) if average_rating is not None else None

    context = {
        'service': service,
        'additional_services': additional_services,
        'available_times': available_times,
        'average_rating': average_rating,
        'rounded_rating': rounded_rating,
        'reviews': reviews,
    }

    return render(request, 'services/service_detail.html', context)


class MockBooking:
    def __init__(self, user, service, date, time):
        self.user = user
        self.service = service
        self.date = date
        self.time = time
        self.created_at = timezone.now()


def get_available_times(request, service_id):
    if request.method == 'GET' and 'booking_date' in request.GET:
        service = get_object_or_404(Service, pk=service_id)
        booking_date = request.GET['booking_date']
        available_times = service.get_available_times(booking_date)
        data = {
            'available_times': available_times
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def get_booked_times(request, service_id):
    if request.method == 'GET' and 'booking_date' in request.GET:
        service = get_object_or_404(Service, pk=service_id)
        booking_date = request.GET['booking_date']
        booked_times_qs = Booking.objects.filter(service=service, date=booking_date).values_list('time', flat=True)
        booked_times = list(booked_times_qs)
        data = {
            'booked_times': booked_times
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_service(request):
    """ Add a service to the salon """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('services:all_services'))

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, 'Successfully added service!')
            return redirect(reverse('services:service_detail', args=[service.id]))
        else:
            messages.error(request, 'Failed to add service. Please ensure the form is valid.')
    else:
        form = ServiceForm()
    template = 'services/add_service.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_service(request, service_id):
    """ Edit a service in the salon """
    print(f"User: {request.user}, Superuser: {request.user.is_superuser}")

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('home:index'))

    service = get_object_or_404(Service, pk=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated service!')
            return redirect(reverse('services:service_detail', args=[service.id]))
        else:
            messages.error(request, 'Failed to update service. Please ensure the form is valid.')
    else:
        form = ServiceForm(instance=service)
        messages.info(request, f'You are editing {service.name}')

    template = 'services/edit_service.html'
    context = {
        'form': form,
        'service': service,
    }

    return render(request, template, context)


@login_required
def delete_service(request, service_id):
    """ Delete a service from the salon """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('home:index'))

    service = get_object_or_404(Service, pk=service_id)
    service.delete()
    messages.success(request, 'Service deleted!')
    return redirect(reverse('services:all_services'))
