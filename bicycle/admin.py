from django.contrib import admin
from .models import Car, Booking


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'price_per_day', 'available')
    list_filter = ('available', 'brand')
    search_fields = ('brand', 'name')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'start_date', 'end_date', 'total_price')
    list_filter = ('start_date', 'end_date')
    search_fields = ('car__name', 'car__brand', 'user__username')
