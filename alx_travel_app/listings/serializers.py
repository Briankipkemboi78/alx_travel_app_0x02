from rest_framework import serializers
from .models import Listing, Booking


class ListingSerializer(serializers.ModelSerializer):
    """Serialize Listing model"""
    class Meta:
        model = Listing
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    """	Serialize Booking model"""
    # listing = ListingSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'
