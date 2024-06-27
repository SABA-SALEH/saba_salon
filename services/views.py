from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Service, Category , Booking
from django.http import JsonResponse
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils import timezone


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
        'selected_category_names': selected_category,
    }

    return render(request, 'services/services.html', context)




def service_detail(request, service_id):
    """ A view to show individual service details and handle booking """

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
            return redirect('service_detail', service_id=service_id)

    if request.method == 'GET':
        booking_date = request.GET.get('booking_date')  
        if not booking_date:
            booking_date = datetime.now().date()  

    available_times = service.get_available_times(booking_date)

    context = {
        'service': service,
        'additional_services': additional_services,
        'available_times': available_times,
    }

    return render(request, 'services/service_detail.html', context)



class MockBooking:
    def __init__(self, user, service, date, time):
        self.user = user
        self.service = service
        self.date = date
        self.time = time
        self.created_at = timezone.now()

@login_required
@csrf_protect
def book_service(request, service_id):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')

        service = Service.objects.get(id=service_id)
        user = request.user

        booking = MockBooking(
            user=user,
            service=service,
            date=booking_date,
            time=booking_time,
        )

        additional_service_id = request.POST.get('additional_service')
        additional_booking = None
        if additional_service_id:
            additional_booking_date = request.POST.get('additional_booking_date')
            additional_booking_time = request.POST.get('additional_booking_time')
            additional_service = Service.objects.get(id=additional_service_id)
            additional_booking = MockBooking(
                user=user,
                service=additional_service,
                date=additional_booking_date,
                time=additional_booking_time,
            )

        context = {
            'booking': booking,
            'additional_booking': additional_booking,
        }

        
        return render(request, 'services/book_service.html', context)
    
    return HttpResponse("Invalid request method.", status=405)


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
