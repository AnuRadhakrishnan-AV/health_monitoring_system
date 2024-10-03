from django.db import models
from django.contrib.auth.models import AbstractUser

#user model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('healthcare_provider', 'Healthcare Provider'),
        ('patient', 'Patient'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default='patient')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"



class HealthMetric(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_metrics')
    age=models.IntegerField(null=True)
    weight = models.FloatField(help_text="Weight in kilograms")
    systolic_bp = models.IntegerField(help_text="Systolic blood pressure in mmHg")
    diastolic_bp = models.IntegerField(help_text="Diastolic blood pressure in mmHg")
    heart_rate = models.IntegerField(help_text="Heart rate in beats per minute")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d')}"



class HealthGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_description = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=(('active', 'Active'), ('completed', 'Completed')))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"



class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_text = models.TextField(help_text="Personalized health recommendation")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"



class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    content = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} on {self.recommendation.id}"


