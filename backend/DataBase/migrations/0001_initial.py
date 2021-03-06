# Generated by Django 2.2.4 on 2019-10-29 00:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('ID', models.IntegerField(primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=100)),
                ('Place', models.CharField(max_length=100)),
                ('StartTime', models.DateField()),
                ('EndTime', models.DateField()),
                ('SignUpStartTime', models.DateField()),
                ('SignUpEndTime', models.DateField()),
                ('MinUser', models.IntegerField()),
                ('MaxUser', models.IntegerField()),
                ('Type', models.CharField(max_length=100)),
                ('Status', models.IntegerField(choices=[(0, 'Except'), (1, 'BeforeSignup'), (2, 'Signup'), (3, 'SignupPaused'), (4, 'SignupStopped'), (5, 'Signin'), (6, 'SigninPaused'), (7, 'Finish')])),
                ('CanBeSearched', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('Name', models.CharField(max_length=30)),
                ('OpenID', models.CharField(max_length=30, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='JoinInformation',
            fields=[
                ('ID', models.IntegerField(primary_key=True, serialize=False)),
                ('JoinTime', models.DateField()),
                ('CheckTime', models.DateField()),
                ('Status', models.IntegerField(choices=[(0, 'WaitValidate'), (1, 'Joined'), (2, 'NotChecked'), (3, 'Checked'), (4, 'Finished'), (5, 'Missed')])),
                ('ActivityId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DataBase.Activity')),
                ('UserId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DataBase.User')),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('ID', models.IntegerField(primary_key=True, serialize=False)),
                ('StartYear', models.IntegerField()),
                ('Department', models.CharField(max_length=30)),
                ('Type', models.CharField(choices=[('U', 'Undergraduate'), ('M', 'Master'), ('D', 'Doctor')], max_length=1)),
                ('Student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DataBase.User')),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='Creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DataBase.User'),
        ),
    ]
