# Generated by Django 5.1.6 on 2025-03-09 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='expiry_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
