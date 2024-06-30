from django.db import models


# Create your models here.
class Station(models.Model):
    GSN_FLAGS = [
        ('', 'non-GSN station or WMO Station number not available'),
        ('GSN', 'GSN station'),
    ]

    HCN_CRN_FLAGS = [
        ('', 'Not a member of the U.S. Historical Climatology or U.S. Climate Reference Networks'),
        ('HCN', 'U.S. Historical Climatology Network station'),
        ('CRN', 'U.S. Climate Reference Network or U.S. Regional Climate Network Station'),
    ]

    id = models.CharField(max_length=11, primary_key=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    elevation = models.DecimalField(max_digits=5, decimal_places=1, default=-999.9)
    state = models.CharField(max_length=2)
    name = models.CharField(max_length=30)
    gsn_flag = models.CharField(max_length=3, choices=GSN_FLAGS, blank=True)
    hcn_crn_flag = models.CharField(max_length=3, choices=HCN_CRN_FLAGS, blank=True)
    wmo_id = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.name
