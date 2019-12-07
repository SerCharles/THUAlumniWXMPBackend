'''
处理管理员请求的数据库函数
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
from django.contrib.auth.hashers import make_password, check_password
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
from Alumni.LogicManager import GlobalFunctions

def JudgeWhetherAdminLogin(TheSession):
    '''
    描述：判断管理员是否登录
    参数：session
    返回：是true否false
    '''  
    Success = True
    if TheSession == "UNDEFINED":
        Success = False
    if Success:
        try:
            TheAdmin = Admin.objects.get(Session = TheSession)
        except:
            Success = False
    return Success

def AddAdmin(TheUsername, ThePassword):
    '''
    添加用户的后门函数
    '''
    try:
        TheAdmin = Admin.objects.get(Username = TheUsername)
        TheAdmin.Password = make_password(ThePassword)
        TheAdmin.save()
    except:
        Admin.objects.create(Username = TheUsername, Password = make_password(ThePassword))    

def Login(TheUsername, ThePassword):
    '''
    描述：管理员登录的数据库函数
    参数：用户名，密码
    返回：成功{result：success}
		 失败：{result：fail，reason：xxx，code：xxx}
         成功还有session
    '''
    Success = True
    Reason = ""
    TheSession = ""
    Code = 0
    Return = {}
    print(TheUsername, ThePassword)
    if Success:
        try:
            TheAdmin = Admin.objects.get(Username = TheUsername)
        except:
            Success = False
            Reason = "帐号不存在！"
            Code = Constants.ERROR_CODE_NOT_FOUND
    print(Success)
    if Success:
        try:
            if check_password(ThePassword, TheAdmin.Password) != True:
                Success = False
                Reason = "密码不正确！"  
                Code = Constants.ERROR_CODE_NOT_FOUND
        except:
            Success = False
            Reason = "帐号不存在！"
            Code = Constants.ERROR_CODE_NOT_FOUND
    if Success:
        try:
            TheSession = GlobalFunctions.GenerateSessionID()
            TheAdmin.Session = TheSession
            TheAdmin.save()
        except:
            Success = False
            Reason = "登录失败！"
            Code = Constants.ERROR_CODE_UNKNOWN
    if Success:
        Return["result"] = "success"
        Return["session"] = TheSession
    else:
        Return["result"] = "fail"
        Return["reason"] = Reason
        Return["code"] = Code
    return Return

def Logout(TheSession):
    '''
    描述：管理员登出的数据库函数
    参数：session
    返回：成功{result：success}
		 失败：{result：fail，reason：xxx，code：xxx}
         成功还有session
    '''
    Success = True
    Reason = ""
    Code = 0
    Return = {}
    if Success:
        try:
            TheAdmin = Admin.objects.get(Session = TheSession)
        except:
            Success = False
            Reason = "帐号不存在！"
            Code = Constants.ERROR_CODE_NOT_FOUND
    if Success:
        try:
            TheAdmin.Session = "UNDEFINED"
            TheAdmin.save()
        except:
            Success = False
            Reason = "登出失败！"
            Code = Constants.ERROR_CODE_UNKNOWN
    if Success:
        Return["result"] = "success"
    else:
        Return["result"] = "fail"
        Return["reason"] = Reason
        Return["code"] = Code
    return Return