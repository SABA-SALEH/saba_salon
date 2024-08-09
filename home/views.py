from django.shortcuts import render
from services.models import Service, Booking

# Create your views here.


def index(request):
    """A view to return the index page"""
    services = Service.objects.all()
    return render(request, 'home/index.html', {'services': services})
