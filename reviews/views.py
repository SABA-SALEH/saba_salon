from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm
from services.models import Service
from packages.models import Package
from django.contrib import messages

def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    services = Service.objects.all()  
    packages = Package.objects.all()  
    return render(request, 'reviews/review_list.html', {'reviews': reviews, 'services': services, 'packages': packages})

@login_required
def add_review(request, entity_type, entity_id):
    if entity_type not in ['service', 'package']:
        return redirect('home')

    if entity_type == 'service':
        entity = get_object_or_404(Service, id=entity_id)
    else:
        entity = get_object_or_404(Package, id=entity_id)

    form = ReviewForm(request.POST or None, initial={entity_type: entity})

    if request.method == 'POST':
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user

            if entity_type == 'service':
                review.service = entity
            elif entity_type == 'package':
                review.package = entity

            review.save()
            messages.success(request, 'Your review has been added successfully.')
            return redirect('reviews:review_list')

    return render(request, 'reviews/add_review.html', {
        'form': form,
        'entity': entity,
        'entity_type': entity_type,
        'entity_name': entity.name  
    })