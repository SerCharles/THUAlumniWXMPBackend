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
            except:
                TheMostNumber = Constants.UNDEFINED_NUMBER
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    
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
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    
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
    Data = json.loads(request.body)
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivity = int(request.GET.get("activityId"))
        except:
            Success = False
            Reason = "请求参数不合法！"
            Code = Constants.ERROR_CODE_INVALID_PARAMETER

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

def ChangeActivityByTime(request):
    '''
    描述：按照时间自动修改活动
    参数：request，什么都没有
    返回：同上
    '''
    Success = True
    Return = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER

    #调用数据库函数
    if Success:
        try:
            Result = ActivityManager.ChangeActivityStatusByTime()
            if Result != True:
                Success = False
                Reason = "更新正常活动状态失败！"
                ErrorID = Constants.ERROR_CODE_UNKNOWN
        except:
            Success = False
            Reason = "更新正常活动状态失败！"
            ErrorID = Constants.ERROR_CODE_UNKNOWN
    
    if Success:
        try:
            Result = ActivityManager.ChangeActivityStatusFinish()
            if Result != True:
                Success = False
                Reason = "更新活动结束状态失败！"
                ErrorID = Constants.ERROR_CODE_UNKNOWN
        except:
            Success = False
            Reason = "更新活动结束状态失败！"
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
    