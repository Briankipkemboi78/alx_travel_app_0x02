# Generated by Django 4.2.18 on 2025-02-06 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0003_alter_payment_booking_reference_alter_payment_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
