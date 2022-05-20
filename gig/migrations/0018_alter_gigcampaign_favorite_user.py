# Generated by Django 3.2.9 on 2022-04-06 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_user_avater'),
        ('gig', '0017_auto_20220406_2248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gigcampaign',
            name='favorite_user',
            field=models.ManyToManyField(blank=True, db_table='gig_campaign_favorite', related_name='favorite_user_set', to='account.User'),
        ),
    ]
