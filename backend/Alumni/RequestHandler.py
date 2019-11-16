'''
处理请求的函数集合

'''

from django.http import HttpResponse
from django.http import JsonResponse
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
#import numpy as np
#from io import BytesIO
import random
import sqlite3
import sys
import os
import time
import configparser
import urllib.request
import base64
import json
import requests
import traceback
from Alumni.constants import Constants
from . import DatabaseActivityManager
from . import DataBaseGlobalFunctions
from . import DatabaseJudgeValid
from . import DatabaseUserManager

def LoginUser(request):
    '''
    描述：处理登录请求
    参数：request
    成功返回：
    { 
    "result": "success",
    "session": "123456abcdef",
    "openId": "asfsfs"
    }
    失败返回：
    {"errid": 101, "errmsg": "身份信息不存在"}
    ''' 
    Success = True
    Return = {}
    Info = {}
    TheParam = {}
    ErrorId = Constants.UNDEFINED_NUMBER
    Reason = ""
    TheCode = ""
    TheSession = ""
    TheOpenID = ""
    TheSessionKey = ""
    if Success:
        try:
            TheCode = request.GET.get("code")
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
            Reason = "请求参数不合法！"
    if Success:
        try:
            TheParam = {}
            TheParam = DatabaseUserManager.GetAppIDWechat()
            TheParam["js_code"] = TheCode
            TheParam["grant_type"] = "authorization_code"
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
            Reason = "请求参数不合法！"
    #换取openid 和 key    
    #print(TheParam)
    if Success:
        try:
            TheRequest = requests.get("https://api.weixin.qq.com/sns/jscode2session", params = TheParam, timeout = (5,10), allow_redirects = True)
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
            Reason = "网络繁忙，访问超时！"      

    if Success:
        try:
            if TheRequest.status_code < 200 or TheRequest.status_code >= 400:
                Success = False
                ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
                Reason = "网络繁忙，访问微信失败！！"
            TheJson = TheRequest.json()
            if TheJson["errcode"] == -1:
                Success = False
                ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
                Reason = "网络繁忙，访问微信失败！"  
            elif TheJson["errcode"] == 40029:
                Success = False
                ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
                Reason = "Code无效！"  
            elif TheJson["errcode"] == 45011:
                Success = False
                ErrorId = Constants.ERROR_CODE_INVALID_CHANGE
                Reason = "访问过于频繁，每个用户每分钟最多访问100次！"
            elif TheJson["errcode"] != 0:
                Success = False
                ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
                Reason = "网络繁忙，访问微信失败！"          
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
            Reason = "网络繁忙，访问微信失败！"  

    if Success:
        try:
            TheOpenID = TheJson["openid"]
            TheSessionKey = TheJson["session_key"]
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
            Reason = "网络繁忙，访问微信失败！"   

    if Success:
        try:
            TheSession = DatabaseGlobalFunctions.GenerateSessionID()
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_UNKNOWN
            Reason = "生成session失败！"  
    
    if Success:
        try:
            Return = DatabaseUserManager.AddUserID(TheOpenID, TheSessionKey, TheSession)
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_UNKNOWN
            Reason = "访问数据库失败！"
    if Success == False:
        Return["errid"] = ErrorId
        Return["errmsg"] = Reason

    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def GetAlumniInfo(request): 
    '''
    描述：获取校友信息
    参数：request
    成功返回：
    {
    "params": {
    "appId": "wx1ebe3b2266f4afe0",
    "path": "pages/index/index",
    "envVersion": "develop",
    "extraData": {
      "origin": "miniapp",
      "ticket": "52ec7c69-9d7c-4495-b07f-7e10ab4ad24f",
      "type": "oauth"
    }
    }
    }
    失败返回：
    {"errid": 101, "errmsg": "身份信息不存在"}
    '''
    Success = True
    Return = {}
    Info = {}
    TheParam = {}
    TheJson = {}
    ErrorId = Constants.UNDEFINED_NUMBER
    Reason = ""
    TheSession = ""
    TheOpenID = ""
    TheSessionKey = ""
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
            Reason = "请求参数不合法！"
    if Success:
        try:
            TheParam = DatabaseManager.GetAppIDThis()
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
            Reason = "请求参数不合法！"
    #换取openid 和 key    
    print(TheParam)
    if Success:
        try:
            TheRequest = requests.post("https://alumni-test.iterator-traits.com/fake-info-tsinghua-org/mp/oauth/initiate/miniapp", data = json.dumps(TheParam), timeout = (5,10), allow_redirects = True)
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
            Reason = "网络繁忙，访问超时！" 
    #print(TheRequest)     
    if Success:
        try:
            if TheRequest.status_code < 200 or TheRequest.status_code >= 400:
                Success = False
                ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
                Reason = "网络繁忙，访问清华人失败！！"
            TheJson = TheRequest.json()
            TheRequestID = TheJson["requestId"]       
            Info  = TheJson["params"] 
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
            Reason = "网络繁忙，访问清华人失败！"  

    if Success:
        if DatabaseUserManager.AddRequestID(TheSession, TheRequestID) != True:
            Success = False
            ErrorId = Constants.ERROR_CODE_LOGIN_ERROR
            Reason = "用户未登录！"
    
    if Success == False:
        Return["errid"] = ErrorId
        Return["errmsg"] = Reason
    else:
        Return["params"] = Info
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def ReceiveAlunmiInfo(request):
    '''
    描述：接收清华人回调请求，存储用户信息
    参数：request
    成功返回
    {
    "result": "success"
    }
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    TheParam = {}
    TheJson = {}
    Reason = ""
    ErrorId = Constants.UNDEFINED_NUMBER
    TheContent = {}
    TheRequestID = ""
    if Success:
        try:
            TheContent = json.loads(request.body)["data"]
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
            Reason = "请求参数不合法"
    if Success:
        ReturnResult = DatabaseUserManager.AddUser(TheContent) 
        if ReturnResult["result"] != "success":
            Success = False
            ErrorId = ReturnResult["code"]
            Reason = ReturnResult["reason"]
    if Success:
        Return["result"] = "success"
    else:
        Return["errid"] = ErrorId
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def QueryUser(request):
    '''
    描述：处理查询用户信息请求
    参数：request
    成功返回：
    {
    "name": "李肇阳",
    "campusIdentity": [
    {
      "enrollmentYear": "2014",
      "department": "软件学院",
      "enrollmentType": "Undergraduate"
    },
    {
      "enrollmentYear": "2018",
      "department": "软件学院",
      "enrollmentType": "Master"
    }
    ]
    }
    失败返回：
    {"errid": 101, "errmsg": "身份信息不存在"}
    '''
    Success = True
    Return = {}
    Info = {}
    ErrorId = Constants.UNDEFINED_NUMBER
    Reason = ""
    TheSession = ""
    SelfOpenID = ""
    TheOpenID = ""
    #print(request.POST)
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
            Reason = "请求参数不合法！"
    
    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            SelfOpenID = DatabaseUserManager.GetCurrentUser(TheSession)
            if SelfOpenID == None:
                Success = False
                ErrorId = Constants.ERROR_CODE_LOGIN_ERROR
                Reason = "用户未登录！"
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_LOGIN_ERROR
            Reason = "用户未登录！"
    if Success:
        try:
            TheOpenID = request.GET.get("openId")
            if TheOpenID == None:
                TheOpenID = SelfOpenID
        except:
            TheOpenID = SelfOpenID
    

    #调用数据库函数查询信息
    print(SelfOpenID)
    if Success:
        try:
            Info = DatabaseUserManager.QueryUser(TheOpenID)
            #print(Info)
            if Info == {}:
                Success = False
                Reason = "身份信息不存在！"
                ErrorId = Constants.ERROR_CODE_NOT_FOUND
            elif Info["name"] == "UNDEFINED":
                Success = False
                Reason = "身份信息尚未存储！"
                ErrorId = Constants.ERROR_CODE_NOT_STORED
        except:
            Success = False
            Reason = "身份信息不存在！"
            ErrorId = Constants.ERROR_CODE_NOT_FOUND

    if Success == True:
        Return = Info    
    else:
        Return["errid"] = ErrorId
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def StartActivity(request):
    '''
    描述：处理添加活动请求
    参数：request

    成功返回：
    {
    “id”:”0000001”(活动id)
    }
    失败返回：
    {"errid": 101, "errmsg": "身份信息不存在"}
    '''
    Success = True
    Return = {}
    Info = {}
    RequestBody = {}
    ErrorId = Constants.UNDEFINED_NUMBER
    Reason = ""
    TheSession = ""
    SelfOpenID = ""
    #print(request.POST)

    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            SelfOpenID = DatabaseUserManager.GetCurrentUser(TheSession)
            if SelfOpenID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorId = Constants.ERROR_CODE_LOGIN_ERROR

        except:
            Success = False
            Reason = "用户未登录！"
            ErrorId = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数进行操作
    if Success:
        try:
            RequestBody = json.loads(request.body)
            Info = DatabaseActivityManager.AddActivity(SelfOpenID, RequestBody)
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER

    if Success:
        if Info["result"] == "success":
            Return["activityId"] = str(Info["activityId"])
        else:
            if ErrorId == Constants.UNDEFINED_NUMBER:
                Success = False
                Return["errmsg"] = Info["reason"]
                Return["errid"] = Info["code"]
    else:
        Return["errid"] = ErrorId
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def JoinActivity(request):
    '''
    描述：处理报名活动请求
    参数：request
    成功只返回
    {
    "result": "success"
    }   
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheActivity = Constants.UNDEFINED_NUMBER
    TheUserID = ""
    TheJoinReason = None
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivity = int(request.GET.get("activityId"))
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    #获取请求理由
    if Success:
        try:
            TheJoinReason = json.loads(request.body)["reason"]
        except:
            TheJoinReason = None

    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数添加活动
    if Success:
        try:
            Info = DatabaseActivityManager.JoinActivity(TheUserID, TheActivity, False, TheJoinReason)
            #print(Info)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "加入活动失败"
            ErrorID = Constants.ERROR_CODE_UNKNOWN

    if Success:
        Return["result"] = "success"
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response
 
