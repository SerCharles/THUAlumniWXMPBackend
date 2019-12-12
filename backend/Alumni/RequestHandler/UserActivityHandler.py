'''
处理用户-活动请求的函数集合
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
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    #获取请求理由
    if Success:
        try:
            TheJoinReason = json.loads(request.body)["reason"]
        except:
            TheJoinReason = None

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

    #调用数据库函数添加活动
    if Success:
        try:
            Info = UserActivityManager.JoinActivity(TheUserID, TheActivity, TheJoinReason)
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
 
def QuitActivity(request):
    '''
    描述：处理退出活动请求
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

    #调用数据库函数删除活动
    if Success:
        try:
            Info = UserActivityManager.QuitActivity(TheUserID, TheActivity)
            #print(Info)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "退出活动失败"
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
            Info, ErrorInfo = UserActivityManager.ShowSelfActivity(TheUserID)
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
            Info, ErrorInfo = UserActivityManager.ShowAllMembers(TheActivity)
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
            Info, ErrorInfo = UserActivityManager.ShowAllMembersAdmin(TheUserID, TheActivity)
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
            Info, ErrorInfo = UserActivityManager.ShowAllAuditMembers(TheUserID, TheActivity)
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

def ChangeUserRole(request):
    '''
    描述：处理修改用户权限请求
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
    TheSelfID = ""
    TheActivityID = 0
    TheNewRole = 0
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheUserID = request.GET.get("userId")
            TheActivityID = int(request.GET.get("activityId"))
            TheNewRole = int(request.GET.get("newRole"))
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER

    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            TheSelfID = UserManager.GetCurrentUser(TheSession)
            if TheSelfID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #判断是否被封禁
    if Success:
        JudgeResult = JudgeValid.JudgeUserValid(TheSelfID)
        if JudgeResult != True:
            Success = False
            Reason = "用户已被封禁，不能操作！！"
            ErrorID = Constants.ERROR_CODE_INVALID_CHANGE

    #调用数据库函数
    if Success:
        try:
            Info = UserActivityManager.ChangeUserRole(TheSelfID, TheUserID, TheActivityID, TheNewRole)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "修改用户权限失败"
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
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER

    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            TheManagerID = UserManager.GetCurrentUser(TheSession)
            if TheManagerID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #判断是否被封禁
    if Success:
        JudgeResult = JudgeValid.JudgeUserValid(TheManagerID)
        if JudgeResult != True:
            Success = False
            Reason = "用户已被封禁，不能操作！！"
            ErrorID = Constants.ERROR_CODE_INVALID_CHANGE

    #调用数据库函数
    if Success:
        try:
            Info = UserActivityManager.AuditUser(TheManagerID, TheUserID, TheActivityID, WhetherPass)
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
    if Success:
        if int(WhetherPass) == 1:
            TimeManager.SendTimedMessageUser(TheActivityID, TheUserID, Constants.MESSAGE_TYPE_AUDIT_PASS)
            print("send audit pass")
        else:  
            TimeManager.SendTimedMessageUser(TheActivityID, TheUserID, Constants.MESSAGE_TYPE_AUDIT_FAIL)
            print("send audit fail")
    return Response

def RemoveFromActivity(request):
    '''
    描述：将用户踢出活动
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
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER

    #判断是否登录， 获取待查询的openid
    if Success:
        try:
            TheManagerID = UserManager.GetCurrentUser(TheSession)
            if TheManagerID == None:
                Success = False
                Reason = "用户未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "用户未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR

    #判断是否被封禁
    if Success:
        JudgeResult = JudgeValid.JudgeUserValid(TheManagerID)
        if JudgeResult != True:
            Success = False
            Reason = "用户已被封禁，不能操作！！"
            ErrorID = Constants.ERROR_CODE_INVALID_CHANGE

    #调用数据库函数
    if Success:
        try:
            Info = UserActivityManager.RemoveUser(TheManagerID, TheUserID, TheActivityID)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "将用户移出活动失败"
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
    if Success:
        TimeManager.SendTimedMessageUser(TheActivityID, TheUserID, Constants.MESSAGE_TYPE_KICK)
        print("send kick")
    return Response

def CheckInActivity(request):
    '''
    描述：处理签到活动请求
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
            TheCode = request.GET.get("code")
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

    #调用数据库函数添加活动
    if Success:
        try:
            Info = UserActivityManager.CheckInActivity(TheUserID, TheActivity, TheCode)
            #print(Info)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "签到失败"
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

def ReportActivity(request):
    '''
    描述：处理举报活动请求
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
    TheReason = None
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivity = int(request.GET.get("activityId"))
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    #获取请求理由
    if Success:
        try:
            TheReason = json.loads(request.body)["reason"]
            if TheReason == "":
                Success = False
                Reason = "举报理由不能为空！"
                ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
        except:
            Success = False
            Reason = "举报理由不能为空！"
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

    #调用数据库函数添加活动
    if Success:
        try:
            Info = UserActivityManager.ReportActivity(TheUserID, TheActivity, TheReason)
            #print(Info)
            if Info["result"] != "success":
                Success = False
                Reason = Info["reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "举报活动失败"
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