# turfs/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q # For complex queries if needed later
from users.models import UserType # To check user type
from .models import Turf
from .forms import TurfForm


@login_required
def turf_list(request):
    """
    Displays a list of turfs with search and filter capabilities.
    - For Turf Owners: Shows only their turfs.
    - For Players: Shows all active turfs, allows search.
    - For Admins: Shows all turfs, allows search.
    """
    search_query = request.GET.get('q') # Get the search query from the URL parameter 'q'

    if request.user.is_turf_owner():
        turfs = Turf.objects.filter(owner=request.user)
        context_heading = "My Turfs"
    elif request.user.is_player():
        turfs = Turf.objects.filter(is_active=True) # Players only see active turfs
        context_heading = "Available Turfs"
    elif request.user.is_admin():
        turfs = Turf.objects.all() # Admins see all turfs
        context_heading = "All Turfs (Admin View)"
    else:
        turfs = Turf.objects.none() # No turfs for unhandled user types
        context_heading = "No Turfs Available"

    # Apply search filter if a query is provided
    if search_query:
        # Filter turfs by name or location containing the search query (case-insensitive)
        turfs = turfs.filter(Q(name__icontains=search_query) | Q(location__icontains=search_query))
        context_heading = f"Results for '{search_query}'" # Update heading for search results

    context = {
        'turfs': turfs,
        'heading': context_heading,
        'user_type': request.user.user_type,
        'search_query': search_query, # Pass the search query back to the template to pre-fill the search box
    }
    return render(request, 'turfs/turf_list.html', context)

@login_required
def turf_list(request):
    """
    Displays a list of turfs with search and filter capabilities.
    - For Turf Owners: Shows only their turfs.
    - For Players: Shows all active turfs, allows search.
    - For Admins: Shows all turfs, allows search.
    """
    search_query = request.GET.get('q') # Get the search query from the URL parameter 'q'

    # Start with a base queryset for all active turfs (most common for players)
    # This ensures that the search filter can be applied to the correct initial set.
    if request.user.is_turf_owner():
        initial_turfs = Turf.objects.filter(owner=request.user)
        context_heading = "My Turfs"
    elif request.user.is_player():
        initial_turfs = Turf.objects.filter(is_active=True)
        context_heading = "Available Turfs"
    elif request.user.is_admin():
        initial_turfs = Turf.objects.all()
        context_heading = "All Turfs (Admin View)"
    else:
        initial_turfs = Turf.objects.none()
        context_heading = "No Turfs Available"

    turfs = initial_turfs # Assign the initial filtered queryset

    # Apply search filter if a query is provided
    if search_query:
        # Filter turfs by name or location containing the search query (case-insensitive)
        turfs = turfs.filter(Q(name__icontains=search_query) | Q(location__icontains=search_query))
        context_heading = f"Results for '{search_query}'" # Update heading for search results

    # # --- DEBUGGING STEP ---
    # print(f"Search Query: '{search_query}'")
    # print(f"Filtered Turfs Count: {turfs.count()}")
    # for turf in turfs:
    #     print(f"  - Turf: {turf.name}, Location: {turf.location}")
    # # --- END DEBUGGING STEP ---

    context = {
        'turfs': turfs,
        'heading': context_heading,
        'user_type': request.user.user_type,
        'search_query': search_query, # Pass the search query back to the template to pre-fill the search box
    }
    return render(request, 'turfs/turf_list.html', context)

# ... (turf_create, turf_update, turf_delete functions remain the same) ...

@login_required
def turf_create(request):
    """
    Allows a Turf Owner to add a new turf.
    Requires the user to be a Turf Owner.
    """
    if not request.user.is_turf_owner():
        messages.error(request, "You must be a Turf Owner to add a turf.")
        return redirect('users:player_dashboard') # Redirect to a more appropriate page

    if request.method == 'POST':
        form = TurfForm(request.POST, request.FILES) # request.FILES is crucial for image uploads
        if form.is_valid():
            turf = form.save(commit=False) # Don't save to DB yet
            turf.owner = request.user # Assign the current logged-in user as the owner
            turf.save() # Now save to DB
            messages.success(request, f"Turf '{turf.name}' added successfully!")
            return redirect('turfs:turf_list') # Redirect to the turf list page
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = TurfForm() # Empty form for GET request
    return render(request, 'turfs/turf_form.html', {'form': form, 'form_title': 'Add New Turf'})

@login_required
def turf_update(request, pk):
    """
    Allows a Turf Owner to edit an existing turf.
    Ensures that only the owner of the turf can update it.
    """
    turf = get_object_or_404(Turf, pk=pk)

    # Security check: Ensure only the owner can update their turf
    if not request.user.is_turf_owner() or turf.owner != request.user:
        messages.error(request, "You are not authorized to edit this turf.")
        return redirect('turfs:turf_list') # Redirect to their turf list

    if request.method == 'POST':
        form = TurfForm(request.POST, request.FILES, instance=turf) # Pass instance for update
        if form.is_valid():
            form.save()
            messages.success(request, f"Turf '{turf.name}' updated successfully!")
            return redirect('turfs:turf_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = TurfForm(instance=turf) # Pre-populate form with existing turf data
    return render(request, 'turfs/turf_form.html', {'form': form, 'form_title': f'Edit Turf: {turf.name}'})

@login_required
def turf_delete(request, pk):
    """
    Allows a Turf Owner to delete an existing turf.
    Ensures that only the owner of the turf can delete it.
    """
    turf = get_object_or_404(Turf, pk=pk)

    # Security check: Ensure only the owner can delete their turf
    if not request.user.is_turf_owner() or turf.owner != request.user:
        messages.error(request, "You are not authorized to delete this turf.")
        return redirect('turfs:turf_list')

    if request.method == 'POST':
        turf.delete()
        messages.success(request, f"Turf '{turf.name}' deleted successfully!")
        return redirect('turfs:turf_list')
    # For GET request, render a confirmation page (optional, but good UX)
    return render(request, 'turfs/turf_confirm_delete.html', {'turf': turf})

