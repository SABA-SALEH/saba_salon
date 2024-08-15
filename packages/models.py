from django.db import models
from django.apps import apps
from django.db.models import Avg


class Package(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    saving_price = models.DecimalField(max_digits=6, decimal_places=2)
    services = models.ManyToManyField('services.Service', related_name='packages')

    def get_average_rating(self):
        """
        Returns the average rating of the package.
        """
        Review = apps.get_model('reviews', 'Review')
        reviews = Review.objects.filter(package=self)
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        return round(average_rating, 1) if average_rating is not None else None

    def __str__(self):
        """
        Returns the string representation of the package.
        """
        return self.name

    class Meta:
        """
        Meta options for the Package model.
        """
        verbose_name_plural = "Packages"
        ordering = ['name']
