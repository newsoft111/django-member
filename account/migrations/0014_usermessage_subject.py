# Generated by Django 3.2.9 on 2022-04-04 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_usermessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermessage',
            name='subject',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
