from django.urls import path
from django.shortcuts import render, redirect
from .views import services, toggle_subscription
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),  # Services page
    path("toggle-subscription/", toggle_subscription, name="toggle_subscription"),  
    #path('signup/', views.signup, name='signup'),  # Signup page
    #path('success/', views.success, name='success'),  # Success page
    #path('contact/', views.contact, name='contact'),  # Contact page
    #path('contact-success/', views.contact_success, name='contact_success'),  # Success page
    path('about/', views.about, name='about'),  # About Us page
    
    path("signup/success/", lambda request: render(request, "website/signup_success.html"), name="signup_success"),
    path('contact/', views.contact_view, name='contact'),
    path("contact/success/", lambda request: render(request, "website/contact_success.html"), name="contact_success"),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
   #service urls
    path('services/', views.service_list, name='services'),
    path('subscribe/<int:service_id>/', views.subscribe, name='subscribe'),
    path('unsubscribe/<int:service_id>/', views.unsubscribe, name='unsubscribe'),
    #payment urls
    path('checkout/<int:service_id>/', views.create_checkout_session, name='checkout'),
    path('payment-success/<int:service_id>/', views.payment_success, name='payment_success'),
    #reminder urls for test- manual
    path('send-reminders/', views.send_reminders_view, name='send_reminders'),
    #dashboard urls
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    #add routes for renew  and cancel
    path('subscription/renew/<int:sub_id>/', views.renew_subscription, name='renew_subscription'),
    path('subscription/cancel/<int:sub_id>/', views.cancel_subscription, name='cancel_subscription'),
    #path for admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),



]
