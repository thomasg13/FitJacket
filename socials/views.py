from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'socials/socials.html')    

def search_users(request):
    query = request.GET.get('q')
    users = []

    if query:
        users = User.objects.filter(username__icontains=query)

    return render(request, 'socials/search_results.html', {'users': users, 'query': query})