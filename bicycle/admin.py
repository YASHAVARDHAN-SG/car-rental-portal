from django.contrib import admin
from .models import Car, Booking


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'price_per_day', 'fuel_type', 'transmission', 'seating_capacity', 'available')
    list_filter = ('available', 'brand')
    search_fields = ('brand', 'name')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'start_date', 'end_date', 'pickup_location', 'dropoff_location', 'total_price', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('car__name', 'car__brand', 'user__username', 'pickup_location', 'dropoff_location')
