from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Package
from .forms import PackageForm
from django.contrib import messages
from django.urls import reverse


# View for listing all packages and identifying the best deal
def package_list(request):
    packages = Package.objects.all()
    # Determine the package with the highest saving price
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
    """Add a new package to the salon"""
    # Check if the user is a superuser (salon owner)
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

    context = {
        'form': form,
    }

    return render(request, 'packages/add_package.html', context)


@login_required
def edit_package(request, package_id):
    """Edit an existing package in the salon"""
    # Check if the user is a superuser (salon owner)
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('home:index'))

    # Get the package or return a 404 error if it doesn't exist
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

    context = {
        'form': form,
        'package': package,
    }

    return render(request, 'packages/edit_package.html', context)


@login_required
def delete_package(request, package_id):
    """Delete a package from the salon"""
    # Check if the user is a superuser (salon owner)
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only salon owners can do that.')
        return redirect(reverse('home:index'))

    # Get the package or return a 404 error if it doesn't exist
    package = get_object_or_404(Package, pk=package_id)
    package.delete()
    messages.success(request, 'Package deleted!')
    return redirect(reverse('packages:package_list'))
