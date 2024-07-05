from django.shortcuts import render, get_object_or_404
from .models import Package

# Create your views here.


def package_list(request):
    packages = Package.objects.all()
    return render(request, 'packages/package_list.html', {'packages': packages})



   