from rest_framework import serializers
from .models import User,HealthMetric,HealthGoal,Recommendation,Feedback
from django.contrib.auth import authenticate

#user serializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password','role']

        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'password': {'required': True},
            'confirm_password': {'required': True},
        }

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        email = data.get('email')
       

        
        if password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})

        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({"password": "Password must contain at least one digit."})

        if not any(char.isalpha() for char in password):
            raise serializers.ValidationError({"password": "Password must contain at least one letter."})

        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already exists."})

        
        

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  
        password = validated_data.pop('password')
        
        
        user = User(**validated_data)
        user.set_password(password)  
        user.save()
        
        return user

#login serializer

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid username or password.")

        return data

class HealthMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthMetric
        fields = '__all__'


class HealthGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthGoal
        fields = '__all__'

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
     
    class Meta:
        model = Feedback
        fields = '__all__'