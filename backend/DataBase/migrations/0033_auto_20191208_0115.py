# Generated by Django 2.2.4 on 2019-12-07 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0032_auto_20191207_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='Session',
            field=models.CharField(default='UNDEFINED', max_length=100),
        ),
    ]
