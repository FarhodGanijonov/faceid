# Generated by Django 5.2.3 on 2025-06-19 18:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('address', models.CharField(max_length=255)),
                ('district', models.CharField(max_length=100)),
                ('room_count', models.IntegerField()),
                ('description', models.TextField()),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('contacts_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='houses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='House_image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='house_image')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='house.house')),
            ],
        ),
    ]
