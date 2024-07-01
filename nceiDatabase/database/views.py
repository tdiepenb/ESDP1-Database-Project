from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from .models import Station


# Create your views here.
def index(request):
    return HttpResponse("Hello, this is the index view of the database")


class StationListView(ListView):
    model = Station
    template_name = 'station_list.html'
    context_object_name = 'stations'
