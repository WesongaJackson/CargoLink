from django.contrib import admin
from .models import Profile, Vehicle, Transaction, Notification


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'location', 'owner']
    list_filter = ['location', 'owner']
    search_fields = ['location']


# Register your models here.
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['owner', 'name','model','is_published', 'type', 'location', 'for_hire_or_sell']
    list_filter = ['location', 'owner','is_published', 'model', 'type', 'for_hire_or_sell']
    search_fields = ['location','is_published', 'owner', 'model', 'type']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'status', 'checkout_request_id', 'merchant_request_id', 'vehicle__name',
                    'created_at', 'update_at']
    list_filter = ['status']
    search_fields = ['phone_number', 'vehicle__name','status', 'checkout_request_id', ' merchant_request_id']

    def vehicle__name(self, obj):
        return obj.vehicle.name

    vehicle__name.short_description = 'Vehicle Name'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_for', 'message', 'created_at', 'is_read']
    list_filter = ['is_read']
    search_fields = ['user__username', 'message']

    def notification_for(self, obj):
        return obj.user.username

