from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .booking_forms import BookingForm
from .forms import RegistrationForm
from .models import Booking, Car


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    next_url = request.POST.get('next') or request.GET.get('next', '')
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect(next_url)
        return redirect('home')
    return render(request, 'login.html', {'form': form, 'next': next_url})


def register_view(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your account is ready. Please log in.')
        return redirect('login')
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    cars = Car.objects.filter(available=True)
    return render(request, 'index.html', {'cars': cars})


@login_required
def book_car(request, car_id):
    car = get_object_or_404(Car, id=car_id, available=True)
    form = BookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        start = form.cleaned_data['start_date']
        end = form.cleaned_data['end_date']
        days = (end - start).days + 1
        booking = Booking.objects.create(
            user=request.user,
            car=car,
            start_date=start,
            end_date=end,
            pickup_location=form.cleaned_data['pickup_location'],
            dropoff_location=form.cleaned_data['dropoff_location'],
            total_price=days * car.price_per_day,
        )
        messages.success(request, 'Your booking has been confirmed.')
        return redirect('booking_detail', booking_id=booking.id)
    return render(
        request,
        'booking.html',
        {
            'car': car,
            'form': form,
            'today': date.today().isoformat(),
        },
    )


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('car')
    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('car'),
        id=booking_id,
        user=request.user,
    )
    return render(request, 'booking_detail.html', {'booking': booking})


@login_required
def cancel_booking(request, booking_id):
    if request.method != 'POST':
        return redirect('booking_detail', booking_id=booking_id)

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user,
    )
    if booking.status == Booking.Status.CANCELLED:
        messages.info(request, 'This booking has already been cancelled.')
    else:
        booking.status = Booking.Status.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.save(update_fields=['status', 'cancelled_at'])
        messages.success(request, 'Your booking has been cancelled.')
    return redirect('booking_detail', booking_id=booking.id)
