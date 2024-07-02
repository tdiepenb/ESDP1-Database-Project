from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('stations/', views.StationListView.as_view(), name='station-list'),
]
