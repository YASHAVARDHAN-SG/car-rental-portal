from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Booking, Car


class HomePageTests(TestCase):
    def test_home_page_shows_available_cars_and_their_selected_photos(self):
        available_car = Car.objects.create(
            name='City',
            brand='Honda',
            price_per_day='40.00',
            image='image/honda-city.jfif',
            available=True,
        )
        Car.objects.create(
            name='Unavailable',
            brand='Example',
            price_per_day='50.00',
            available=False,
        )

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, available_car.brand)
        self.assertContains(response, available_car.name)
        self.assertContains(response, 'image/honda-city.')
        self.assertNotContains(response, 'Example Unavailable')

    def test_home_page_shows_an_empty_state_without_available_cars(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No cars are available right now')


class AuthenticationTests(TestCase):
    def test_valid_login_authenticates_user(self):
        User.objects.create_user(username='renter', password='StrongPassword!234')

        response = self.client.post(
            reverse('login'),
            {'username': 'renter', 'password': 'StrongPassword!234'},
        )

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login_displays_an_error(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'missing', 'password': 'not-the-password'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')

    def test_registration_creates_user_and_validates_password(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newrenter',
                'email': 'renter@example.com',
                'password1': 'StrongPassword!234',
                'password2': 'StrongPassword!234',
            },
        )

        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newrenter').exists())


class BookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='renter',
            password='StrongPassword!234',
        )
        self.car = Car.objects.create(
            name='City',
            brand='Honda',
            price_per_day='40.00',
        )

    def test_guest_is_redirected_to_login_and_returned_to_booking(self):
        response = self.client.get(reverse('book_car', args=[self.car.id]))

        self.assertRedirects(
            response,
            f'/login/?next=/book/{self.car.id}/',
        )

    def test_signed_in_user_can_confirm_booking_with_total_price(self):
        self.client.force_login(self.user)
        start = date.today() + timedelta(days=1)
        end = start + timedelta(days=2)

        response = self.client.post(
            reverse('book_car', args=[self.car.id]),
            {'start_date': start.isoformat(), 'end_date': end.isoformat()},
        )

        self.assertRedirects(response, reverse('home'))
        booking = Booking.objects.get(user=self.user, car=self.car)
        self.assertEqual(booking.total_price, Decimal('120.00'))

    def test_end_date_before_start_date_does_not_create_booking(self):
        self.client.force_login(self.user)
        start = date.today() + timedelta(days=2)
        end = start - timedelta(days=1)

        response = self.client.post(
            reverse('book_car', args=[self.car.id]),
            {'start_date': start.isoformat(), 'end_date': end.isoformat()},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The end date must be on or after the start date.')
        self.assertFalse(Booking.objects.exists())
