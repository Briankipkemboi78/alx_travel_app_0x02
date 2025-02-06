from rest_framework import routers
from django.urls import path, include
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet

from .views import initiate_payment, verify_payment
from . import views

class SampleAPIView(APIView):
    def get(self, request):
        return Response({"messge": "Hello, Django!"})
    
# Swagger schemaview
schema_view =get_schema_view(
    openapi.Info(
      title="Sample API",
      default_version='v1',
      description="Test API documentation",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@sample.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)

# Define API routes
router = routers.DefaultRouter()
router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),
    path('api/sample/', SampleAPIView.as_view(), name='sample-api'),
    path('api/', include(router.urls)),
    path("api/payment/initiate/", initiate_payment, name="initiate_payment"),
    path("api/payment/verify/", verify_payment, name="verify_payment"),
    path('create-booking/', views.create_booking_and_initiate_payment, name='create_booking_and_initiate_payment'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
]