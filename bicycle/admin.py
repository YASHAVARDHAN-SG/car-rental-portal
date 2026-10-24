from django.contrib import admin
from .models import Bike, Booking, Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'price_per_day', 'fuel_type', 'transmission', 'seating_capacity', 'available')
    list_filter = ('available', 'brand')
    search_fields = ('brand', 'name')


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'vehicle_type', 'price_per_day', 'engine_cc', 'transmission', 'available')
    list_filter = ('vehicle_type', 'available', 'brand')
    search_fields = ('brand', 'name')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'start_date', 'end_date', 'pickup_location', 'dropoff_location', 'total_price', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('car__name', 'car__brand', 'user__username', 'pickup_location', 'dropoff_location')
