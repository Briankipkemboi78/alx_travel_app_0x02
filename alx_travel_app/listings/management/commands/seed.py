import random
from django.core.management.base import BaseCommand
from listings.models import Listing, Booking, Review
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        self.create_listings()
        self.create_bookings()
        self.create_reviews()
        self.stdout.write('Database seeded successfully!')

    def create_listings(self):
        Listing.objects.all().delete()
        listings_data = [
            {'title': 'Beach House', 'description': 'A lovely beach house.', 'price_per_night': 100.00, 'location': 'Malibu'},
            {'title': 'Mountain Cabin', 'description': 'A cozy cabin in the mountains.', 'price_per_night': 80.00, 'location': 'Aspen'},
            {'title': 'City Apartment', 'description': 'A modern apartment in the city.', 'price_per_night': 120.00, 'location': 'New York'},
        ]
        for listing in listings_data:
            Listing.objects.create(**listing)

    def create_bookings(self):
        Booking.objects.all().delete()
        listings = Listing.objects.all()
        users = User.objects.all()
        for listing in listings:
            user = random.choice(users)
            Booking.objects.create(
                listing=listing,
                user=user,
                start_date='2024-01-01',
                end_date='2024-01-07'
            )

    def create_reviews(self):
        Review.objects.all().delete()
        listings = Listing.objects.all()
        users = User.objects.all()
        for listing in listings:
            user = random.choice(users)
            Review.objects.create(
                listing=listing,
                user=user,
                rating=random.randint(1, 5),
                comment='Great place to stay!'
            )
