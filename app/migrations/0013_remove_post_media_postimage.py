# Generated by Django 5.0.6 on 2024-10-21 10:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_searchhistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='media',
        ),
        migrations.CreateModel(
            name='PostImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(blank=True, upload_to='medias/')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app.post')),
            ],
        ),
    ]
