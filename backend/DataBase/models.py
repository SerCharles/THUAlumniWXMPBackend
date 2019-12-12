from django.db import models
 
 
class GlobalVariables(models.Model):
    AppId = models.CharField(max_length = 100)
    SecretId = models.CharField(max_length = 100)
    AccessToken = models.CharField(max_length = 300, default = "UNDEFINED")


class User(models.Model):
    ID = models.AutoField(primary_key = True)
    Name = models.CharField(max_length = 30)
    OpenID = models.CharField(max_length = 100, unique = True)
    Session = models.CharField(max_length = 100)
    SessionKey = models.CharField(max_length = 300)
    RequestID = models.CharField(max_length = 300)
    AvatarURL = models.CharField(max_length = 300)
    Valid = models.BooleanField(default = False)
    Status = models.BooleanField(default = True)

class Admin(models.Model):
    ID = models.AutoField(primary_key = True)
    Username = models.CharField(max_length = 30, unique = True)
    Password = models.CharField(max_length = 30)
    Session = models.CharField(max_length = 100, default = "UNDEFINED")

class Education(models.Model):
    ID = models.AutoField(primary_key = True)
    Student = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "Education")
    StartYear = models.IntegerField()
    Department = models.CharField(max_length = 30)
    Type = models.CharField(max_length = 30)

class Activity(models.Model):
    STATUS_TYPE_GLOBAL_ACTIVITY = (
        (0,'Except'),
        (1,'Normal'),
        (2,'Finish'),
    )
    STATUS_TYPE_JOIN_CHECK_ACTIVITY = (
        (0,'Before'),
        (1,'Continue'),
        (2,'Paused'),
        (3,'Stopped'),
    )
    RULE_TYPE_ACTIVITY = (
        (0, "Accept"),
        (1, "Audit"),
        (2, "Reject"),
    )
    ID = models.AutoField(primary_key = True)
    Name = models.CharField(max_length = 100)
    Place = models.CharField(max_length = 100)
    StartTime = models.IntegerField()
    EndTime = models.IntegerField()
    SignUpStartTime = models.IntegerField()
    SignUpEndTime = models.IntegerField()
    CreateTime = models.IntegerField()
    MinUser = models.IntegerField()
    CurrentUser = models.IntegerField()
    MaxUser = models.IntegerField()
    Type = models.CharField(max_length = 100)
    StatusGlobal = models.IntegerField(choices = STATUS_TYPE_GLOBAL_ACTIVITY)
    StatusJoin = models.IntegerField(choices = STATUS_TYPE_JOIN_CHECK_ACTIVITY)
    StatusCheck = models.IntegerField(choices = STATUS_TYPE_JOIN_CHECK_ACTIVITY)
    CanBeSearched = models.BooleanField()
    GlobalRule = models.IntegerField(choices = RULE_TYPE_ACTIVITY)
    Tags = models.CharField(max_length = 300)
    ImageURL = models.CharField(max_length = 300)
    Description = models.TextField()
    Code = models.CharField(max_length = 100, default = "UNDEFINED")

class AdvancedRule(models.Model):
    RULE_TYPE = (
        (0, "Accept"),
        (1, "Audit"),
        (2, "Reject"),
    )
    ID = models.AutoField(primary_key = True)
    ActivityId = models.ForeignKey(Activity, on_delete = models.CASCADE, related_name = "AdvancedRule")
    MinStartYear = models.IntegerField()
    MaxStartYear = models.IntegerField()
    Department = models.CharField(max_length = 30)
    EducationType = models.CharField(max_length = 30)
    Type = models.IntegerField(choices = RULE_TYPE)

class JoinInformation(models.Model):
    STATUS_TYPE_JOIN = (
        (0, "WaitValidate"),  
        (1, "Joined"),
        (2, "Checked"),
        (3, "Finished"),
        (4, "FinishedWithoutCheck"),
        (5, "Abnormal"),
        (6, "Refused"),
    )
    ROLE_TYPE_JOIN = (
        (0, "Commoner"),
        (1, "Manager"),
        (2, "Creator") 
    )
    ID = models.AutoField(primary_key = True)
    SubmitTime = models.IntegerField()
    JoinTime = models.IntegerField()
    CheckTime = models.IntegerField()
    Status = models.IntegerField(choices = STATUS_TYPE_JOIN)
    Role = models.IntegerField(choices = ROLE_TYPE_JOIN)
    UserId = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "History")
    ActivityId = models.ForeignKey(Activity, on_delete = models.CASCADE, related_name = "History")
    JoinReason = models.CharField(max_length = 310)

class ReportInformation(models.Model):
    ID = models.AutoField(primary_key = True)
    SubmitTime = models.IntegerField()
    UserId = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "ReportList")
    ActivityId = models.ForeignKey(Activity, on_delete = models.CASCADE, related_name = "ReportList")
    Reason = models.CharField(max_length = 310)

class Department(models.Model):
    ID = models.AutoField(primary_key = True)
    Name = models.CharField(max_length = 300)
 
class EducationType(models.Model):
    ID = models.AutoField(primary_key = True)
    Name = models.CharField(max_length = 300)

class ActivityType(models.Model):
    ID = models.AutoField(primary_key = True)
    Name = models.CharField(max_length = 300)

def GeneratePictureURL(TheInstance, TheFileName):
    TheExtention = TheFileName.split('.').pop()
    TheMainFileName = TheFileName[ : 0 - len(TheExtention) - 1]
    TheFileName = TheMainFileName + '_' + str(TheInstance.CreateTime) + '.' + TheExtention
    return TheFileName

class Picture(models.Model):
    ID = models.AutoField(primary_key = True)
    CreateTime = models.IntegerField()
    Image = models.ImageField(upload_to = GeneratePictureURL)

