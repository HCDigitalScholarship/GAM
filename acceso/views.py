from django.shortcuts import render
from acceso.models import *

# Create your views here.
def main(request):
    return render(request, 'acceso/index.html', {})

def about(request):
    return render(request, 'acceso/about.html', {})

def map(request):
    return render(request, 'acceso/map.html', {})


def history(request):
    return render(request, 'acceso/history.html', {})

def caso(request, caso):
    caso = Caso.objects.get(slug_name=caso)
    context = {'caso': caso }
    return render(request, 'acceso/caso.html', context)











