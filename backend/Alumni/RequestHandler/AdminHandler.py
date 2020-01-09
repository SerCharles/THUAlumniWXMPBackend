'''
处理管理员请求的接口函数
'''

from django.http import HttpResponse
from django.http import JsonResponse
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
#import numpy as np
#from io import BytesIO
import random
import string
import sqlite3
import sys
import os
import time
import configparser
import urllib.request
import base64
import json
import traceback
from django.db import models
from DataBase.models import User
from DataBase.models import Education
from DataBase.models import Activity
from DataBase.models import JoinInformation
from DataBase.models import GlobalVariables
from DataBase.models import AdvancedRule
from DataBase.models import Department
from DataBase.models import EducationType
from DataBase.models import ActivityType
from DataBase.models import Picture
from DataBase.models import Admin
from DataBase.models import ReportInformation
from Alumni.LogicManager.Constants import Constants
from Alumni.DatabaseManager import AdminManager
from Alumni.DatabaseManager import UserManager
from Alumni.DatabaseManager import TimeManager


def Login(request):
    '''
    描述：处理管理员登录请求
    参数：request
    返回：response
    '''
    TheUserName = ""
    ThePassWord = ""
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
    ErrorID = Constants.UNDEFINED_NUMBER
    if Success:
        try:
            TheUserName = request.GET.get("username")
            ThePassWord = request.GET.get("password")
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    if Success:
        try:
            TheResult = AdminManager.Login(TheUserName, ThePassWord)
            if TheResult["result"] != "success":
                Success = False
                Reason = TheResult["reason"]
                ErrorID = TheResult["code"]
        except:
            Success = False
            Reason = "登录失败！"
            ErrorID = Constants.ERROR_CODE_UNKNOWN
    if Success:
        Return = TheResult
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def Logout(request):
    '''
    描述：处理管理员登出请求
    参数：request
    返回：response
    '''
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
    ErrorID = Constants.UNDEFINED_NUMBER
    try:
        TheSession = request.GET.get("session")
        if TheSession == 'UNDEFINED':
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER    
    except:
        Success = False
        Reason = "请求参数不合法！"
        ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    try:
        TheResult = AdminManager.Logout(TheSession)
        if TheResult["result"] != "success":
            Success = False
            Reason = TheResult["reason"]
            ErrorID = TheResult["code"]
    except:
        Success = False
        Reason = "登出失败！"
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

