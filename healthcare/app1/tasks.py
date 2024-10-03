from celery import shared_task
from .models import Recommendation, User
import pandas as pd
import joblib

# Load  model 
model = joblib.load('C:/Users/hp/Desktop/Healthcare_system/healthcare/healthcare/health_recommendation_model.pkl')

@shared_task
def process_health_recommendation_task(input_data):
    # Prepare input data for the model
    df = pd.DataFrame([input_data])

    # Predict the recommendation
    prediction = model.predict(df[['weight', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'age']])

    # Map the prediction to a recommendation text
    recommendations_mapping = {
        0: "Maintain healthy diet",
        1: "Increase exercise",
        2: "Consult doctor"
    }
    recommendation_text = recommendations_mapping.get(prediction[0], "No recommendation available")

    # Fetch the user and save the recommendation
    user = User.objects.get(id=input_data['user_id'])
    Recommendation.objects.create(user=user, recommendation_text=recommendation_text)

    return recommendation_text
