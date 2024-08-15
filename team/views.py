from django.shortcuts import render, get_object_or_404, redirect
from .models import StaffMember
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from .forms import StaffMemberForm

# Create your views here.


def team_list(request):
    """
    A view to show all staff members.
    """
    staff_members = StaffMember.objects.all()  # Fetch all staff members
    context = {
        'staff_members': staff_members,  # Pass the staff members to the template
    }
    return render(request, 'team/team_list.html', context)


def superuser_required(view_func):
    """
    Decorator to ensure that only superusers can access the decorated view.
    """
    return user_passes_test(lambda u: u.is_superuser)(view_func)


@superuser_required
def add_staff_member(request):
    """
    A view to handle adding a new staff member.
    """
    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the new staff member to the database
            messages.success(request, 'Staff member added successfully!')
            return redirect('team:team_list')  # Redirect to the staff list view after saving
    else:
        form = StaffMemberForm()  # Create an empty form for GET requests
    return render(request, 'team/add_staff_member.html', {'form': form})


@login_required
def edit_staff_member(request, pk):
    """
    A view to handle editing an existing staff member.
    """
    staff_member = get_object_or_404(StaffMember, pk=pk)  # Fetch the staff member or return 404
    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES, instance=staff_member)
        if form.is_valid():
            form.save()  # Update the staff member's details
            return redirect('team:team_list')  # Redirect to the staff list view after saving
    else:
        form = StaffMemberForm(instance=staff_member)  # Populate form with existing data
    return render(request, 'team/edit_staff_member.html', {'form': form, 'staff_member': staff_member})


@login_required
def delete_staff_member(request, pk):
    """
    A view to handle deleting a staff member.
    """
    staff_member = get_object_or_404(StaffMember, pk=pk)  # Fetch the staff member or return 404
    if request.method == 'POST':
        staff_member.delete()  # Delete the staff member from the database
        messages.success(request, 'Staff member deleted successfully!')
        return redirect('team:team_list')  # Redirect to the staff list view after deletion

    return redirect('team:team_list')  # Redirect to the staff list view if not a POST request
