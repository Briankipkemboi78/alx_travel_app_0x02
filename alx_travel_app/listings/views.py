from rest_framework import viewsets
from django.shortcuts import render, redirect
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
import requests
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import uuid
from django.urls import reverse

# Listing view set remains unchanged
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


# Booking view set remains unchanged
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


# Set up logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
def initiate_payment(request):
    # Extract booking reference and amount from the request
    booking_reference = request.data.get('booking_reference')
    amount = request.data.get('amount')

    if not booking_reference or not amount:
        return Response({'error': 'Booking reference and amount are required.'}, status=400)

    try:
        # Ensure amount is a valid positive number
        amount = float(amount)
        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero.'}, status=400)
    except ValueError:
        return Response({'error': 'Invalid amount format.'}, status=400)

    # Prepare data for Chapa API request
    payment_data = {
        "amount": amount,
        "booking_reference": booking_reference,
        "secret_key": settings.CHAPA_SECRET_KEY,
    }

    try:
        # Send request to Chapa for payment initialization
        response = requests.post("https://sandbox.chapa.co/api/v1/initialize", data=payment_data)
        response_data = response.json()

        if response.status_code == 200:
            # Store the payment record in the database
            payment = Payment.objects.create(
                booking_reference=booking_reference,
                amount=amount,
                transaction_id=response_data['transaction_id'],
                status='Pending'  # Payment is pending until verified
            )

            # Return the payment URL for user redirection
            return redirect(response_data['payment_url'])

        else:
            # Handle failure from the Chapa API
            logger.error(f"Chapa API error: {response_data}")
            return Response({'error': 'Payment initiation failed. Please try again.'}, status=500)

    except requests.exceptions.RequestException as e:
        # Handle network issues or request failures
        logger.error(f"Error connecting to Chapa API: {str(e)}")
        return Response({'error': 'Payment initiation failed due to a connection error.'}, status=500)


@api_view(['POST'])
def create_booking_and_initiate_payment(request):
    # Extract booking data from the request
    listing_id = request.data.get('listing_id')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')

    if not listing_id or not start_date or not end_date:
        return Response({'error': 'Listing, start date, and end date are required.'}, status=400)

    # Create booking
    listing = Listing.objects.get(id=listing_id)
    user = request.user
    booking = Booking.objects.create(
        listing=listing,
        user=user,
        start_date=start_date,
        end_date=end_date
    )

    # Calculate the amount
    amount = listing.price_per_night * (end_date - start_date).days

    # Prepare payment data
    payment_data = {
        "amount": amount,
        "booking_reference": str(uuid.uuid4()),
        "secret_key": settings.CHAPA_SECRET_KEY,
    }

    # Send payment request to Chapa API
    response = requests.post("https://sandbox.chapa.co/api/v1/initialize", data=payment_data)
    response_data = response.json()

    if response.status_code == 200:
        # Store the payment record in the database
        Payment.objects.create(
            booking_reference=payment_data['booking_reference'],
            amount=amount,
            transaction_id=response_data['transaction_id'],
            status='Pending'
        )

        # Redirect user to the Chapa payment URL
        return redirect(response_data['payment_url'])

    return Response({'error': 'Payment initiation failed'}, status=400)


@api_view(['GET'])
def verify_payment(request):
    # Extract transaction ID from query parameters
    transaction_id = request.query_params.get('transaction_id')

    if not transaction_id:
        return Response({'error': 'Transaction ID is required.'}, status=400)

    # Request to verify payment status with Chapa
    response = requests.get(f"https://sandbox.chapa.co/api/v1/verify/{transaction_id}")
    response_data = response.json()

    if response.status_code == 200:
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)

        # Update payment status based on Chapa response
        payment.status = response_data.get('status', 'Failed')
        payment.save()

        return Response({'status': payment.status})

    return Response({'error': 'Payment verification failed'}, status=400)

def payment_form(request):
    return render(request, 'listings/payment_form.html')

def home(request):
    return render(request, 'home.html')
