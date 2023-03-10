# Generated by Django 4.0.6 on 2023-02-13 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('liming', '0002_alter_farmer_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='growingfield',
            options={'ordering': ['field_number']},
        ),
        migrations.AlterUniqueTogether(
            name='growingfield',
            unique_together={('farmer', 'field_number', 'parcel_number')},
        ),
    ]
