# Generated by Django 3.2.9 on 2022-04-07 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_remove_user_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='point',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
