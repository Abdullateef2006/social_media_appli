# Generated by Django 5.0.6 on 2024-10-09 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(upload_to='profile_pics/'),
        ),
    ]
