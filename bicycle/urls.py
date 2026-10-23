from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('book/<int:car_id>/', book_car, name='book_car'),
    path('my-bookings/', my_bookings, name='my_bookings'),
    path('bookings/<int:booking_id>/', booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/cancel/', cancel_booking, name='cancel_booking'),
]
