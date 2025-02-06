# Generated by Django 4.2.18 on 2025-02-06 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0002_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='booking_reference',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='Pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(default='46867a9781d840fb8eec322e4da6e473', max_length=255, unique=True),
        ),
    ]
