# Generated by Django 3.2.9 on 2022-04-03 23:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20220403_2320'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accountpointlog',
            old_name='user_id',
            new_name='user',
        ),
    ]