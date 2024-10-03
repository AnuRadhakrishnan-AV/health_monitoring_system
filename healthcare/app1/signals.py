from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Recommendation
from django.core.mail import send_mail  
from django.contrib.auth.models import User
from django.conf import settings

#notification when recommendation created

@receiver(post_save, sender=Recommendation)
def send_recommendation_notification(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        recommendation_text = instance.recommendation_text 
        
       
        notification_message = (
            f"Dear {user.username},\n\n"
            f"A new health recommendation has been added for you.\n\n"
            f"Recommendation: {recommendation_text}\n\n"
            f"Best regards,\n"
            f"Your Health Monitoring Team"
        )
        
       
        send_mail(
            subject='New Health Recommendation',
            message=notification_message,
            from_email=settings.EMAIL_HOST_USER,  
            recipient_list=[user.email],
            fail_silently=False,
        )

