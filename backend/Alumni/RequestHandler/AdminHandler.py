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
    try:
        TheUserName = request.GET.get("username")
        ThePassWord = request.GET.get("password")
    except:
        Success = False
        Reason = "请求参数不合法！"
        ErrorID = Constants.ERROR_CODE_INVALID_PARAMETER
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