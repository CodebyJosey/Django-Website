from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Book(models.Model):
    title = models.TextField()
    author = models.TextField()
    genre = models.TextField()
    number_of_pages = models.IntegerField(
        blank=False,
        validators=[
            MinValueValidator(1, message="Waarde moet groter dan of gelijk zijn aan 1!"),
            MaxValueValidator(4032, message="Er bestaat geen boek met meer dan 4032 pagina's!")]
    )
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='approved_by', null=True, blank=True)
    def __str__(self):
        return self.title
    

class Read(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(
            blank=False,
            validators=[
                MinValueValidator(0, message="Waarde moet grooter of gelijk zijn aan 0"),
                MaxValueValidator(10, message="Waarde moet kleiner dan of gelijk zijn aan 10")
            ])

class Profile(models.Model):
    biotext = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
