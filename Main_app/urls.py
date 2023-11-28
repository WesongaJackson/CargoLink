from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views
urlpatterns = [
    path("",views.index, name='index'),
    path("home/",views.home, name='home'),
    path("about/",views.about, name='about'),
    path("services/",views.service, name="services"),
    path("contact/",views.contact, name='contact'),
    path("register/",views.signup, name='signup'),
    path("login/",views.signin, name="signin"),
    path("logout/",views.signout, name='signout'),
    path('profile/',views.profile,name="profile"),
    path('update_profile/',views.update_profile,name="update_profile"),
    path('notification/',views.notification_view,name="notification"),
    path('create/',views.create,name="create"),
    path('search/',views.search_vehicle,name="search"),
    path('dashboard/<int:pk>/details/',views.details,name="details"),
    path('dashboard/<int:pk>/details/delete/',views.delete,name="delete"),
    path('dashboard/<int:pk>/details/initiate/', views.initiate_payment, name="initiate"),
    path('dashboard/details/callback/', views.callback, name="callback"),
    path('payment/success/', views.success, name="payment_success"),
    path('check/<str:mid>/<str:cid>/',views.check_payment,name='check'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)