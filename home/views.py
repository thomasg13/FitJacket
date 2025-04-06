from django.shortcuts import render

def home(request):
    return render(request, 'home/home.html')

def about(request):
    template_data = {'title': 'About'}
    return render(request, 'home/about.html', {'template_data': template_data})