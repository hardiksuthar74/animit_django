# Generated by Django 5.0.4 on 2024-04-24 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_useranimestatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='useranimestatus',
            name='episodes',
            field=models.IntegerField(default=0),
        ),
    ]
