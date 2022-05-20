# Generated by Django 3.2.9 on 2022-04-06 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gig', '0008_auto_20220405_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='gigcampaign',
            name='merchant',
            field=models.CharField(default=1, max_length=5),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='gigcampaign',
            name='campaign_type',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='gigcampaign',
            name='category',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='gigcampaign',
            name='channel',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='gigcampaign',
            name='product_url',
            field=models.CharField(blank=True, default=1, max_length=255),
            preserve_default=False,
        ),
    ]
