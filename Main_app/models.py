import os
from django.db import models
from django.core.exceptions import ValidationError

import uuid
from django.contrib.auth.models import User
from PIL import Image


# Create your models here.
# profile pic unique name
def unique_image_name(instance, filename):
    name = uuid.uuid4()
    ext = filename.split(".")[-1]
    full_name = f"{name}.{ext}"
    return os.path.join('profile_pics', full_name)


# profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(default="default.png", null=True, upload_to=unique_image_name)
    owner = models.BooleanField(default=False, null=True, blank=True, )

    def __str__(self):
        return self.user.username
        # resizing  profile image

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


# vehicle image unique name
def unique_vehicle_image_name(instance, filename):
    name = uuid.uuid4()
    ext = filename.split(".")[-1]
    full_name = f"{name}.{ext}"
    return os.path.join('vehicle_images', full_name)


# vehicle model
class Vehicle(models.Model):
    VEHICLE_TYPE_CHOISES = [
        ('lorry', 'Lorry'),
        ('truck', 'Truck'),
        ('pickup', 'Pickup'),
    ]
    FOR_HIRE_OR_SELL = [
        ('hire', 'Hire'),
        ('sell', 'Sell'),
    ]
    MODEL = [
        ('isuzu', ' Isuzu'),
        ('toyota', 'Toyota'),
        ('mercedes-benz', 'Mercedes -Benz'),
        ('tata tipper', 'Tata Tipper'),
        ('mitsubishi', 'Mitsubishi'),
        ('others', 'Others'),

    ]
    model = models.CharField(max_length=100, choices=MODEL)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=VEHICLE_TYPE_CHOISES)
    location = models.CharField(max_length=100)
    for_hire_or_sell = models.CharField(max_length=20, choices=FOR_HIRE_OR_SELL)
    image = models.ImageField(upload_to=unique_vehicle_image_name)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='vehicles', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False, null=True)

    def generate_vehicle_unique_name(self):
        vehicle_type = self.type
        vehicle_model = self.model
        vehicle_owner_name =f"{self.owner.user.username[:3]}Cargo"
        unique_name = f"{vehicle_model}_{vehicle_type}_{vehicle_owner_name}"
        return unique_name

    # resizing vehicle image
    def save(self, *args, **kwargs):
        # print(f"Owner: {self.owner}")
        # print(f"Owner owner: {self.owner.owner}")
        # print(f"Owner phone number: {self.owner.phone_number}")

        if self.owner and self.owner.owner and self.owner.phone_number:
            unique_name = self.generate_vehicle_unique_name()
            self.name = unique_name
            super(Vehicle, self).save(*args, **kwargs)
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 400:
                output_size = (300, 400)
                img.thumbnail(output_size)
                img.save(self.image.path)
        else:
            # print("Validation failed")

            raise ValidationError("Update your profile  add phone number and ownership")

    def __str__(self):
        return f'{self.owner.user.username} vehicle'


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('error', 'Error'),
        ('success', 'Success')

    ]
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    merchant_request_id = models.CharField(max_length=50, unique=True)
    checkout_request_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    update_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'Transaction for {self.vehicle.model} - {self.status}'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} you have a message"
