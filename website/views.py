from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from .forms import ProfileUpdateForm
from .models import Signup
from .forms import ContactForm
from .models import BlogPost
from .models import UserProfile
import stripe
from .models import Service, Payment, Subscription
from .tasks import send_expiry_reminders
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages



# Create your views here.
def home(request):
    return render(request, 'website/home.html')

#def services(request):
 #   return render(request, 'website/services.html')  # Renders the services page

def services(request):
    all_services = Service.objects.all()  # Fetch all services
    return render(request, 'website/services.html', {'services': all_services})


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            signup = form.save()

            # Send a well-formatted email
            subject = "Welcome to Rengigs Automation Solutions 🚀"
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #007bff;">Welcome to Rengigs, {signup.company_name}! 🎉</h2>
                <p>Thank you for signing up with Rengigs. Our team will reach out soon.</p>
                <p>🚀 <b>Automate your workflows & cut down costs</b> with AI-driven tools.</p>
                <p>🔹 AI BOTs for SOPs  
                🔹 Intelligent Workflow Automation  
                🔹 Business Process Optimization</p>
                <br>
                <p>Best Regards,</p>
                <p><b>The Rengigs Team</b></p>
            </body>
            </html>
            """
            email = EmailMessage(subject, html_content, settings.EMAIL_HOST_USER, [signup.email])
            email.content_subtype = "html"  # Set content type to HTML
            email.send()

            return redirect("signup_success")

    else:
        form = SignupForm()

    return render(request, "website/signup.html", {"form": form})



#This function renders the About Us page template.
def about(request):
    return render(request, 'website/about.html')

#the new contact view with email support. Old contact will go with success

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            # Format the email
            email_subject = f"New Contact Form Submission: {subject}"
            email_body = f"""
            Name: {name}
            Email: {email}

            Message:
            {message}
            """

            # Send email to admin
            send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, ["admin@rengigs.com"], fail_silently=False)

            return redirect("contact_success")  # Redirect to success page

    else:
        form = ContactForm()

    return render(request, "website/contact.html", {"form": form})


#this view list the blogs
def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, "website/blog_list.html", {"posts": posts})

def blog_detail(request, post_id):
    post = BlogPost.objects.get(id=post_id)
    return render(request, "website/blog_detail.html", {"post": post})

#this create the signupview as step 2 after creating the form


#creates the login view

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_dashboard')
        else:
            return render(request, 'website/login.html', {'error': 'Invalid username or password'})
    return render(request, 'website/login.html')

##creates the logout view
def logout_view(request):
    logout(request)
    return redirect('home')

#restrict dashboard to login users
@login_required
def dashboard(request):
    user_subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'website/dashboard.html', {'subscriptions': user_subscriptions})


#create the profile view

@login_required
def profile_view(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'website/profile.html', {'profile': profile})

# creates the profileedit view

@login_required
def edit_profile_view(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'website/edit_profile.html', {'form': form})


#list services



def service_list(request):
    services = Service.objects.all()
    user_subscriptions = Subscription.objects.filter(user=request.user) if request.user.is_authenticated else []
    subscribed_services = [sub.service.id for sub in user_subscriptions]

    return render(request, 'website/services.html', {
        'services': services,
        'subscribed_services': subscribed_services
    })

#create subscribe and unsubscribe view



@login_required
def subscribe(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    subscription, created = Subscription.objects.get_or_create(user=request.user, service=service)

    if not created:
        messages.warning(request, "You are already subscribed to this service.")
    else:
        messages.success(request, f"You have successfully subscribed to {service.name}.")

    return redirect('services')

    

@login_required
def unsubscribe(request, service_id):
    subscription = Subscription.objects.filter(user=request.user, service_id=service_id)
    if subscription.exists():
        subscription.delete()
    return redirect('services')

#creates payment view


@login_required
def create_checkout_session(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': service.name,
                },
                'unit_amount': int(service.price * 100),  # Stripe uses cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/payment-success/{service.id}/'),
        cancel_url=request.build_absolute_uri('/services/'),
    )

    return redirect(checkout_session.url, code=303)


#Creates a payment success view
#Sends an email confirmation to users after payment


@login_required
def payment_success(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    # Create payment record
    Payment.objects.create(user=request.user, service=service, amount=service.price)

    # Subscribe user to service
    Subscription.objects.get_or_create(user=request.user, service=service)

    # Send confirmation email
    subject = "Payment Successful - Rengigs"
    message = f"Dear {request.user.username},\n\nYou have successfully subscribed to {service.name}.\n\nThank you for choosing Rengigs!"
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])
    
    
    #notify admin
    #Notifies the admin team when a new user subscribes.
    admin_email = "admin@rengigs.com"
    admin_subject = f"New Subscription: {service.name}"
    admin_message = f"User {request.user.username} has subscribed to {service.name} for ${service.price}."
    send_mail(admin_subject, admin_message, settings.DEFAULT_FROM_EMAIL, [admin_email])
    


    return render(request, 'website/payment_success.html', {'service': service})

#send reminders

def send_reminders_view(request):
    send_expiry_reminders()
    return HttpResponse("Subscription expiry reminders sent!")


#creates user dashboard
#Ensures only logged-in users can access their dashboard.
#Fetches active subscriptions and payment history.

@login_required
def user_dashboard(request):
    subscriptions = Subscription.objects.filter(user=request.user)
   # payments = Payment.objects.filter(user=request.user).order_by('-date')
    payments = Payment.objects.filter(user=request.user).order_by('-paid_at')


    return render(request, 'dashboard/dashboard.html', {
        'subscriptions': subscriptions,
        'payments': payments
    })
    
    #subscription management - renew and cancel subscription
    

@login_required
def renew_subscription(request, sub_id):
    subscription = get_object_or_404(Subscription, id=sub_id, user=request.user)
    subscription.expiry_date += timedelta(days=30)  # Extend by 30 days
    subscription.save()
    
    messages.success(request, "Subscription renewed successfully!")
    return redirect('user_dashboard')

@login_required
def cancel_subscription(request, sub_id):
    subscription = get_object_or_404(Subscription, id=sub_id, user=request.user)
    subscription.delete()
    
    messages.success(request, "Subscription canceled successfully.")
    return redirect('user_dashboard')


#crates admin dashboard
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Subscription, Payment

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    active_subscriptions = Subscription.objects.count()
    total_revenue = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    #payments = Payment.objects.order_by('-date')[:10]  # Last 10 payments
    payments = Payment.objects.order_by('-paid_at')[:10]  # Fix field name
    users = User.objects.all().order_by('-date_joined')[:10]  # Last 10 users

    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'active_subscriptions': active_subscriptions,
        'total_revenue': total_revenue,
        'payments': payments,
        'users': users
    })

#toggle subsciption

@login_required
def toggle_subscription(request):
    if request.method == "POST":
        service_id = request.POST.get("service_id")
        service = get_object_or_404(Service, id=service_id)

        if request.user.subscriptions.filter(id=service.id).exists():
            request.user.subscriptions.remove(service)  # Unsubscribe
        else:
            request.user.subscriptions.add(service)  # Subscribe

    return redirect('services')
