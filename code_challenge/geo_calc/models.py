import uuid

from django.db import models


class GoogleAddrWithCoord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coord_lat = models.DecimalField(max_digits=16, null=False, decimal_places=10)
    coord_lng = models.DecimalField(max_digits=16, null=False, decimal_places=10)
    formatted_address = models.CharField(max_length=256, null=False, blank=False, unique=True)


class SearchTerms(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_term = models.CharField(max_length=256, null=False, blank=False)
    coord_record = models.ForeignKey(GoogleAddrWithCoord, on_delete=models.CASCADE, related_name="search_term")
