from django.db import models
from django.conf import settings
from django.utils import timezone
from django.apps import apps


class Review(models.Model):
    RATINGS = [(i, str(i)) for i in range(1, 6)]

    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, null=True, blank=True)
    package = models.ForeignKey('packages.Package', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATINGS)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not (self.service or self.package):
            raise ValueError("A review must be associated with either a service or a package.")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.service:
            return f"Review by {self.user} for Service {self.service.name}"
        return f"Review by {self.user} for Package {self.package.name}"

    class Meta:
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['package']),
            models.Index(fields=['rating']),
        ]
