# Generated by Django 4.2.1 on 2023-05-22 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_product_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orderData', models.CharField(max_length=200)),
                ('orderCart', models.CharField(max_length=200)),
                ('orderOrder', models.CharField(max_length=200)),
                ('orderItems', models.CharField(max_length=200)),
            ],
        ),
    ]
