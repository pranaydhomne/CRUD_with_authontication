# Generated by Django 4.1.5 on 2023-12-19 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='forgot_password_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]