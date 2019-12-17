'''
url绑定函数和初始化
'''


'''WordList = ["校友第一次聚餐活动","校友团体聚会活动","计算机系出游","计算机系软件学院团体聚餐","郊游团建和聚餐","软件学院","计算机系","聚餐","集体聚餐","集体聚餐","集体活动","团队建设"]
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
#TheSearcher.SearchInfo("校友聚餐")
#TheSearcher.AddOneInfo(8,"聚餐之王--电子恰猪肉团体聚餐")
#TheSearcher.DeleteOneInfo(7)
#TheSearcher.UpdateOneInfo(5,"贵系恰清真饭聚个锤子餐")
#TheSearcher.SearchInfo("校友聚餐")
#print(DatabaseUserManager.AddUserID("13d","bbb", "bbb"))'''


from django.contrib import admin
from django.conf.urls import url
from django.views.static import serve
from Alumni.settings import MEDIA_ROOT
from Alumni.LogicManager.Constants import Constants
from Alumni.LogicManager import GlobalFunctions
from Alumni.LogicManager import JudgeValid
from Alumni.DatabaseManager import UserManager
from Alumni.DatabaseManager import ActivityManager
from Alumni.DatabaseManager import UserActivityManager
from Alumni.DatabaseManager import SearchAndRecommend
from Alumni.DatabaseManager import AdminManager
from Alumni.DatabaseManager import TimeManager
from Alumni.RequestHandler import UserHandler
from Alumni.RequestHandler import ActivityHandler
from Alumni.RequestHandler import UserActivityHandler
from Alumni.RequestHandler import SearchHandler
from Alumni.RequestHandler import OtherHandler
from Alumni.RequestHandler import AdminHandler

TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
print(GlobalFunctions.SetAccessToken())
print(GlobalFunctions.GetAccessToken())
#AdminManager.AddAdmin("kebab","reich")


urlpatterns = [
    #处理用户请求url
    url(r'^login$', UserHandler.LoginUser),
    url(r'^alumniCheck$', UserHandler.GetAlumniInfo),
    url(r'^qhrcallback$', UserHandler.ReceiveAlunmiInfo),
    url(r'^userData$', UserHandler.QueryUser),
    url(r'^setAvatarUrl$', UserHandler.SetAvatarURL),

    #处理活动请求url
    url(r'^createActivity$', ActivityHandler.StartActivity),
    url(r'^modifyActivity$', ActivityHandler.ChangeActivity),
    url(r'^modifyActivityDescription$', ActivityHandler.ChangeActivityDetail),
    url(r'^getAllActivity$', ActivityHandler.GetActivityList),
    url(r'^getActivityInfo$', ActivityHandler.QueryActivity),
    url(r'^getActivityDescription$', ActivityHandler.QueryActivityDetail),
    url(r'^deleteActivity$', ActivityHandler.DeleteActivity),
    url(r'^generateCheckinCode$', ActivityHandler.UploadActivityQRCode),
    url(r'^changeActivityByTime$', TimeManager.ChangeActivityByTime),

    #处理用户-活动请求url
    url(r'^joinActivity$', UserActivityHandler.JoinActivity),
    url(r'^checkInActivity$', UserActivityHandler.CheckInActivity),
    url(r'^removeFromActivity$', UserActivityHandler.RemoveFromActivity),
    url(r'^cancelJoinActivity$', UserActivityHandler.QuitActivity),
    url(r'^getSelfActivity$', UserActivityHandler.QuerySelfActivity),
    url(r'^getAllParticipants$', UserActivityHandler.QueryAllParticipants),
    url(r'^getAllParticipantsAdmin$', UserActivityHandler.QueryAllParticipantsAdmin),
    url(r'^needReview$', UserActivityHandler.QueryAllAuditParticipants),
    url(r'^changeUserRole$', UserActivityHandler.ChangeUserRole),
    url(r'^handleAudit$', UserActivityHandler.AuditUser),
    url(r'^reportActivity$', UserActivityHandler.ReportActivity),


    #处理搜索-推荐请求url
    url(r'^searchActivity$', SearchHandler.SearchActivity),
    url(r'^searchActivityAdvanced$', SearchHandler.SearchActivityAdvanced),
    url(r'^recommendByActivity$', SearchHandler.RecommendActivityByActivity),
    url(r'^recommendByUser$', SearchHandler.RecommendActivityByUser),

    #处理其余url
    url(r'^activityTypesList$', OtherHandler.QueryActivityTypes),
    url(r'^educationTypesList$', OtherHandler.QueryEducationTypes),
    url(r'^departmentsList$', OtherHandler.QueryDepartments),
    url(r'^uploadImage$', OtherHandler.UploadPicture),
    url(r'^media/(?P<path>.*)', serve, {"document_root":MEDIA_ROOT}),

    #处理管理员url
    url(r'^adminLogin$', AdminHandler.Login),
    url(r'^adminLogout$', AdminHandler.Logout),
    url(r'^adminGetAllActivity$', AdminHandler.ShowAllActivity),
    url(r'^adminGetReportList$', AdminHandler.ShowAllReport),
    url(r'^adminModifyActivityStatus$', AdminHandler.ChangeActivityStatus),
    url(r'^adminGetActivityInfo$', AdminHandler.ShowOneActivity),
    url(r'^adminGetActivityReportList$', AdminHandler.ShowAllActivityReport),
    url(r'^adminDeleteOneReport$', AdminHandler.DeleteOneReport),
    url(r'^adminDeleteActivityReport$', AdminHandler.DeleteActivityReport),
    url(r'^adminGetAllUser$', AdminHandler.ShowAllUser),
    url(r'^adminUserData$', AdminHandler.ShowOneUser),
    url(r'^adminModifyUser$', AdminHandler.ChangeUserStatus),

    #测试url
    url(r'^testt$', TimeManager.Testt)

]