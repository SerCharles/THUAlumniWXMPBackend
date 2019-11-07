from django.db import models
 
 
class User(models.Model):
    ID = models.AutoField(primary_key = True)
    Name = models.CharField(max_length = 30)
    OpenID = models.CharField(max_length = 100, unique = True)
    Session = models.CharField(max_length = 100)

class Education(models.Model):
    EDUCATION_TYPE = (
        ('U','Undergraduate'),
        ('M','Master'),
        ('D','Doctor'),
    )
    ID = models.AutoField(primary_key = True)
    Student = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "Education")
    StartYear = models.IntegerField()
    Department = models.CharField(max_length = 30)
    Type = models.CharField(max_length = 30, choices = EDUCATION_TYPE)

class Activity(models.Model):
    STATUS_TYPE_ACTIVITY = (
        (0,'Except'),
        (1,'BeforeSignup'),
        (2,'Signup'),
        (3,'SignupPaused'),
        (4,'SignupStopped'),
        (5,'Signin'),
        (6,'SigninPaused'),
        (7,'Finish'),
    )
    ID = models.AutoField(primary_key = True)
    Name = models.CharField(max_length = 100)
    Place = models.CharField(max_length = 100)
    StartTime = models.IntegerField()
    EndTime = models.IntegerField()
    SignUpStartTime = models.IntegerField()
    SignUpEndTime = models.IntegerField()
    MinUser = models.IntegerField()
    CurrentUser = models.IntegerField()
    MaxUser = models.IntegerField()
    Type = models.CharField(max_length = 100)
    Status = models.IntegerField(choices = STATUS_TYPE_ACTIVITY)
    CanBeSearched = models.BooleanField()
    #todo:rule

class JoinInformation(models.Model):
    STATUS_TYPE_JOIN = (
        (0, "WaitValidate"),  
        (1, "Joined"),
        (2, "NotChecked"),
        (3, "Checked"),
        (4, "Finished"),
        (5, "Missed"),
    )
    ROLE_TYPE_JOIN = (
        (0, "Common"),
        (1, "Manager"),
        (2, "Creator") 
    )
    ID = models.AutoField(primary_key = True)
    JoinTime = models.IntegerField()
    CheckTime = models.IntegerField()
    Status = models.IntegerField(choices = STATUS_TYPE_JOIN)
    Role = models.IntegerField(choices = ROLE_TYPE_JOIN)
    UserId = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "History")
    ActivityId = models.ForeignKey(Activity, on_delete = models.CASCADE, related_name = "History")

    #todo:付款等