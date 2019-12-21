'''
处理用户请求的函数集合
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
            TheParam = GlobalFunctions.GetAppIDWechat()
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
            #print(TheJson)
            if "errcode" in TheJson:
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
                    Reason = TheJson["errmsg"]       
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
            TheSession = GlobalFunctions.GenerateSessionID()
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_UNKNOWN
            Reason = "生成session失败！"  
    
    if Success:
        try:
            Return = UserManager.AddUserID(TheOpenID, TheSessionKey, TheSession)
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
            TheParam = GlobalFunctions.GetAppIDThis()
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
            Reason = "请求参数不合法！"
    #换取openid 和 key    
    #print(TheParam)
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
        if UserManager.AddRequestID(TheSession, TheRequestID) != True:
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
        ReturnResult = UserManager.AddUser(TheContent) 
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

def SetAvatarURL(request):
    '''
    描述：处理设置用户头像url请求
    参数：request
    成功返回：
    {
    “result”：“success”
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
    TheURL = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
    #判断是否登录，获取待查询的openid
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
            TheURL = RequestBody["avatarUrl"]
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
    if Success:
        try:
            if UserManager.SetAvatarURL(SelfOpenID, TheURL) != True:
                Success = False
                Reason = "设置头像url失败！"
                ErrorId = Constants.ERROR_CODE_UNKNOWN
        except:
            Success = False
            Reason = "设置头像url失败！"
            ErrorId = Constants.ERROR_CODE_UNKNOWN
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

def SetExtraData(request):
    '''
    描述：处理设置用户补充信息请求
    参数：request
    成功返回：
    {
    “result”：“success”
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
    TheURL = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
    #判断是否登录，获取待查询的openid
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
        except:
            Success = False
            Reason = "请求参数不合法！"
            ErrorId = Constants.ERROR_CODE_INVALID_PARAMETER
    if Success:
        try:
            QueryResult = UserManager.SetUserExtraData(SelfOpenID, RequestBody)
            if QueryResult["result"] != "success":
                Success = False
                Reason = QueryResult["reason"]
                ErrorId = QueryResult["code"]
        except:
            Success = False
            Reason = "设置头像url失败！"
            ErrorId = Constants.ERROR_CODE_UNKNOWN
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
    ExtraInfo = {}
    ErrorId = Constants.UNDEFINED_NUMBER
    Reason = ""
    TheSession = ""
    SelfOpenID = ""
    TheOpenID = ""
    TheActivityID = None
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
            TheResult = {}
            TheResult = UserManager.GetCurrentUserInQueryUser(TheSession)
            if TheResult["result"] == "success":
                SelfOpenID = TheResult["openId"]
            else:
                Success = False
                Reason = TheResult["reason"]
                ErrorId = TheResult["code"]
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
        try:
            TheActivityID = request.GET.get("activityId")
        except:
            TheActivityID = None
    
    #调用数据库函数查询信息
    #print(SelfOpenID)
    if Success:
        try:
            Info = UserManager.QueryUser(TheOpenID)
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
    #查询补充信息
    if Success:
        try:
            ExtraInfo = UserManager.GetUserExtraData(SelfOpenID, TheOpenID, TheActivityID)
            if "extraData" in ExtraInfo:
                Info["extraData"] = ExtraInfo["extraData"]
        except:
            Success = False
            Reason = "查询用户信息失败！"
            ErrorId = Constants.ERROR_CODE_UNKNOWN

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