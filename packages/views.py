from django.shortcuts import render, get_object_or_404
from .models import Package

# Create your views here.

def package_list(request):
    packages = Package.objects.all()
    best_deal_package = max(packages, key=lambda package: package.saving_price, default=None)

    context = {
        'packages': packages,
        'best_deal_package': best_deal_package,
    }
    return render(request, 'packages/package_list.html', context)
   