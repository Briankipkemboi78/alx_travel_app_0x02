from django.urls import path
from . import views

urlpatterns = [
    # URL for creating a booking and initiating the payment
    path('create_booking_and_initiate_payment/', views.create_booking_and_initiate_payment, name='create_booking_and_initiate_payment'),

    # URL for verifying payment after the user completes the payment process
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    
    # For listing, booking, and review management you might use DRF viewsets
    path('listings/', views.ListingViewSet.as_view({'get': 'list'}), name='listing-list'),
    path('bookings/', views.BookingViewSet.as_view({'get': 'list'}), name='booking-list'),
    path('payment-form/', views.payment_form, name='payment_form'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
]
