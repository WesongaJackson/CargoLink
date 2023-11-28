from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.template.loader import render_to_string

from .forms import ListForm, LoginForm, ProfileUpdateForm, UserRegistrationForm, SearchForm
from django.contrib.auth.models import User
from .models import Vehicle, Transaction, Notification
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
import json
import requests

from django.http import JsonResponse

import logging
from Main_app import mpesa
from django.core.mail import send_mail
from django.core.paginator import Paginator

from CargoLink import settings

logger = logging.getLogger(__name__)


# Create your views here.

# homeview
def index(request):
    return render(request, 'Main_app/index.html')


# aboutview
def about(request):
    return render(request, 'Main_app/about.html')


# contact view

def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        # print(email,message,name,subject)
        recipient_list = [settings.EMAIL_SETTINGS['EMAIL_HOST_USER']]
        message_body = f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}"
        # print(recipient_list)
        send_mail(
            subject=subject,
            message=message_body,
            from_email=email,
            recipient_list=recipient_list,
            fail_silently=True

        )

        messages.success(request, 'Thank you for contacting us')

    return render(request, 'Main_app/contact.html')


# services view
def service(request):
    return render(request, 'Main_app/services.html')


# signupview
@csrf_exempt
def signup(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, 'Account is created successful')
            return redirect('signin')
    else:
        form = UserRegistrationForm()
    return render(request, 'Main_app/register.html', {'form': form})