def ShowAllActivity(request):
    '''
    描述：处理管理员获取全部活动信息请求
    参数：request
    返回：response
    '''
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
    TheErrorInfo = {}
    ErrorID = Constants.UNDEFINED_NUMBER
    TheLastSeenID = Constants.UNDEFINED_NUMBER
    TheMostNumber = Constants.UNDEFINED_NUMBER
    if Success:
        try:
            TheSession = request.GET.get("session")
            if TheSession == 'UNDEFINED':
                Success = False
                Reason = "请求参数不合法！"
                ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
            try:
                TheLastSeenID = int(request.GET.get("lastSeenId"))
            except:
                TheLastSeenID = Constants.UNDEFINED_NUMBER
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
    if Success:
        try:
            if AdminManager.JudgeWhetherAdminLogin(TheSession) != True:
                Success = False
                Reason = "管理员未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "管理员未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
    if Success:
        try:
            TheResult, TheErrorInfo = AdminManager.ShowAllActivity(TheLastSeenID, TheMostNumber)
            if TheResult == {}:
                Success = False
                Reason = TheErrorInfo["reason"]
                ErrorID = TheErrorInfo["code"]
        except:
            Success = False
            Reason = "查询全部活动失败！"
            ErrorID = Constants.ERROR_CODE_UNKNOWN
    if Success:
        Return = TheResult
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def ShowOneActivity(request):
    '''
    描述：处理管理员获取单一活动信息请求
    参数：request
    返回：response
    '''
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
    TheErrorInfo = {}
    ErrorID = Constants.UNDEFINED_NUMBER
    TheActivityID = 0
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivityID = int(request.GET.get("activityId"))
            if TheSession == 'UNDEFINED':
                Success = False
                Reason = "请求参数不合法！"
                ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    if Success:
        try:
            if AdminManager.JudgeWhetherAdminLogin(TheSession) != True:
                Success = False
                Reason = "管理员未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "管理员未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
    if Success:
        if 1:
            TheResult, TheErrorInfo = AdminManager.ShowOneActivity(TheActivityID)
            if TheResult == {}:
                Success = False
                Reason = TheErrorInfo["reason"]
                ErrorID = TheErrorInfo["code"]
        else:
            Success = False
            Reason = "查询活动失败！"
            ErrorID = Constants.ERROR_CODE_UNKNOWN
    if Success:
        Return = TheResult
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def ShowAllUser(request):
    '''
    描述：处理管理员获取全部用户请求
    参数：request
    返回：response
    '''
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
    TheErrorInfo = {}
    ErrorID = Constants.UNDEFINED_NUMBER
    TheLastSeenID = Constants.UNDEFINED_NUMBER
    TheMostNumber = Constants.UNDEFINED_NUMBER
    if Success:
        try:
            TheSession = request.GET.get("session")
            if TheSession == 'UNDEFINED':
                Success = False
                Reason = "请求参数不合法！"
                ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
            try:
                TheLastSeenID = int(request.GET.get("lastSeenId"))
            except:
                TheLastSeenID = Constants.UNDEFINED_NUMBER
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
    if Success:
        try:
            if AdminManager.JudgeWhetherAdminLogin(TheSession) != True:
                Success = False
                Reason = "管理员未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "管理员未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
    if Success:
        try:
            TheResult, TheErrorInfo = AdminManager.ShowAllUsers(TheLastSeenID, TheMostNumber)
            if TheResult == {}:
                Success = False
                Reason = TheErrorInfo["reason"]
                ErrorID = TheErrorInfo["code"]
        except:
            Success = False
            Reason = "查询全部用户失败！"
            ErrorID = Constants.ERROR_CODE_UNKNOWN
    if Success:
        Return = TheResult
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def ChangeActivityStatus(request):
    '''
    描述：修改单一活动状态
    参数：request
    返回：response
    '''
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
    TheErrorInfo = {}
    TheInfo = {}
    ErrorID = Constants.UNDEFINED_NUMBER
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheInfo = json.loads(request.body)
            if TheSession == 'UNDEFINED':
                Success = False
                Reason = "请求参数不合法！"
                ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER     
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    if Success:
        try:
            if AdminManager.JudgeWhetherAdminLogin(TheSession) != True:
                Success = False
                Reason = "管理员未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "管理员未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
    if Success:
        try:
            TheResult = AdminManager.ChangeActivityStatus(TheInfo)
            if TheResult["result"] != "success":
                Success = False
                Reason = TheResult["reason"]
                ErrorID = TheResult["code"]
        except:
            Success = False
            Reason = "修改活动状态失败！"
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
    
    #发送消息
    if Success and "sendMessage" in TheResult:
        TimeManager.SendTimedMessageActivity(TheInfo["id"], TheResult["sendMessage"])
        if TheResult["sendMessage"] == Constants.MESSAGE_TYPE_ACTIVITY_FORBIDDEN:  
            print("send forbid")
        elif TheResult["sendMessage"] == Constants.MESSAGE_TYPE_AUDIT_PASS:  
            print("send audit pass")
        elif TheResult["sendMessage"] == Constants.MESSAGE_TYPE_AUDIT_FAIL:  
            print("send audit fail")
    return Response

def ChangeUserStatus(request):
    '''
    描述：处理管理员修改用户状态请求
    参数：request
    返回：response
    '''
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
    ErrorID = Constants.UNDEFINED_NUMBER
    TheUserID = ""
    TheBody = {}
    TheStatus = Constants.UNDEFINED_NUMBER
    if Success:
        try:
            TheBody = json.loads(request.body)
            TheSession = request.GET.get("session")
            if TheSession == 'UNDEFINED':
                Success = False
                Reason = "请求参数不合法！"
                ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    if Success:
        try:
            if AdminManager.JudgeWhetherAdminLogin(TheSession) != True:
                Success = False
                Reason = "管理员未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "管理员未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
    if Success:
        try:
            TheResult = AdminManager.ChangeUserStatus(TheBody)
            if TheResult["result"] != "success":
                Success = False
                Reason = TheResult["reason"]
                ErrorID = TheResult["code"]
        except:
            Success = False
            Reason = "修改用户状态失败！"
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

def ChangeUserPoint(request):
    '''
    描述：处理管理员修改用户积分请求
    参数：request
    返回：response
    '''
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
    ErrorID = Constants.UNDEFINED_NUMBER
    TheUserID = ""
    TheBody = {}
    TheStatus = Constants.UNDEFINED_NUMBER
    if Success:
        try:
            TheBody = json.loads(request.body)
            TheSession = request.GET.get("session")
            if TheSession == 'UNDEFINED':
                Success = False
                Reason = "请求参数不合法！"
                ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
    if Success:
        try:
            if AdminManager.JudgeWhetherAdminLogin(TheSession) != True:
                Success = False
                Reason = "管理员未登录！"
                ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
        except:
            Success = False
            Reason = "管理员未登录！"
            ErrorID = Constants.ERROR_CODE_LOGIN_ERROR
    if Success:
        try:
            TheResult = AdminManager.ChangeUserPoint(TheBody)
            if TheResult["result"] != "success":
                Success = False
                Reason = TheResult["reason"]
                ErrorID = TheResult["code"]
        except:
            Success = False
            Reason = "修改用户状态失败！"
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