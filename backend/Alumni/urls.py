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
from . import DatabaseActivityManager
from . import DataBaseGlobalFunctions
from . import DatabaseJudgeValid
from . import DatabaseUserManager
from . import RequestHandler

from . import SearchAndRecommend
WordList = ["校友第一次聚餐活动","校友团体聚会活动","计算机系出游","计算机系软件学院团体聚餐","郊游团建和聚餐","软件学院","计算机系","聚餐","集体聚餐","集体聚餐","集体活动","团队建设"]
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
#DataBaseGlobalFunctions.GenerateSessionID()

#SearchAndRecommand.test()
TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
#TheSearcher.SearchInfo("校友聚餐")
#TheSearcher.AddOneInfo(8,"聚餐之王--电子恰猪肉团体聚餐")
#TheSearcher.DeleteOneInfo(7)
#TheSearcher.UpdateOneInfo(5,"贵系恰清真饭聚个锤子餐")
#TheSearcher.SearchInfo("校友聚餐")
#print(DatabaseUserManager.AddUserID("13d","bbb", "bbb"))

urlpatterns = [
    url(r'^login$', RequestHandler.LoginUser),
    url(r'^alumniCheck$', RequestHandler.GetAlumniInfo),
    url(r'^qhrcallback$', RequestHandler.ReceiveAlunmiInfo),
    url(r'^userData$', RequestHandler.QueryUser),
    url(r'^setAvatarUrl$', RequestHandler.SetAvatarURL),
    url(r'^createActivity$', RequestHandler.StartActivity),
    url(r'^joinActivity$', RequestHandler.JoinActivity),
    url(r'^cancelJoinActivity$', RequestHandler.QuitActivity),
    url(r'^getAllActivity$', RequestHandler.GetActivityList),
    url(r'^getActivityInfo$', RequestHandler.QueryActivity),
    url(r'^getSelfActivity$', RequestHandler.QuerySelfActivity),
    url(r'^getAllParticipants$', RequestHandler.QueryAllParticipants),
    url(r'^getAllParticipantsAdmin$', RequestHandler.QueryAllParticipantsAdmin),
    url(r'^needReview$', RequestHandler.QueryAllAuditParticipants),
    url(r'^modifyActivity$', RequestHandler.ChangeActivity),
    url(r'^changeUserRole$', RequestHandler.ChangeUserStatus),
    url(r'^handleAudit$', RequestHandler.AuditUser),
    url(r'^deleteActivity$', RequestHandler.DeleteActivity),
    url(r'^activityTypesList$', RequestHandler.QueryActivityTypes),
    url(r'^educationTypesList$', RequestHandler.QueryEducationTypes),
    url(r'^departmentsList$', RequestHandler.QueryDepartments),
    url(r'^searchActivity$', RequestHandler.SearchActivity),
    url(r'^recommendByActivity$', RequestHandler.RecommendActivityByActivity),
    url(r'^recommendByUser$', RequestHandler.RecommendActivityByUser),

]