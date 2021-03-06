'''
处理活动请求的函数集合
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
from Alumni.LogicManager.Constants import Constants
from Alumni.LogicManager import GlobalFunctions
from Alumni.LogicManager import JudgeValid
from Alumni.DatabaseManager import UserManager
from Alumni.DatabaseManager import ActivityManager
from Alumni.DatabaseManager import UserActivityManager
from Alumni.DatabaseManager import TimeManager


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
            SelfOpenID = UserManager.GetCurrentUser(TheSession)
            if SelfOpenID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorId = Constants.ERROR_CODE_LOGIN_ERROR

        except:
            Success = False
            Reason = "用户未登录！"
            ErrorId = Constants.ERROR_CODE_LOGIN_ERROR

    #判断是否被封禁
    if Success:
        JudgeResult = JudgeValid.JudgeUserValid(SelfOpenID)
        if JudgeResult != True:
            Success = False
            Reason = "用户已被封禁，不能操作！！"
            ErrorId = Constants.ERROR_CODE_INVALID_CHANGE

    #调用数据库函数进行操作
    if Success:
        try:
            RequestBody = json.loads(request.body)
            Info = ActivityManager.AddActivity(SelfOpenID, RequestBody)
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER

    if Success:
        if Info["result"] == "success" or Info["result"] == "needAudit":
            Return["activityId"] = str(Info["activityId"])
            Return["result"] = Info["result"]
        else:
            if ErrorId == Constants.UNDEFINED_NUMBER:
                Success = False
                Return["errmsg"] = Info["reason"]
                Return["errid"] = Info["code"]
    else:
        Return["errid"] = ErrorId
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)

    if Success:
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
    TheLastID = Constants.UNDEFINED_NUMBER
    TheMostNumber = Constants.UNDEFINED_NUMBER
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            try:
                TheLastID = int(request.GET.get("lastSeenId"))
            except:
                TheLastID = Constants.UNDEFINED_NUMBER
            try:
                TheMostNumber = int(request.GET.get("most"))
                if TheMostNumber <= 0:
                    Success = False
                    Reason = "请求参数不合法！"
                    ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER 
            except:
                TheMostNumber = Constants.UNDEFINED_NUMBER
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = UserManager.GetCurrentUser(TheSession)
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
            Info, ErrorInfo = ActivityManager.ShowAllActivity(TheLastID, TheMostNumber)
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
    SelfInfo = {}
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
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = UserManager.GetCurrentUser(TheSession)
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
            Info, ErrorInfo = ActivityManager.ShowOneActivity(TheUserID, TheActivity)
            if Info == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
        except:
            Success = False
            Reason = "查询活动详情失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND
    if Success:
        try:
            SelfInfo, ErrorInfo = UserActivityManager.GetSelfActivityRelation(TheUserID, TheActivity)
            if SelfInfo == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
            else:
                Info["selfStatus"] = SelfInfo["selfStatus"]
                Info["selfRole"] = SelfInfo["selfRole"]
                if "ruleForMe" in SelfInfo:
                    Info["ruleForMe"] = SelfInfo["ruleForMe"]
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

def QueryActivityDetail(request):
    '''
    描述：处理查询单个活动详情请求
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
    SelfInfo = {}
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
            TheUserID = UserManager.GetCurrentUser(TheSession)
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
            Info = ActivityManager.ShowActivityDetail(TheActivity)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
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
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = UserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #判断是否被封禁
    if Success:
        JudgeResult = JudgeValid.JudgeUserValid(TheUserID)
        if JudgeResult != True:
            Success = False
            Reason = "用户已被封禁，不能操作！！"
            ErrorID = Constants.ERROR_CODE_INVALID_CHANGE

    #调用数据库函数
    if Success:
        try:
            Info = ActivityManager.DeleteActivity(TheUserID, TheActivity)
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
    if Success:
        TimeManager.SendTimedMessageActivity(TheActivity, Constants.MESSAGE_TYPE_ACTIVITY_CANCEL)  
        print("send cancel")

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
    Data = {}
    NeedPush = False
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            Data = json.loads(request.body)
            try:
                TheNeedPush = request.GET.get("needPush")
                if int(TheNeedPush) > 0:
                    NeedPush = True
            except:
                NeedPush = False
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER

    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            TheUserID = UserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #判断是否被封禁
    if Success:
        JudgeResult = JudgeValid.JudgeUserValid(TheUserID)
        if JudgeResult != True:
            Success = False
            Reason = "用户已被封禁，不能操作！！"
            ErrorID = Constants.ERROR_CODE_INVALID_CHANGE

    #调用数据库函数
    if Success:
        try:
            Info = ActivityManager.ChangeActivity(TheUserID, Data)
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

    #发送消息
    if Success and NeedPush:
        TimeManager.SendTimedMessageActivity(Data["id"], Constants.MESSAGE_TYPE_ACTIVITY_CHANGE)  
        print("send change")
      
    return Response

def ChangeActivityDetail(request):
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
    TheActivity = 0
    TheUserID = ""
    Data = {}
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivity = int(request.GET.get("activityId"))
            Data = json.loads(request.body)
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER

    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            TheUserID = UserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #判断是否被封禁
    if Success:
        JudgeResult = JudgeValid.JudgeUserValid(TheUserID)
        if JudgeResult != True:
            Success = False
            Reason = "用户已被封禁，不能操作！！"
            ErrorID = Constants.ERROR_CODE_INVALID_CHANGE

    #调用数据库函数
    if Success:
        try:
            Info = ActivityManager.ChangeActivityDetail(TheUserID, TheActivity, Data)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "修改活动详情失败"
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

def UploadActivityQRCode(request):
    '''
    描述：处理更新活动二维码请求
    参数：request
    成功返回
    {
    图片
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
    TheImageName = ""
    TheImage = None
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
            TheUserID = UserManager.GetCurrentUser(TheSession)
            if TheUserID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #判断是否被封禁
    if Success:
        JudgeResult = JudgeValid.JudgeUserValid(TheUserID)
        if JudgeResult != True:
            Success = False
            Reason = "用户已被封禁，不能操作！！"
            ErrorID = Constants.ERROR_CODE_INVALID_CHANGE

    #调用数据库函数
    if Success:
        try:
            Info, TheImageName = ActivityManager.UploadActivityQRCode(TheUserID, TheActivity)
            #print(Info)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "更新活动二维码失败！"
            ErrorID = Constants.ERROR_CODE_NOT_FOUND

    if Success:
        TheImage = open(TheImageName,"rb").read()
        Response = HttpResponse(TheImage, content_type="image/png")
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
        Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

