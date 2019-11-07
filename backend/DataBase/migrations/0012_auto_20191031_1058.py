# Generated by Django 2.2.4 on 2019-10-31 02:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0011_auto_20191030_1925'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='Creator',
        ),
        migrations.AddField(
            model_name='activity',
            name='Member',
            field=models.ManyToManyField(related_name='Activity', through='DataBase.JoinInformation', to='DataBase.User'),
        ),
        migrations.AddField(
            model_name='joininformation',
            name='Role',
            field=models.IntegerField(choices=[(0, 'Common'), (1, 'Manager'), (2, 'Creator')], default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='joininformation',
            name='ActivityId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='History', to='DataBase.Activity'),
        ),
        migrations.AlterField(
            model_name='joininformation',
            name='Status',
            field=models.IntegerField(choices=[(0, 'WaitValidate'), (1, 'Joined'), (2, 'NotChecked'), (3, 'Checked'), (4, 'Finished'), (5, 'Missed')]),
        ),
        migrations.AlterField(
            model_name='joininformation',
            name='UserId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='History', to='DataBase.User'),
        ),
    ]
