# Generated by Django 4.0.6 on 2023-02-23 22:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('liming', '0005_alter_applicationrate_options_alter_farmer_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='applicationrate',
            options={'verbose_name': 'Formularz aplikacji nawozów', 'verbose_name_plural': 'Formularze aplikacji nawozów'},
        ),
        migrations.AddField(
            model_name='order',
            name='creation_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
