# Generated by Django 3.2.9 on 2022-04-11 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0021_alter_user_avater'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='birth_year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
