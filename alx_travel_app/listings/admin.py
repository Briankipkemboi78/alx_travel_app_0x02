from django.contrib import admin
from .models import Listing, Booking, Payment

# Register the Listing model
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_per_night', 'location', 'created_at')
    search_fields = ('title', 'location')
    list_filter = ('location',)

admin.site.register(Listing, ListingAdmin)

# Register the Booking model
class BookingAdmin(admin.ModelAdmin):
    list_display = ('listing', 'user', 'start_date', 'end_date', 'created_at')
    list_filter = ('listing', 'user')
    search_fields = ('listing__title', 'user__username')

admin.site.register(Booking, BookingAdmin)

# Register the Payment model
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'user', 'amount', 'status', 'transaction_id')
    list_filter = ('status',)
    search_fields = ('transaction_id',)

admin.site.register(Payment, PaymentAdmin)
