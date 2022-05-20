# Generated by Django 3.2.9 on 2022-04-07 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_user_avater'),
        ('gig', '0021_remove_gigcampaignfavorite_place'),
    ]

    operations = [
        migrations.AddField(
            model_name='gigcampaign',
            name='favorite_user',
            field=models.ManyToManyField(blank=True, related_name='like_user_set', through='gig.GigCampaignFavorite', to='account.User'),
        ),
    ]