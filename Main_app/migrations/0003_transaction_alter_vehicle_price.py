# Generated by Django 4.2.7 on 2023-11-23 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main_app', '0002_vehicle_created_at_alter_profile_location_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=15)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('merchant_request_id', models.CharField(max_length=50, unique=True)),
                ('checkout_request_id', models.CharField(max_length=50, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('error', 'Error'), ('success', 'Success')], default='pending', max_length=10)),
            ],
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
