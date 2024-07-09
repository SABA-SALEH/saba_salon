from django.db import models

class Package(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    saving_price = models.DecimalField(max_digits=6, decimal_places=2)
    services = models.ManyToManyField('services.Service', related_name='packages')

    def __str__(self):
        return self.name
