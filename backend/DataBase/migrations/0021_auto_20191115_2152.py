# Generated by Django 2.2.4 on 2019-11-15 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0020_auto_20191115_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advancedrule',
            name='Type',
            field=models.IntegerField(choices=[(0, 'Accept'), (1, 'Audit'), (2, 'Reject')]),
        ),
    ]
