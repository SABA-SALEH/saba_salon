from django.db import models

# Create your models here.


class StaffMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='staff_photos/', null=True, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
