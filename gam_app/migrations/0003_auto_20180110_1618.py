# Generated by Django 2.0.1 on 2018-01-10 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gam_app', '0002_auto_20180109_2142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caso',
            name='caja_no',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='caso',
            name='carpeta_no',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='caso',
            name='legajo_no',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='imagen',
            name='caja',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='imagen',
            name='carpeta',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='imagen',
            name='legajo',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
