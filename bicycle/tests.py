from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Bike, Booking, Car


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

    def test_home_page_shows_motorcycles_and_scooters_in_separate_sections(self):
        motorcycle = Bike.objects.create(
            name='Duke 390',
            brand='KTM',
            price_per_day='20.00',
            image='image/ktm-duke-390.svg',
            engine_cc=125,
            vehicle_type=Bike.VehicleType.MOTORCYCLE,
            available=True,
        )
        scooter = Bike.objects.create(
            name='Activa',
            brand='Honda',
            price_per_day='10.00',
            image='image/honda-activa.svg',
            engine_cc=110,
            vehicle_type=Bike.VehicleType.SCOOTER,
            available=True,
        )
        Bike.objects.create(
            name='Unavailable',
            brand='Example',
            price_per_day='25.00',
            available=False,
        )

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, motorcycle.name)
        self.assertContains(response, scooter.name)
        self.assertContains(response, 'ktm-duke-390.')
        self.assertContains(response, 'honda-activa.')
        self.assertContains(response, 'Motorcycles for Rent')
        self.assertContains(response, 'Scooters for Rent')
        self.assertNotContains(response, 'Example Unavailable')


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
            {
                'start_date': start.isoformat(),
                'end_date': end.isoformat(),
                'pickup_location': 'Airport',
                'dropoff_location': 'City Center',
            },
        )

        booking = Booking.objects.get(user=self.user, car=self.car)
        self.assertRedirects(
            response,
            reverse('booking_detail', args=[booking.id]),
        )
        self.assertEqual(booking.total_price, Decimal('120.00'))
        self.assertEqual(booking.pickup_location, 'Airport')
        self.assertEqual(booking.dropoff_location, 'City Center')

    def test_booking_form_requires_pickup_and_dropoff_locations(self):
        self.client.force_login(self.user)
        start = date.today() + timedelta(days=1)

        response = self.client.post(
            reverse('book_car', args=[self.car.id]),
            {
                'start_date': start.isoformat(),
                'end_date': start.isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertFalse(Booking.objects.exists())

    def test_end_date_before_start_date_does_not_create_booking(self):
        self.client.force_login(self.user)
        start = date.today() + timedelta(days=2)
        end = start - timedelta(days=1)

        response = self.client.post(
            reverse('book_car', args=[self.car.id]),
            {
                'start_date': start.isoformat(),
                'end_date': end.isoformat(),
                'pickup_location': 'Airport',
                'dropoff_location': 'City Center',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The end date must be on or after the start date.')
        self.assertFalse(Booking.objects.exists())

    def test_user_can_view_own_booking_details_but_not_another_users(self):
        booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            pickup_location='Airport',
            dropoff_location='City Center',
            total_price='40.00',
        )
        self.car.fuel_type = 'Petrol'
        self.car.transmission = 'Automatic'
        self.car.description = 'Compact city car'
        self.car.save()
        self.client.force_login(self.user)

        own_response = self.client.get(
            reverse('booking_detail', args=[booking.id]),
        )

        self.assertEqual(own_response.status_code, 200)
        self.assertContains(own_response, 'Airport')
        self.assertContains(own_response, 'City Center')
        self.assertContains(own_response, 'Automatic')
        self.assertContains(own_response, 'Compact city car')
        self.assertContains(own_response, 'Cancel booking')

        other_user = User.objects.create_user(
            username='another-renter',
            password='StrongPassword!234',
        )
        self.client.force_login(other_user)

        response = self.client.get(
            reverse('booking_detail', args=[booking.id]),
        )

        self.assertEqual(response.status_code, 404)

    def test_my_bookings_only_lists_the_signed_in_users_bookings(self):
        booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            pickup_location='Airport',
            dropoff_location='City Center',
            total_price='40.00',
        )
        other_user = User.objects.create_user(
            username='another-renter',
            password='StrongPassword!234',
        )
        Booking.objects.create(
            user=other_user,
            car=self.car,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            pickup_location='Other Airport',
            dropoff_location='Other City',
            total_price='40.00',
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('my_bookings'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Airport')
        self.assertContains(response, reverse('booking_detail', args=[booking.id]))
        self.assertNotContains(response, 'Other Airport')

    def test_user_can_cancel_own_booking_and_booking_remains_in_history(self):
        booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            pickup_location='Airport',
            dropoff_location='City Center',
            total_price='40.00',
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('cancel_booking', args=[booking.id]),
        )

        self.assertRedirects(
            response,
            reverse('booking_detail', args=[booking.id]),
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELLED)
        self.assertIsNotNone(booking.cancelled_at)

    def test_user_cannot_cancel_another_users_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            pickup_location='Airport',
            dropoff_location='City Center',
            total_price='40.00',
        )
        other_user = User.objects.create_user(
            username='another-renter',
            password='StrongPassword!234',
        )
        self.client.force_login(other_user)

        response = self.client.post(
            reverse('cancel_booking', args=[booking.id]),
        )

        self.assertEqual(response.status_code, 404)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)

    def test_get_request_cannot_cancel_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            pickup_location='Airport',
            dropoff_location='City Center',
            total_price='40.00',
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('cancel_booking', args=[booking.id]),
        )

        self.assertRedirects(
            response,
            reverse('booking_detail', args=[booking.id]),
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)
