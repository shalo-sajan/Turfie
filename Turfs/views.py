# Turfs/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Turf


@login_required
def turf_list_view(request):
    # Filter turfs to get only those owned by the current user
    owner_turfs = Turf.objects.filter(owner=request.user)
    
    context = {
        'turfs': owner_turfs
    }
    return render(request, 'turfs/turf_list.html', context)
@login_required
def turf_detail_view(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    context = {'turf': turf}
    return render(request, 'turfs/turf_detail.html', context)
@login_required
def turf_add_view(request):
    # if request.method == 'POST':
    #     # Handle form submission for adding a new turf
    #     # This part is not implemented in this snippet
    #     pass
    # else:
    #     # Render the form for adding a new turf
    #     # This part is not implemented in this snippet
    #     pass
    
    return render(request, 'turfs/turf_add.html')