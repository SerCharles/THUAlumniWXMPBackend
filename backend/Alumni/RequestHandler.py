'''
处理请求的函数集合

用户类请求：
    登录（todo）
    查询信息
活动类请求：
    增加单个
    报名单个
    查询单个
    查询全部
    查询用户对应活动
    查询人员
    修改单个
    修改用户信息
    删除单个
'''

from django.http import HttpResponse
from django.http import JsonResponse
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import numpy as np
from PIL import Image
from io import BytesIO
import random
import sqlite3
import pickle
import sys
import os
import time
import configparser
import urllib.request
import base64
import json
import imageio
import scipy.misc as misc
import traceback
from Alumni.constants import Constants
from . import DatabaseManager

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
            SelfOpenID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.QueryUser(TheOpenID)
            #print(Info)
            if Info == {}:
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
            SelfOpenID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.AddActivity(SelfOpenID, RequestBody)
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
            TheUserID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.JoinActivity(TheUserID, TheActivity, False)
            #print(Info)
            if Info["result"] != "success":
                Success = False
                Reason = Info["Reason"]
                ErrorID = Info["code"]
        except:
            Success = False
            Reason = "添加活动失败"
            ErrorID = Constants.ERROR_CODE_UNKNOWN

    if Success:
        Return["result"] = "success"
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
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
            TheUserID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.ShowAllActivity()
            #print(Info)
            if Info == {}:
                Success = False
                Reason = "查询活动列表失败！"
                ErrorID = Constants.ERROR_CODE_NOT_FOUND
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
            Code = Constants.ERROR_CODE_INVALID_PARAMETER
    
    #判断是否登录，获取待查询的openid
    if Success:
        try:
            TheUserID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.QueryActivity(TheActivity)
            #print(Info)
            if Info == {}:
                Success = False
                Reason = "查询活动详情失败！"
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
            TheUserID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.ShowSelfActivity(TheUserID)
            #print(Info)
            if Info == {}:
                Success = False
                Reason = "查询活动列表失败！"
                ErrorID = Constants.ERROR_CODE_NOT_FOUND
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
    Response.status_code = 400
    return Response 

def QueryAllParticipants(request):
    '''
    描述：处理查询单个活动全部成员信息请求
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
            TheUserID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.ShowAllMembers(TheActivity)
            #print(Info)
            if Info == {}:
                Success = False
                Reason = "查询活动成员信息失败！"
                ErrorID = Constants.ERROR_CODE_NOT_FOUND
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
            TheUserID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.DeleteActivity(TheUserID, TheActivity)
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
            TheUserID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.ChangeActivity(TheUserID, Data)
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
            TheUserID = DatabaseManager.GetCurrentUser(TheSession)
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
            Info = DatabaseManager.ChangeUserStatus(TheUserID, Data)
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
    Response.status_code = 400
    return Response