from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import UserSerializer,LoginSerializer,HealthMetricSerializer,HealthGoalSerializer,RecommendationSerializer,FeedbackSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User,HealthMetric,HealthGoal,Recommendation,Feedback
from .permissions import IsAdminUser,IsHealthcareProvider
import pickle
import numpy as np
import joblib
import pandas as pd
from .tasks import process_health_recommendation_task


#user registration view [POST]    (username,first_name, last_name, email, password,confirmed_password)

class RegisterUserView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        
        
        if serializer.is_valid():
            user = serializer.save()

            return Response({
                'status': "success",
                'message': 'User registered successfully',
                'response_code': status.HTTP_201_CREATED,
                'data': UserSerializer(user).data 
            }, status=status.HTTP_201_CREATED)

        
        else:
            return Response({
                'status': "failed",
                'message': "User registration failed",
                'response_code': status.HTTP_400_BAD_REQUEST,
                'data': serializer.errors 
            }, status=status.HTTP_400_BAD_REQUEST)

#login view [POST]( JWT )

class LoginUserView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            user = authenticate(username=username, password=serializer.validated_data['password'])

            
            refresh = RefreshToken.for_user(user)

            return Response({
                'status': "success",
                'message': 'Login successful',
                'response_code': status.HTTP_200_OK,
                'data': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'status': "failed",
            'message': "Login failed",
            'response_code': status.HTTP_400_BAD_REQUEST,
            'data': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

#  Users health metrics [GET]

class HealthMetricView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        health_metrics = HealthMetric.objects.filter(user=user).order_by('-timestamp')

        if health_metrics.exists():
            serializer = HealthMetricSerializer(health_metrics, many=True)
            return Response({
                "status": 'success',
                "message": "Health metrics fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": 'failed',
                "message": "No health metrics found for this user",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)


#add health metrics [POST]

class AddHealthMetricView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        
        required_fields = ['age','weight', 'systolic_bp', 'diastolic_bp', 'heart_rate']

        
        missing_fields = [field for field in required_fields if field not in data]
        
        
        if missing_fields:
            return Response({
                'status': 'failed',
                'message': f'Missing fields: {", ".join(missing_fields)}',
                'response_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        
        health_metric = HealthMetric(
            user=user, 
            age=data['age'],
            weight=data['weight'],
            systolic_bp=data['systolic_bp'],
            diastolic_bp=data['diastolic_bp'],
            heart_rate=data['heart_rate']
        )
        health_metric.save()

        
        return Response({
            'status': 'success',
            'message': 'Health metric added successfully',
            'data': {
                'id': health_metric.id,
                'user': health_metric.user.username,
                'age': health_metric.age,
                'weight': health_metric.weight,
                'systolic_bp': health_metric.systolic_bp,
                'diastolic_bp': health_metric.diastolic_bp,
                'heart_rate': health_metric.heart_rate,
                'timestamp': health_metric.timestamp
            }
        }, status=status.HTTP_201_CREATED)

#update health_metrics [PATCH]

class HealthMetricUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        health_metric = HealthMetric.objects.filter(pk=pk, user=request.user).first()
        
        if not health_metric:
            return Response({
                "status": 'failed',
                "message": "Health metric not found",
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = HealthMetricSerializer(health_metric, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 'success',
                "message": "Health metric updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": 'failed',
            "message": "Error in updating health metric",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

#delete health metric [DELETE]

class HealthMetricDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        health_metric = HealthMetric.objects.filter(pk=pk, user=request.user).first()
        
        if not health_metric:
            return Response({
                "status": 'failed',
                "message": "Health metric not found",
            }, status=status.HTTP_404_NOT_FOUND)

        health_metric.delete()
        return Response({
            "status": 'success',
            "message": "Health metric deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

# user health goal [GET]

class HealthGoalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        health_goals = HealthGoal.objects.filter(user=user).order_by('-created_at')

        if health_goals.exists():
            serializer = HealthGoalSerializer(health_goals, many=True)
            return Response({
                "status": 'success',
                "message": "Health goals fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": 'failed',
                "message": "No health goals found for this user",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)


#health goals add [POST]

class AddHealthGoalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        
        required_fields = ['goal_description', 'status']

        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response({
                'status': 'failed',
                'message': f'Missing fields: {", ".join(missing_fields)}',
                'response_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        
        if data['status'] not in ['active', 'completed']:
            return Response({
                'status': 'failed',
                'message': 'Invalid status value. Must be "active" or "completed".',
                'response_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        
        health_goal = HealthGoal(
            user=user,
            goal_description=data['goal_description'],
            status=data['status']
        )
        health_goal.save()

        
        serializer = HealthGoalSerializer(health_goal)

        return Response({
            'status': 'success',
            'message': 'Health goal added successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

#update health goal [PATCH]

class HealthGoalUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        health_goal = HealthGoal.objects.filter(pk=pk, user=request.user).first()
        
        if not health_goal:
            return Response({
                "status": 'failed',
                "message": "Health goal not found",
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = HealthGoalSerializer(health_goal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 'success',
                "message": "Health goal updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": 'failed',
            "message": "Error in updating health goal",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


#delete health goal [DELETE]

class HealthGoalDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        health_goal = HealthGoal.objects.filter(pk=pk, user=request.user).first()
        
        if not health_goal:
            return Response({
                "status": 'failed',
                "message": "Health goal not found",
            }, status=status.HTTP_404_NOT_FOUND)

        health_goal.delete()
        return Response({
            "status": 'success',
            "message": "Health goal deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)



# View to fetch health data of users(health metrics,health goals)

class HealthDataAndRecommendationView(APIView):
    permission_classes = [IsAuthenticated, IsHealthcareProvider|IsAdminUser]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')

        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "status": status.HTTP_404_NOT_FOUND,
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)

       
        health_metrics = HealthMetric.objects.filter(user=user)
        health_goals = HealthGoal.objects.filter(user=user)

        if not health_metrics.exists():
            return Response({
                "success": False,
                "status": status.HTTP_404_NOT_FOUND,
                "message": "No health metrics found for the user."
            }, status=status.HTTP_404_NOT_FOUND)

        if not health_goals.exists():
            return Response({
                "success": False,
                "status": status.HTTP_404_NOT_FOUND,
                "message": "No health goals found for the user."
            }, status=status.HTTP_404_NOT_FOUND)

        
        health_metrics_serializer = HealthMetricSerializer(health_metrics, many=True)
        health_goals_serializer = HealthGoalSerializer(health_goals, many=True)

        return Response({
            "success": True,
            "status": status.HTTP_200_OK,
            "health_metrics": health_metrics_serializer.data,
            "health_goals": health_goals_serializer.data
        }, status=status.HTTP_200_OK)

 
#create recommendation for health data 

class AddHealthRecommendationView(APIView):
    permission_classes = [IsAuthenticated, IsHealthcareProvider|IsAdminUser]


    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        recommendation_text = request.data.get('recommendation_text')

        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "status": status.HTTP_404_NOT_FOUND,
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)

        
        health_metrics = HealthMetric.objects.filter(user=user)
        health_goals = HealthGoal.objects.filter(user=user)

        if not health_metrics.exists():
            return Response({
                "success": False,
                "status": status.HTTP_404_NOT_FOUND,
                "message": "No health metrics found for the user."
            }, status=status.HTTP_404_NOT_FOUND)

        if not health_goals.exists():
            return Response({
                "success": False,
                "status": status.HTTP_404_NOT_FOUND,
                "message": "No health goals found for the user."
            }, status=status.HTTP_404_NOT_FOUND)

        if recommendation_text:
            recommendation_data = {
                "user": user.id,
                "recommendation_text": recommendation_text
            }

            serializer = RecommendationSerializer(data=recommendation_data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": status.HTTP_201_CREATED,
                    "message": "Recommendation created successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                "success": False,
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid data.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": False,
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Recommendation text is required."
        }, status=status.HTTP_400_BAD_REQUEST)


#user feedback retrieve [GET]

class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, recommendation_id=None, *args, **kwargs):
        if recommendation_id:
            feedback = Feedback.objects.filter(recommendation_id=recommendation_id).order_by('-created_at')
        else:
            feedback = Feedback.objects.filter(user=request.user).order_by('-created_at')

        if feedback.exists():
            serializer = FeedbackSerializer(feedback, many=True)
            return Response({
                "status": 'success',
                "message": "Feedback fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": 'failed',
                "message": "No feedback found",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

#add feedback [POST]


class AddFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        
        required_fields = ['recommendation', 'content']

        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response({
                'status': 'failed',
                'message': f'Missing fields: {", ".join(missing_fields)}',
                'response_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

       
        feedback = Feedback(
            user=user,  
            recommendation_id=data['recommendation'],  
            content=data['content']
        )
        feedback.save()

        
        serializer = FeedbackSerializer(feedback)

        return Response({
            'status': 'success',
            'message': 'Feedback added successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


#feedback list (admin & healthcare provider)

class FeedbackListView(APIView):
   
    permission_classes = [IsAuthenticated, IsAdminUser| IsHealthcareProvider]

    def get(self, request, *args, **kwargs):
        
        feedback = Feedback.objects.all()

       
        if not feedback.exists():
            return Response({
                "success": False,
                "status": status.HTTP_404_NOT_FOUND,
                "message": "No feedback found.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

       
        serializer = FeedbackSerializer(feedback, many=True)

     
        return Response({
            "success": True,
            "status": status.HTTP_200_OK,
            "message": "feedback fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


#######################################################  ML MODEL INTEGRATION   ######################################################################

# personalized recommentation using machine learning model[RandomForest classifier]

class RecommendationView(APIView):
    """View to provide health recommendations based on health metrics."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = joblib.load('C:/Users/hp/Desktop/Healthcare_system/healthcare/healthcare/health_recommendation_model.pkl')

    def post(self, request, *args, **kwargs):
        serializer = HealthMetricSerializer(data=request.data)
        if serializer.is_valid():
            # Save the health metric data
            health_metric = serializer.save()

            # Prepare input data for the model
            input_data = {
                'weight': health_metric.weight,
                'systolic_bp': health_metric.systolic_bp,
                'diastolic_bp': health_metric.diastolic_bp,
                'heart_rate': health_metric.heart_rate,
                'age': health_metric.age,
                'user_id': health_metric.user.id  
            }

            # Trigger the Celery task to process the recommendation asynchronously
            task = process_health_recommendation_task.delay(input_data)

            return Response({
                'status': 'success',
                'message': 'Recommendation processing started.',
                'task_id': task.id,
                'response_code': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 'failed',
            'message': 'Invalid data',
            'response_code': status.HTTP_400_BAD_REQUEST,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
