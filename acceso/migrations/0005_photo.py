# Generated by Django 2.1.2 on 2019-03-01 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acceso', '0004_auto_20190207_1550'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.CharField(blank=True, max_length=200)),
                ('folder', models.CharField(blank=True, max_length=200)),
                ('filtros', models.ManyToManyField(blank=True, related_name='photo_filtros', to='acceso.Filtros')),
            ],
        ),
    ]
