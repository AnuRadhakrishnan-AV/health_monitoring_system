from django.contrib import admin
from .models import User,HealthMetric,Recommendation,HealthGoal,Feedback

admin.site.register(User)
admin.site.register(HealthMetric)
admin.site.register(Recommendation)
admin.site.register(HealthGoal)
admin.site.register(Feedback)