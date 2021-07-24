from django.urls import path
from geo_calc.views import SearchLocationViewSet

urlpatterns = [
    path('search', SearchLocationViewSet.as_view({'get': 'list'}))
]