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
    ErrorID = Constants.UNDEFINED_NUMBER
    TheInfo = json.loads(request.body)
    if Success:
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
    if Success and "statusGlobal" in TheInfo and TheInfo["statusGlobal"] == Constants.ACTIVITY_STATUS_GLOBAL_EXCEPT:
        TimeManager.SendTimedMessageActivity(TheInfo["id"], Constants.MESSAGE_TYPE_ACTIVITY_FORBIDDEN)  
        print("send forbid")

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
        try:
            TheResult, TheErrorInfo = AdminManager.ShowOneActivity(TheActivityID)
            if TheResult == {}:
                Success = False
                Reason = TheErrorInfo["reason"]
                ErrorID = TheErrorInfo["code"]
        except:
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

def ShowAllReport(request):
    '''
    描述：处理管理员获取全部举报信息请求
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
            TheResult, TheErrorInfo = AdminManager.ShowAllReports(TheLastSeenID, TheMostNumber)
            if TheResult == {}:
                Success = False
                Reason = TheErrorInfo["reason"]
                ErrorID = TheErrorInfo["code"]
        except:
            Success = False
            Reason = "查询全部举报失败！"
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

def ShowAllActivityReport(request):
    '''
    描述：处理管理员获取单一活动举报信息请求
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
        try:
            TheResult, TheErrorInfo = AdminManager.ShowActivityReports(TheActivityID)
            if TheResult == {}:
                Success = False
                Reason = TheErrorInfo["reason"]
                ErrorID = TheErrorInfo["code"]
        except:
            Success = False
            Reason = "查询举报失败！"
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

def DeleteOneReport(request):
    '''
    描述：处理管理员删除单一举报信息请求
    参数：request
    返回：response
    '''
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
    ErrorID = Constants.UNDEFINED_NUMBER
    TheReportID = 0
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheReportID = int(request.GET.get("id"))
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
            TheResult = AdminManager.DeleteOneReport(TheReportID)
            if TheResult["result"] != "success":
                Success = False
                Reason = TheResult["reason"]
                ErrorID = TheResult["code"]
        except:
            Success = False
            Reason = "删除举报信息失败！"
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

def DeleteActivityReport(request):
    '''
    描述：处理管理员获取单一举报信息请求
    参数：request
    返回：response
    '''
    Success = True
    Return = {}
    Reason = ""
    TheSession = ""
    TheResult = {}
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
        try:
            TheResult = AdminManager.DeleteActivityReport(TheActivityID)
            if TheResult["result"] != "success":
                Success = False
                Reason = TheResult["reason"]
                ErrorID = TheResult["code"]
        except:
            Success = False
            Reason = "删除活动的举报信息失败！"
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

def ShowOneUser(request):
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
    TheOpenID = ""
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheOpenID = request.GET.get("openId")
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
            TheResult = UserManager.QueryUser(TheOpenID)
            if TheResult == {}:
                Success = False
                Reason = "用户不存在！"
                ErrorID = Constants.ERROR_CODE_NOT_FOUND
        except:
            Success = False
            Reason = "查询用户失败！"
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
    TheStatus = Constants.UNDEFINED_NUMBER
    if Success:
        try:
            TheBody = json.loads(request.body)
            TheSession = request.GET.get("session")
            TheUserID = TheBody["openId"]
            TheStatus = int(TheBody["status"])
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
            TheResult = AdminManager.ChangeUser(TheUserID, TheStatus)
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