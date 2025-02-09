from django.urls import path, include
from rest_framework import routers
from django.contrib.auth.decorators import login_required
from .views import ListingViewSet, BookingViewSet, initiate_payment, verify_payment

router = routers.DefaultRouter()
router.register(r'listing', ListingViewSet, basename='listing')
router.register(r'booking', BookingViewSet, basename='booking')

urlpatterns = [
	path('', include(router.urls)),
    path('payments/initiate/', login_required(initiate_payment), name='initiate-payment'),
    path('payments/verify/<str:transaction_id>/', login_required(verify_payment), name='verify-payment'),
]