# loginview
@csrf_exempt
def signin(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful')
                return redirect('home')
            else:
                messages.error(request, 'Invalid Credentials')
    else:
        form = LoginForm()

    return render(request, 'Main_app/login.html', {'form': form})


# logoutview
@login_required
def signout(request):
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('index')


# profile view
@login_required
def profile(request):
    return render(request, 'Main_app/profile.html')


# update profile view
@csrf_exempt
@login_required
def update_profile(request):
    if request.method == 'POST':

        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            profile = p_form.save(commit=False)
            profile.phone_number = p_form.cleaned_data['phone_number']
            profile.location = p_form.cleaned_data['location']
            profile.save()
            messages.success(request, f'profile updated!')
            return redirect('profile')
    else:

        p_form = ProfileUpdateForm(instance=request.user.profile)
        context = {

            'p_form': p_form,
        }

    return render(request, 'Main_app/update_profile.html', context)


# creating vehicle

@login_required
@csrf_exempt
# @permission_required('Main_app.add_vehicle', raise_exception=True)
def create(request):
    if request.method == 'POST':
        form = ListForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = request.user.profile
            if user_profile.owner and user_profile.phone_number:
                form.instance.owner = user_profile
                form.save()
                messages.success(request, 'Item created successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Update your profile to add a phone number and set owner to true.')
                return redirect('update_profile')
    else:
        form = ListForm()

    return render(request, 'Main_app/create.html', {'form': form})


# listing
@login_required
def home(request):
    form = SearchForm()
    vehicles = Vehicle.objects.filter(is_published=True).order_by('-created_at')
    paginator = Paginator(vehicles, 6)
    page_number = request.GET.get("page")
    data = paginator.get_page(page_number)
    return render(request, 'Main_app/dashboard.html', {'vehicles': data, 'form': form})


#  notification
@login_required
def notification_view(request):
    notification = Notification.objects.filter(user=request.user,is_read=False).first()
    if  notification:
        notification.is_read = True
        notification.save()
    context = {
        'notification': notification,
        'unread_count': 1 if notification else 0,
    }

    return render(request, 'Main_app/notification.html', context=context)


@login_required
def search_vehicle(request):
    vehicles = None
    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            vehicle_location = form.cleaned_data.get('location')
            vehicle_type = form.cleaned_data.get('type')
            vehicle_model = form.cleaned_data.get('model')
            vehicle_for_hire_or_sell = form.cleaned_data.get('for_hire_or_sell')

            vehicle_price = form.cleaned_data.get('price')

            query = Q()

            if vehicle_location:
                query |= Q(location__icontains=vehicle_location)
            if vehicle_type:
                query |= Q(type__icontains=vehicle_type)
            if vehicle_model:
                query |= Q(model__icontains=vehicle_model)
            if vehicle_for_hire_or_sell:
                query |= Q(for_hire_or_sell__icontains=vehicle_for_hire_or_sell)
            if vehicle_price is not None:
                query |= Q(price__lt=vehicle_price)

            vehicles = Vehicle.objects.filter(query)


    else:
        form = SearchForm()

    context = {
        'form': form,
        'vehicles': vehicles
    }

    return render(request, 'Main_app/dashboard.html', context)


#
@csrf_exempt
@login_required
def details(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'Main_app/detail.html', {'vehicle': vehicle})


# delete vehicle
@login_required
@permission_required('Main_app.delete_vehicle', raise_exception=True)
def delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    vehicle.delete()
    messages.error(request, 'Item delete successfully')
    return redirect('home')


# mpesa views


# Create your views here.

@csrf_exempt
@login_required
def initiate_payment(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == "POST":
        phone = request.POST['phone']
        amount = 1
        logger.info(f"{phone} {amount}")
        data = {
            "BusinessShortCode": mpesa.get_business_shortcode(),
            "Password": mpesa.generate_password(),
            "Timestamp": mpesa.get_current_timestamp(),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": mpesa.get_business_shortcode(),
            "PhoneNumber": phone,
            "CallBackURL": mpesa.get_callback_url(),
            "AccountReference": "123456",
            "TransactionDesc": "Payment for Booking",
        }
        headers = mpesa.generate_request_headers()
        response = requests.post(mpesa.get_payment_url(), json=data, headers=headers)
        logger.info(response.json())
        json_response = response.json()
        if "ResponseCode" in json_response:
            code = json_response['ResponseCode']
            if code == "0":
                mid = json_response['MerchantRequestID']
                cid = json_response['CheckoutRequestID']
                logger.info(f"{mid} {cid}")
                transaction = Transaction.objects.create(
                    vehicle=vehicle,
                    phone_number=phone,
                    amount=amount,
                    merchant_request_id=mid,
                    checkout_request_id=cid,
                    status='pending'
                )
                context = {
                    'vehicle': vehicle,
                    'transaction': transaction,
                }
                return render(request, 'Main_app/pending.html', context=context)
            else:
                logger.error(f"Error while initiating stk push {code}")
        elif "errorCode" in json_response:
            erroCode = json_response["errorCode"]
            logger.error(f"Error with the server {erroCode}")

        # print(phone,amount)

    return render(request, 'Main_app/detail.html', {'vehicle': vehicle})


def success(request):
    return render(request, 'Main_app/success.html')


@csrf_exempt
def callback(request):
    result = json.loads(request.body)
    logger.info(result)
    print(result)
    mid = result["Body"]["stkCallback"]["MerchantRequestID"]
    cid = result["Body"]["stkCallback"]["CheckoutRequestID"]
    code = result["Body"]["stkCallback"]["ResultCode"]
    logger.info(f"From Callback Result {mid} {cid} {code}")
    transaction = Transaction.objects.filter(merchant_request_id=mid, checkout_request_id=cid).first()
    if transaction:
        if code == "0":
            transaction.status = "success"
        else:
            transaction.status = "error"
        print(f"Transaction: {transaction}")
        logger.info(f"this is transaction {transaction}")
        transaction.save()

    response_data = {
        'message': 'Successfully received',

    }
    return JsonResponse(response_data)


def check_payment(request, mid, cid):
    transaction = Transaction.objects.filter(merchant_request_id=mid, checkout_request_id=cid).first()
    if transaction:
        if transaction.status == 'success':
            vehicle_owner = transaction.vehicle.owner.user
            vehicle_type = transaction.vehicle.type
            vehicle_model = transaction.vehicle.model
            vehicle_location = transaction.vehicle.location
            vehicle_owner_phone_number = transaction.vehicle.owner.phone_number
            print(vehicle_owner_phone_number)

            user = request.user
            message = render_to_string('Main_app/new_message.html', {
                'user': user,
                'vehicle_owner': vehicle_owner,
                'vehicle_model': vehicle_model,
                'vehicle_type': vehicle_type,
                'vehicle_location': vehicle_location,
                'vehicle_owner_phone_number': vehicle_owner_phone_number,
            })

            notification = Notification.objects.create(user=user, message=message)


            success_url = reverse('payment_success')

            return redirect(success_url)

        else:
            return render(request, 'Main_app/error.html')

    return render(request, 'Main_app/error.html')
# def is_read(re)