def GetActivityList(request):
    '''
    描述：处理查询全部活动请求
    参数：request
    成功返回活动列表
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    ErrorInfo = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info, ErrorInfo = DatabaseActivityManager.ShowAllActivity()
            #print(Info)
            if Info == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
        except:
            Success = False
            Reason = "查询活动列表失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def QueryActivity(request):
    '''
    描述：处理查询单个活动信息请求
    参数：request
    成功返回活动信息
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheActivity = Constants.UNDEFINED_NUMBER
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivity = int(request.GET.get("activityId"))
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info = DatabaseActivityManager.QueryActivity(TheUserID, TheActivity)
            if Info == {}:
                Success = False
                Reason = "未找到活动！"
                ErrorID = Constants.ERROR_CODE_NOT_FOUND
        except:
            Success = False
            Reason = "查询活动详情失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def QuerySelfActivity(request):
    '''
    描述：处理查询自身全部活动信息请求
    参数：request
    成功返回活动列表
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    ErrorInfo = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info, ErrorInfo = DatabaseActivityManager.ShowSelfActivity(TheUserID)
            #print(Info)
            if Info == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
        except:
            Success = False
            Reason = "查询活动列表失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def QueryAllParticipants(request):
    '''
    描述：处理查询单个活动全部成员信息请求--用户
    参数：request
    成功返回全部成员信息
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    ErrorInfo = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheActivity = Constants.UNDEFINED_NUMBER
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivity = int(request.GET.get("activityId"))
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info, ErrorInfo = DatabaseActivityManager.ShowAllMembers(TheActivity)
            #print(Info)
            if Info == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
        except:
            Success = False
            Reason = "查询活动成员信息失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def QueryAllParticipantsAdmin(request):
    '''
    描述：处理查询单个活动全部成员信息请求--管理员
    参数：request
    成功返回全部成员信息
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    ErrorInfo = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheActivity = Constants.UNDEFINED_NUMBER
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivity = int(request.GET.get("activityId"))
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info, ErrorInfo = DatabaseActivityManager.ShowAllMembersAdmin(TheUserID, TheActivity)
            #print(Info)
            if Info == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
        except:
            Success = False
            Reason = "查询活动成员信息失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def QueryAllAuditParticipants(request):
    '''
    描述：处理查询单个活动全部待审核成员信息请求--管理员
    参数：request
    成功返回待审核成员信息
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    ErrorInfo = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheActivity = Constants.UNDEFINED_NUMBER
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivity = int(request.GET.get("activityId"))
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info, ErrorInfo = DatabaseActivityManager.ShowAllAuditMembers(TheUserID, TheActivity)
            if Info == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
        except:
            Success = False
            Reason = "查询待审核成员信息失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def DeleteActivity(request):
    '''
    描述：处理删除单个活动信息请求
    参数：request
    成功返回
    {
    "result": "success"
    }
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheActivity = Constants.UNDEFINED_NUMBER
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivity = int(request.GET.get("activityId"))
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info = DatabaseActivityManager.DeleteActivity(TheUserID, TheActivity)
            #print(Info)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "删除活动失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def ChangeActivity(request):
    '''
    描述：处理修改活动请求
    参数：request
    成功只返回
    {
    "result": "success"
    }   
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheUserID = ""
    Data = json.loads(request.body)
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER

    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info = DatabaseActivityManager.ChangeActivity(TheUserID, Data)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "修改活动失败"
            ErrorID = Constants.ERROR_CODE_UNKNOWN
    
    if Success:
        Return["result"] = "success"
    else:
        Return["errmsg"] = Reason
        Return["errid"] = ErrorID
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def ChangeUserStatus(request):
    '''
    描述：处理修改用户状态请求
    参数：request
    成功只返回
    {
    "result": "success"
    }   
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheUserID = ""
    Data = json.loads(request.body)
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER

    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info = DatabaseActivityManager.ChangeUserStatus(TheUserID, Data)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "修改用户信息失败"
            ErrorID = Constants.ERROR_CODE_UNKNOWN
    
    if Success:
        Return["result"] = "success"
    else:
        Return["errmsg"] = Reason
        Return["errid"] = ErrorID
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def AuditUser(request):
    '''
    描述：审核用户
    参数：request
    返回：成功{result：success}
        失败：{result：fail，errmsg：xxx，errid：xxx}
    '''
    Success = True
    Return = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheManagerID = ""
    TheUserID = ""
    TheActivityID = -1
    WhetherPass = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheUserID = request.GET.get("userId")
            TheActivityID = int(request.GET.get("activityId"))
            WhetherPass = request.GET.get("pass")
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER

    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            TheManagerID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheManagerID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info = DatabaseActivityManager.AuditUser(TheManagerID, TheUserID, TheActivityID, WhetherPass)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "审核用户失败"
            ErrorID = Constants.ERROR_CODE_UNKNOWN
    
    if Success:
        Return["result"] = "success"
    else:
        Return["errmsg"] = Reason
        Return["errid"] = ErrorID
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def QueryActivityTypes(request):
    '''
    描述：处理查询所有活动类型
    参数：request
    成功返回全部活动类型
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info = DataBaseGlobalFunctions.ShowAllActivityType()
            #print(Info)
            if Info == {}:
                Success = False
                Reason = "查询活动类型列表失败！"
                ErrorID = Constants.ERROR_CODE_NOT_FOUND
        except:
            Success = False
            Reason = "查询活动类型列表失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def QueryEducationTypes(request):
    '''
    描述：处理查询所有教育类型
    参数：request
    成功返回全部教育类型
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info = DataBaseGlobalFunctions.ShowAllEducationType()
            #print(Info)
            if Info == {}:
                Success = False
                Reason = "查询教育类型列表失败！"
                ErrorID = Constants.ERROR_CODE_NOT_FOUND
        except:
            Success = False
            Reason = "查询教育类型列表失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def QueryDepartments(request):
    '''
    描述：处理查询所有院系
    参数：request
    成功返回全部院系
    失败则是
    {
    "errid":xxx,
    "errmsg":"xxxx"
    }
    '''
    Success = True
    Return = {}
    Info = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER
    TheSession = ""
    TheUserID = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseUserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #调用数据库函数
    if Success:
        try:
            Info = DataBaseGlobalFunctions.ShowAllDepartment()
            #print(Info)
            if Info == {}:
                Success = False
                Reason = "查询院系列表失败！"
                ErrorID = Constants.ERROR_CODE_NOT_FOUND
        except:
            Success = False
            Reason = "查询院系列表失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        Return = Info
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response  