# Generated by Django 5.1.1 on 2024-10-01 04:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HealthMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(help_text='Weight in kilograms')),
                ('systolic_bp', models.IntegerField(help_text='Systolic blood pressure in mmHg')),
                ('diastolic_bp', models.IntegerField(help_text='Diastolic blood pressure in mmHg')),
                ('heart_rate', models.IntegerField(help_text='Heart rate in beats per minute')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='health_metrics', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
