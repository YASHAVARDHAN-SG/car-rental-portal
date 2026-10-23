from django.db import models
from django.contrib.auth.models import User

CAR_IMAGE_CHOICES = [
    ('image/brezza.jpg', 'Brezza'),
    ('image/Coupe.jpg', 'Coupe'),
    ('image/fortuner.jpg', 'Fortuner'),
    ('image/honda-city.jfif', 'Honda City'),
    ('image/Minivan.jpg', 'Minivan'),
    ('image/Pickup.png', 'Pickup'),
    ('image/Sedan.jpg', 'Sedan'),
    ('image/scorpio.jpg', 'Scorpio'),
    ('image/Sports.png', 'Sports car'),
    ('image/SUV.jpg', 'SUV'),
    ('image/safari.jpg', 'Safari'),
    ('image/verna.jpg', 'Verna'),
]


class Car(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.CharField(max_length=100, choices=CAR_IMAGE_CHOICES, blank=True)
    description = models.TextField(blank=True)
    fuel_type = models.CharField(max_length=30, blank=True)
    transmission = models.CharField(max_length=30, blank=True)
    seating_capacity = models.PositiveSmallIntegerField(default=5)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand} {self.name}"

class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    pickup_location = models.CharField(max_length=200, default='Not specified')
    dropoff_location = models.CharField(max_length=200, default='Not specified')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    cancelled_at = models.DateTimeField(blank=True, null=True)
