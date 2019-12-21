# Generated by Django 2.2.4 on 2019-12-21 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0035_globalvariables_accesstoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='GPSPlace',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='ExtraData',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='Point',
            field=models.IntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='globalvariables',
            name='AccessToken',
            field=models.CharField(default='UNDEFINED', max_length=300),
        ),
    ]
