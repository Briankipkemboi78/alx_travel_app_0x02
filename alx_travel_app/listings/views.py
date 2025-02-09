from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
import requests
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Payment, Booking
from .tasks import send_payment_processing_email, send_payment_verified_email



class ListingViewSet(viewsets.ModelViewSet):

	queryset = Listing.objects.all()
	serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
	
	queryset = Booking.objects.all()
	serializer_class = BookingSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    user = request.user
    booking_id = request.data.get("booking_id")

    booking = get_object_or_404(Booking, id=booking_id, user=user)

    if hasattr(booking, 'payment') and booking.payment.status == "Completed":
        return Response({"error": "Payment already completed for this booking"}, status=status.HTTP_400_BAD_REQUEST)

    amount = booking.listing.price_per_night  # Modify if needed for multiple nights
    transaction_id = f"CHAPA_{booking.id}_{user.id}"
    
	#make amount serializable
    if isinstance(amount, Decimal):
        amount = float(amount)

    payload = {
        "amount": amount,
        "currency": "USD",
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "tx_ref": transaction_id,
        "customization[title]": "Booking Payment",
    }
    
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

    response = requests.post(settings.CHAPA_INITIATE_URL, json=payload, headers=headers)
    data = response.json()

    if data.get("status") == "success":
        # Create or update the payment entry
        payment, created = Payment.objects.update_or_create(
            booking=booking,
            defaults={"user": user, "amount": amount, "transaction_id": transaction_id, "status": "Pending"}
        )
         # Send payment processing email
        send_payment_processing_email.delay(user.email, booking.id)

        return Response({"checkout_url": data["data"]["checkout_url"]}, status=status.HTTP_200_OK)

    return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_payment(request, transaction_id):
    """This endpoint, in real life scenerio will be called after payment have been made i.e in initiate_payment dfined endpoint
    and response will be returned """
    # Get the user from the request object
    user = request.user

    # Make the Chapa API request to verify payment
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    response = requests.get(f"{settings.CHAPA_VERIFY_URL}{transaction_id}", headers=headers)

    if response.status_code != 200:
        return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

    data = response.json()

    # Verify the payment exists
    payment = get_object_or_404(Payment, transaction_id=transaction_id)

    # Verify the Chapa payment response
    if data.get("status") == "success" and data["data"].get("status") == "success":
        payment.status = "Completed"
        payment.save()

        # Send booking confirmation email after payment success
        send_payment_verified_email.delay(user.email, payment.booking.id)

        return Response({"message": "Payment successful and booking confirmed"}, status=status.HTTP_200_OK)
    else:
        # If payment verification fails, update payment status and send failure response
        payment.status = "Failed"
        payment.save()

        return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)