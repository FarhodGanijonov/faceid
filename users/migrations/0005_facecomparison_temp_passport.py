# Generated by Django 5.2.3 on 2025-06-14 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_abstractuser_gmail_alter_abstractuser_telegram'),
    ]

    operations = [
        migrations.AddField(
            model_name='facecomparison',
            name='temp_passport',
            field=models.ImageField(blank=True, null=True, upload_to='temp/'),
        ),
    ]
