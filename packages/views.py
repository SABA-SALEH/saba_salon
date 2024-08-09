from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Package
from .forms import PackageForm
from django.contrib import messages
from django.urls import reverse

# Create your views here.


def package_list(request):
    packages = Package.objects.all()
    best_deal_package = max(packages, key=lambda package: package.saving_price, default=None)

    packages_with_ratings = []
    for package in packages:
        average_rating = package.get_average_rating()
        packages_with_ratings.append({
            'package': package,
            'average_rating': average_rating,
        })

    context = {
        'packages_with_ratings': packages_with_ratings,
        'best_deal_package': best_deal_package,
    }
    return render(request, 'packages/package_list.html', context)


@login_required
def add_package(request):
    """ Add a package to the salon """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('home:index'))

    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save()
            messages.success(request, 'Successfully added package!')
            return redirect(reverse('packages:package_list'))
        else:
            messages.error(request, 'Failed to add package. Please ensure the form is valid.')
    else:
        form = PackageForm()
    template = 'packages/add_package.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_package(request, package_id):
    """ Edit a package in the salon """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('home:index'))

    package = get_object_or_404(Package, pk=package_id)
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated package!')
            return redirect(reverse('packages:package_list'))
        else:
            messages.error(request, 'Failed to update package. Please ensure the form is valid.')
    else:
        form = PackageForm(instance=package)
        messages.info(request, f'You are editing {package.name}')

    template = 'packages/edit_package.html'
    context = {
        'form': form,
        'package': package,
    }

    return render(request, template, context)


@login_required
def delete_package(request, package_id):
    """ Delete a package from the salon"""
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('home:index'))

    package = get_object_or_404(Package, pk=package_id)
    package.delete()
    messages.success(request, 'Package deleted!')
    return redirect(reverse('packages:package_list'))
