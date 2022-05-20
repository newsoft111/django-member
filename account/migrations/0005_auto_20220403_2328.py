# Generated by Django 3.2.9 on 2022-04-03 23:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20220403_2326'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountpoint',
            name='point',
            field=models.BigIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='AccountWithdraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.BigIntegerField(default=0)),
                ('bank', models.CharField(max_length=255)),
                ('is_done', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.user')),
            ],
            options={
                'db_table': 'account_withdraw',
                'managed': True,
            },
        ),
    ]