from django.shortcuts import render
from .restaurant_search import search_rests

def search(request):
    if request.POST:
        term = request.POST['term']
        return render(request, 'search.html', {'result': search_rests(term)})
    else:
        return render(request, 'search.html')