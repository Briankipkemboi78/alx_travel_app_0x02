from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import redirect  

from django.core.mail import send_mail
from celery import shared_task


# Listing view set remains unchanged
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

# Booking view set remains unchanged
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

@api_view(['POST'])
def initiate_payment(request):
    booking_reference = request.data.get('booking_reference')
    amount = request.data.get('amount')

    # Prepare data for the API request
    payment_data = {
        "amount": amount,
        "booking_reference": booking_reference,
        "secret_key": settings.CHAPA_SECRET_KEY,
    }

    # Send the request to the Chapa API for payment initialization
    response = requests.post("https://sandbox.chapa.co/api/v1/initialize", data=payment_data)
    response_data = response.json()

    if response.status_code == 200:
        # Store transaction information in the Payment model
        payment = Payment.objects.create(
            booking_reference=booking_reference,
            amount=amount,
            transaction_id=response_data['transaction_id'],
            status='Pending'  # Initial status is 'Pending'
        )

        # Return the payment URL for redirecting the user to the payment page
        return Response({'payment_url': response_data['payment_url'], 'transaction_id': response_data['transaction_id']})

    return Response({'error': 'Payment initiation failed'}, status=400)


@api_view(['GET'])
def verify_payment(request):
    transaction_id = request.query_params.get('transaction_id')

    # Request to verify the payment status from Chapa
    response = requests.get(f"https://sandbox.chapa.co/api/v1/verify/{transaction_id}")
    response_data = response.json()

    if response.status_code == 200:
        # Get the payment from the database using the transaction_id
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)

        # Update payment status
        payment.status = response_data.get('status', 'Failed')
        payment.save()

        # Return the updated payment status
        return Response({'status': payment.status})
    
    return Response({'error': 'Payment verification failed'}, status=400)


@shared_task
def send_confirmation_email(booking_reference, user_email):
    send_mail(
        'Booking Payment Confirmation',
        f'Your payment for booking {booking_reference} has been successfully completed.',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )

@api_view(['POST'])
def create_booking_and_initiate_payment(request):
    booking_reference = request.data.get('booking_reference')
    amount = request.data.get('amount')
    user_email = request.data.get('user_email')  # Assuming email is provided in the request

    # Create the booking record (you would have a Booking model)
    booking = Booking.objects.create(
        booking_reference=booking_reference,
        amount=amount,
    )

    # Call the initiate_payment function to get the payment URL
    payment_response = initiate_payment(request)
    
    if 'payment_url' in payment_response.data:
        # Redirect the user to the Chapa payment page
        return redirect(payment_response.data['payment_url'])

    # On successful payment, send confirmation email
    send_confirmation_email.apply_async(args=[booking_reference, user_email], countdown=5)

    return Response({'error': 'Payment initiation failed'}, status=400)