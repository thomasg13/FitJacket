from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
def index(request):
    template_data = {}
    template_data['title'] = 'FitJacket'
    return render(request, 'home/index.html', {'template_data': template_data})
def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html',{'template_data': template_data})
