# Generated by Django 5.0.2 on 2025-03-02 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('joo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('order_id', models.CharField(max_length=255, unique=True)),
                ('customer_email', models.CharField(max_length=255)),
                ('restaurant_id', models.IntegerField()),
                ('restaurant_email', models.CharField(max_length=255)),
                ('restaurant_name', models.CharField(max_length=255)),
                ('booking_date', models.DateTimeField()),
                ('order_type', models.CharField(max_length=20)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('items', models.TextField(blank=True, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'joo_order',
                'ordering': ['-booking_date'],
            },
        ),
    ]
