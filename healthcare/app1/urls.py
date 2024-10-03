from django.urls import path
from .views import (RegisterUserView,LoginUserView,HealthMetricView,AddHealthMetricView,HealthMetricUpdateView,HealthMetricDeleteView,
                     HealthGoalView,AddHealthGoalView,HealthGoalUpdateView,HealthGoalDeleteView,RecommendationView
                    ,HealthDataAndRecommendationView,AddHealthRecommendationView,FeedbackView,AddFeedbackView,FeedbackListView)
                    
                    

urlpatterns = [
     
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),

    path('health-metrics/', HealthMetricView.as_view(), name='health-metrics'),  
    path('health-metrics/add/', AddHealthMetricView.as_view(), name='add-health-metric'),  
    path('health-metrics/<int:pk>/update/', HealthMetricUpdateView.as_view(), name='update-health-metric'),  
    path('health-metrics/<int:pk>/delete/', HealthMetricDeleteView.as_view(), name='delete-health-metric'), 

    path('health_goals/', HealthGoalView.as_view(), name='health_goals'),
    path('health_goals/add/', AddHealthGoalView.as_view(), name='add_health_goal'),
    path('health_goals/<int:pk>/update/', HealthGoalUpdateView.as_view(), name='update_health_goal'),
    path('health_goals/<int:pk>/delete/', HealthGoalDeleteView.as_view(), name='delete_health_goal'),

    
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('recommendation_data/<int:user_id>/', HealthDataAndRecommendationView.as_view(), name='recommendation_data'),
    path('add/health-recommendation/', AddHealthRecommendationView.as_view(), name='add-recommendation'),


    path('feedback/', FeedbackView.as_view(), name='recommendation'),
    path('feedback/add/', AddFeedbackView.as_view(), name='add-recommendation'),
    path('feedback/list/', FeedbackListView.as_view(), name='list-recommendation'),
    
    
    ]