from django.shortcuts import render
from .restaurant_info import get_info, get_more, add_to_list

def restaurant(request, license):
    if request.POST:
        email = request.POST['email']
        add_to_list(license, email)
    context = get_info(license)
    return render(request, 'restaurant.html', context)

def more(request, license):
    return render(request, 'more.html', {'result': get_more(license)})