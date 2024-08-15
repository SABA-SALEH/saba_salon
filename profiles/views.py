from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm, ReviewForm
from checkout.models import Order
from reviews.models import Review


@login_required
def profile(request):
    """ Display the user's profile and manage their reviews. """
    # Get the user's profile or return a 404 if not found
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        # Handling profile update
        if 'update_profile' in request.POST:
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
            else:
                messages.error(request, 'Profile update failed. Please ensure the form is valid.')

        # Handling review update
        elif 'update_review' in request.POST:
            review_id = request.POST.get('review_id')
            if review_id:
                try:
                    review = get_object_or_404(Review, id=review_id, user=request.user)
                    form = ReviewForm(request.POST, instance=review)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Review updated successfully.')
                    else:
                        messages.error(request, 'Review update failed. Please ensure the form is valid.')
                except ValueError:
                    messages.error(request, 'Invalid review ID.')
            else:
                messages.error(request, 'Review ID is missing.')

        # Handling review deletion
        elif 'delete_review' in request.POST:
            review_id = request.POST.get('review_id')
            if review_id:
                try:
                    review = get_object_or_404(Review, id=review_id, user=request.user)
                    review.delete()
                    messages.success(request, 'Review deleted successfully.')
                except Exception as e:
                    messages.error(request, f'Error deleting review: {str(e)}')
            else:
                messages.error(request, 'Review ID is missing.')

        # Redirect to the profile page after handling the POST request
        return redirect('profiles:profile')

    else:
        # Initialize forms for GET request
        form = UserProfileForm(instance=profile)
        review_form = ReviewForm()

    # Retrieve user's reviews and orders
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    orders = profile.orders.all()

    # Context data for rendering the profile page
    context = {
        'form': form,
        'review_form': review_form,
        'reviews': reviews,
        'orders': orders,
        'on_profile_page': True,
        'username': request.user.username,
        'email': request.user.email,
    }

    return render(request, 'profiles/profile.html', context)


def order_history(request, order_number):
    """ Display details of a past order based on the order number. """
    # Get the order or return a 404 if not found
    order = get_object_or_404(Order, order_number=order_number)
    email = order.email

    # Display a confirmation message about the past booking
    messages.info(request, (
        f'This is a past confirmation for booking number {order_number}. '
        f'A confirmation email was sent to {email} on the booking date.'
    ))

    # Context data for rendering the order history page
    context = {
        'order': order,
        'email': email,
        'from_profile': True,
    }

    return render(request, 'checkout/checkout_success.html', context)
