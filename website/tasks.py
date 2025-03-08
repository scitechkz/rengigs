from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from .models import Subscription

def send_expiry_reminders():
    today = now().date()
    soon_expiring = Subscription.objects.filter(expiry_date__lte=today + timedelta(days=3))

    for sub in soon_expiring:
        subject = "Rengigs Subscription Expiring Soon!"
        message = f"Hello {sub.user.username},\n\nYour subscription for {sub.service.name} expires on {sub.expiry_date}. Renew now to continue enjoying the service."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [sub.user.email])
