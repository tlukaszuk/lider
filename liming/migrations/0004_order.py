# Generated by Django 4.0.6 on 2023-02-23 21:35

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('liming', '0003_alter_growingfield_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.CharField(max_length=202)),
                ('growing_fields', models.CharField(max_length=200)),
                ('lider_ca_weight', models.FloatField()),
                ('lider_mg_weight', models.FloatField()),
                ('lider_ca_price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='cena Lider Ca')),
                ('lider_mg_price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='cena Lider Mg')),
                ('packing_type', models.CharField(choices=[('P', 'Paleta'), ('B', 'Big bag')], max_length=1, verbose_name='rodzaj opakowania')),
                ('operator', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='liming.farmer')),
            ],
        ),
    ]
