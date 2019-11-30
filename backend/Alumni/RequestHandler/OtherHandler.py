'''
处理杂项请求的函数集合
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
            Info = GlobalFunctions.ShowAllActivityType()
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
            Info = GlobalFunctions.ShowAllEducationType()
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
            Info = GlobalFunctions.ShowAllDepartment()
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
