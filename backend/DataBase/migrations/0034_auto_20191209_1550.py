# Generated by Django 2.2.4 on 2019-12-09 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0033_auto_20191208_0115'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='Status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='Valid',
            field=models.BooleanField(default=False),
        ),
    ]