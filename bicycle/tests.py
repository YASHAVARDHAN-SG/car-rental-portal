from django.test import TestCase
from django.urls import reverse

from .models import Car


class HomePageTests(TestCase):
    def test_home_page_shows_available_cars_to_visitors(self):
        available_car = Car.objects.create(
            name='City',
            brand='Honda',
            price_per_day='2500.00',
            available=True,
        )
        Car.objects.create(
            name='Unavailable',
            brand='Example',
            price_per_day='1000.00',
            available=False,
        )

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, available_car.brand)
        self.assertContains(response, available_car.name)
        self.assertNotContains(response, 'Example Unavailable')

    def test_home_page_shows_an_empty_state_without_available_cars(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No cars are available right now')

    def test_booking_redirects_visitors_to_login(self):
        response = self.client.get(reverse('book_car', args=[1]))

        self.assertRedirects(response, '/login/?next=/book/1/')
