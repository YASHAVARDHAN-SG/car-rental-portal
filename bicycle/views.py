from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

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
    error = None
    if request.method == 'POST':
        try:
            start = datetime.strptime(request.POST.get('start_date', ''), '%Y-%m-%d').date()
            end = datetime.strptime(request.POST.get('end_date', ''), '%Y-%m-%d').date()
        except ValueError:
            error = 'Enter a valid start and end date.'
        else:
            if end < start:
                error = 'The end date must be on or after the start date.'
            elif start < date.today():
                error = 'The start date cannot be in the past.'
            else:
                days = (end - start).days + 1
                Booking.objects.create(
                    user=request.user,
                    car=car,
                    start_date=start,
                    end_date=end,
                    total_price=days * car.price_per_day,
                )
                messages.success(request, 'Your booking has been confirmed.')
                return redirect('home')
    return render(
        request,
        'booking.html',
        {
            'car': car,
            'error': error,
            'today': date.today().isoformat(),
            'start_date': request.POST.get('start_date', ''),
            'end_date': request.POST.get('end_date', ''),
        },
    )
