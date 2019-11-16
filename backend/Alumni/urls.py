"""Alumni URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
<<<<<<< HEAD
from . import DatabaseActivityManager
from . import DataBaseGlobalFunctions
from . import DatabaseJudgeValid
from . import DatabaseUserManager
from . import RequestHandler

info = {
"requestId": "4a157c9c-f069-460b-9e89-718b4778942e",
"user": {
"legalIdentity": {
"legalName": "烤肉串"
},
"campusIdentity": [
{
"enrollmentYear": "2014",
"department": "伊斯兰教法学院",
"enrollmentType": "阿訇"
},
{
"enrollmentYear": "2018",
"department": "伊斯兰教法学院",
"enrollmentType": "伊玛目"
}
]
}
}
#DatabaseManager.AddUser(info)
=======
from . import DatabaseManager
from . import RequestHandler

info = {
    "openid":"2017013569",
    "name": "沈冠霖",
    "campusIdentity": [
    {
      "enrollmentYear": "2017",
      "department": "软件学院",
      "enrollmentType": "Undergraduate"
    },
    {
      "enrollmentYear": "2021",
      "department": "软件学院",
      "enrollmentType": "Doctor"
    }
  ]
    }
#DatabaseManager.AddUser(info["openid"], info["name"], info["campusIdentity"])
>>>>>>> 82e159b3c648f0b186de5ef338522a67d18d598c
Information = {"name":"第三次瓜分波兰", "place":"华沙", "start":"2019-11-28 08:00:00","end":"2019-11-28 12:00:00", "minUser":"3", "maxUser":"100", "type":"个人活动-聚餐", "status":"1","canBeSearched":"True"}
NewInformation = {"id":1, "name":"bork", "start":"2019-11-08 08:00:00", "minUser":1, "maxUser":5, "status":2}
ChangeUserInformation = {"openId":"2017013569", "activityId":1, "newStatus":5, "newRole":0}
#DatabaseManager.AddActivity("xxxxx",Information)
#DatabaseManager.JoinActivity(info["openid"], 1, False)
#print(DatabaseManager.ShowAllActivity())
#print(DatabaseManager.QueryActivity(0))
#print(DatabaseManager.QueryActivity(1))
#print(DatabaseManager.ShowSelfActivity("2017013569"))
#print(DatabaseManager.ShowSelfActivity("xxxxx"))
#print(DatabaseManager.ShowAllMembers(1))
#print(DatabaseManager.ChangeUserStatus("xxxxx", ChangeUserInformation))
<<<<<<< HEAD
#DatabaseManager.GenerateSessionID()

urlpatterns = [
    url(r'^login$', RequestHandler.LoginUser),
    url(r'^alumniCheck$', RequestHandler.GetAlumniInfo),
    url(r'^qhrcallback$', RequestHandler.ReceiveAlunmiInfo),
=======


urlpatterns = [
>>>>>>> 82e159b3c648f0b186de5ef338522a67d18d598c
    url(r'^userData$', RequestHandler.QueryUser),
    url(r'^createActivity$', RequestHandler.StartActivity),
    url(r'^joinActivity$', RequestHandler.JoinActivity),
    url(r'^getAllActivity$', RequestHandler.GetActivityList),
    url(r'^getActivityInfo$', RequestHandler.QueryActivity),
    url(r'^getSelfActivity$', RequestHandler.QuerySelfActivity),
    url(r'^getAllParticipants$', RequestHandler.QueryAllParticipants),
<<<<<<< HEAD
    url(r'^getAllParticipantsAdmin$', RequestHandler.QueryAllParticipantsAdmin),
    url(r'^needReview$', RequestHandler.QueryAllAuditParticipants),
    url(r'^modifyActivity$', RequestHandler.ChangeActivity),
    url(r'^changeUserRole$', RequestHandler.ChangeUserStatus),
    url(r'^handleAudit$', RequestHandler.AuditUser),
    url(r'^deleteActivity$', RequestHandler.DeleteActivity),
    url(r'^activityTypesList$', RequestHandler.QueryActivityTypes),
    url(r'^educationTypesList$', RequestHandler.QueryEducationTypes),
    url(r'^departmentsList$', RequestHandler.QueryDepartments),

=======
    url(r'^modifyActivity$', RequestHandler.ChangeActivity),
    url(r'^changeUserRole$', RequestHandler.ChangeUserStatus),
    url(r'^deleteActivity$', RequestHandler.DeleteActivity),
>>>>>>> 82e159b3c648f0b186de5ef338522a67d18d598c
]