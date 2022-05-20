# Generated by Django 3.2.9 on 2022-04-06 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gig', '0010_alter_gigcampaign_merchant'),
    ]

    operations = [
        migrations.AddField(
            model_name='gigcampaign',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gigcampaign',
            name='merchant',
            field=models.CharField(max_length=5),
        ),
    ]
