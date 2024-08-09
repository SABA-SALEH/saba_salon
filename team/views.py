from django.shortcuts import render, get_object_or_404, redirect
from .models import StaffMember
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StaffMemberForm

# Create your views here.


def team_list(request):
    """ A view to show all staff members """
    staff_members = StaffMember.objects.all()
    context = {
        'staff_members': staff_members,
    }
    return render(request, 'team/team_list.html', context)


def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


@superuser_required
def add_staff_member(request):
    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member added successfully!')
            return redirect('team:team_list')
    else:
        form = StaffMemberForm()
    return render(request, 'team/add_staff_member.html', {'form': form})


@login_required
def edit_staff_member(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)
    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES, instance=staff_member)
        if form.is_valid():
            form.save()
            return redirect('team:team_list')
    else:
        form = StaffMemberForm(instance=staff_member)
    return render(request, 'team/edit_staff_member.html', {'form': form, 'staff_member': staff_member})


@login_required
def delete_staff_member(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)
    if request.method == 'POST':
        staff_member.delete()
        messages.success(request, 'Staff member deleted successfully!')
        return redirect('team:team_list')

    return redirect('team:team_list')
