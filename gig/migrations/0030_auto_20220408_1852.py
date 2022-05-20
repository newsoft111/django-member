# Generated by Django 3.2.9 on 2022-04-08 18:52

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_auto_20220408_1221'),
        ('gig', '0029_auto_20220408_1851'),
    ]

    operations = [
        migrations.CreateModel(
            name='GigCampaignOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appeal', models.CharField(max_length=255)),
                ('offer_at', models.DateTimeField(default=datetime.datetime.now)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gig.gigcampaign')),
                ('shipping_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.usershippingaddress')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.user')),
            ],
            options={
                'db_table': 'gig_campaign_offer',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='gigcampaign',
            name='offer_user',
            field=models.ManyToManyField(blank=True, related_name='offer_user_set', through='gig.GigCampaignOffer', to='account.User'),
        ),
    ]
