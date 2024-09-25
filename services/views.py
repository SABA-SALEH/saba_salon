from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Service, Category, Booking
from django.http import JsonResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import ServiceForm
from reviews.models import Review
from django.db.models import Avg
from datetime import timedelta, datetime


def all_services(request):
    """
    View to display a list of all services with options to sort, filter by category,
    and search by name or description.
    """
    services = Service.objects.all()  # Retrieve all services
    query = None
    sort = None
    direction = None
    categories = None

    # Handle filtering and sorting based on GET parameters
    if request.GET:
        # Filter by category
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
            # Use previously selected categories from session if no category is specified in the request
            selected_category = request.session.get('selected_category', [])
            if selected_category:
                services = services.filter(category__name__in=selected_category)
                categories = Category.objects.filter(name__in=selected_category)
            else:
                categories = Category.objects.all()

        # Sort the services based on GET parameters
        if 'sort' in request.GET:
            sort = request.GET['sort']
            direction = request.GET.get('direction', 'asc')
            if sort == 'rating':
                services = services.annotate(avg_rating=Avg('review__rating'))
                sort = 'avg_rating'
            if direction == 'desc':
                sort = f'-{sort}'
            services = services.order_by(sort)

        # Search services by name or description
        if 'q' in request.GET:
            query = request.GET['q']
            if not query.strip():  # Check if query is empty
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('services:all_services'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            services = services.filter(queries)

    current_sorting = f'{sort}_{direction}' if sort and direction else None

    selected_category = request.session.get('selected_category', [])

    # Reset categories if 'All' is selected
    if 'All' in request.GET.getlist('category', []):
        selected_category = []
        categories = Category.objects.all()

    if not selected_category:
        categories = Category.objects.all()

    # Calculate ratings for services
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
    """
    View to show details for a specific service and handle booking.
    """
    service = get_object_or_404(Service, pk=service_id)  # Retrieve the service or 404 if not found
    additional_services = Service.objects.exclude(pk=service_id)  # Retrieve other services

    if request.method == 'POST':
        # Handle booking form submission
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
            booking_date = datetime.now().date()  # Default to today's date if no date provided

    available_times = service.get_available_times(booking_date)  # Get available times for the chosen date

    # Calculate average rating for the service
    reviews = Review.objects.filter(service=service).order_by('-created_at')
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
    """
    Mock class to simulate a booking object for testing purposes.
    """
    def __init__(self, user, service, date, time):
        self.user = user
        self.service = service
        self.date = date
        self.time = time
        self.created_at = timezone.now()


def get_available_times(request, service_id):
    """
    Returns available times for a given service and date in JSON format.
    """
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
    """
    Returns booked times for a given service and date in JSON format.
    """
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


# Utility function to create time slots between start and end time
def create_time_slots(start_time, end_time, duration):
    """
    Utility function to create time slots between start and end time.
    """
    slots = []
    current_time = start_time
    while current_time + duration <= end_time:
        slots.append(current_time.strftime('%H:%M'))
        current_time += duration
    return slots


# This function handles AJAX requests for dynamically generating time slots
def generate_time_slots(request):
    if request.method == 'GET' and 'duration' in request.GET:
        duration_str = request.GET['duration']
        
        # Adjust parsing for HH:MM:SS format
        hours, minutes, seconds = map(int, duration_str.split(':'))
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        start_time = datetime.strptime('09:00', '%H:%M')
        end_time = datetime.strptime('18:00', '%H:%M')

        # Use the utility function to generate time slots
        time_slots = create_time_slots(start_time, end_time, duration)

        return JsonResponse({'time_slots': time_slots})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_service(request):
    """
    Allows superusers to add a new service to the salon.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('services:all_services'))

    available_times = []
    
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

    # Calculate available time slots if a duration is specified in the form
    if request.method == 'POST' and form.is_valid():
        duration = request.POST.get('duration', '01:00')  # Default duration
        hours, minutes = map(int, duration.split(':'))
        duration_timedelta = timedelta(hours=hours, minutes=minutes)

        # Assume the start time is 09:00 and end time is 18:00
        start_time = datetime.strptime('09:00', '%H:%M')
        end_time = datetime.strptime('18:00', '%H:%M')
        available_times = create_time_slots(start_time, end_time, duration_timedelta)

    template = 'services/add_service.html'
    context = {
        'form': form,
        'available_times': available_times, 
    }

    return render(request, template, context)


@login_required
def edit_service(request, service_id):
    """
    Allows superusers to edit an existing service.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('home:index'))

    service = get_object_or_404(Service, pk=service_id)

    service_durations = {
        "00:15:00": "15 minutes",
        "00:30:00": "30 minutes",
        "01:00:00": "1 hour",
        "01:15:00": "1 hour 15 minutes",
        "01:30:00": "1 hour 30 minutes",
        "02:00:00": "2 hours",
        "02:30:00": "2 hours 30 minutes",
    }

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            service = form.save()
            messages.success(request, 'Successfully updated service!')
            return redirect(reverse('services:service_detail', args=[service.id]))
        else:
            messages.error(request, 'Failed to update service. Please ensure the form is valid.')
    else:
        form = ServiceForm(instance=service)
        messages.info(request, f'You are editing {service.name}')

    # Convert duration (timedelta) to string in HH:MM:SS format
    if isinstance(service.duration, timedelta):
        hours, remainder = divmod(service.duration.total_seconds(), 3600)
        minutes = remainder // 60
        service_duration_str = f"{int(hours):02}:{int(minutes):02}:00"
    else:
        service_duration_str = "01:00:00"  # Default duration if not a timedelta

    # Get the available time slots using `create_time_slots`
    start_time = datetime.strptime('09:00', '%H:%M')
    end_time = datetime.strptime('18:00', '%H:%M')
    
    # Convert the service duration string back to timedelta for generating time slots
    hours, minutes = map(int, service_duration_str.split(":")[:2])
    duration_timedelta = timedelta(hours=hours, minutes=minutes)
    available_times = create_time_slots(start_time, end_time, duration_timedelta)

    selected_times = service.available_times or []  

    context = {
        'form': form,
        'service': service,
        'service_durations': service_durations,
        'service_duration': service_duration_str,  
        'available_times': available_times, 
        'selected_times': selected_times,  
        'duration': service_duration_str, 
    }

    return render(request, 'services/edit_service.html', context)


@login_required
def delete_service(request, service_id):
    """
    Allows superusers to delete a service from the salon.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('home:index'))

    service = get_object_or_404(Service, pk=service_id)
    service.delete()
    messages.success(request, 'Service deleted!')
    return redirect(reverse('services:all_services'))