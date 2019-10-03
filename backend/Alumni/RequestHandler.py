'''
处理请求的函数集合

用户类请求：
    登录（todo）
    修改信息
    删除（todo）
    查询信息
活动类请求：
    查询单个
    查询全部
    修改单个（todo）
    报名单个
    删除单个（todo）
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
from . import DatabaseManager

def ChangeUser(request):
    '''
    描述：处理修改用户信息请求
    参数：request
    POST setUserInfo?openId=(String)
    {
    "name": "小明",
    "gender": "male | female | other",
    "flag":"invalid",
    "education": [
    {
        "type": "undergraduate | master | doctor",
        "id": 2013010253,
        "start": 2013,
        "end": 2017,
        "departmentId": 00210,
        "department": "清华大学软件学院"
        "class": "软81"
    },
    {
        "type": "master",
        "id": 2017011210,
        "start": 2017,
        "end": null,
        "departmentId": 00207,
        "department": "清华大学精仪系"
        "class": "软81"
    }
    ]
    }
    成功返回：
    {
    “id”:”xxxxx”(用户id)
    }
    失败返回：
    {
        “error”："修改活动失败"
    }
    '''
    Success = True
    Return = {}

    #print(request.POST)
    #获取请求数据
    Data = json.loads(request.body)
    #print(request.POST)
    if Success:
        try:
            OpenID = request.GET.get("openID")
            Name = Data["name"]
            Gender = Data["gender"]
            Flag = Data["flag"]
            Education = Data["education"]
            #print(OpenID, Name, Place, Start, End, MaxUser)
        except:
            Success = False
    #print(OpenID,Name,Gender,Flag,Education)
    #print(request)

    #判断是否登录
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            if not Info:
                Success = False
                Return["error"] = "未登录"
        except:
            Success = False
    #print(Success)


    #调用数据库函数修改信息
    if Success:
        try:
            Info = DatabaseManager.ChangeUser(OpenID, Name, Gender, Flag, Education)
            #print(Info)
            if Info["Success"] == False:
                Success = False
            else:
                Return["id"] = OpenID
        except:
            Success = False
    #print(Success)
    if Success == False and (not Return["error"]):
        try:
            Return["error"] = Info["Reason"]
        except:
            Return["error"] = "others"
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
    GET getUserInfo?userWechatId=(String)    
    成功返回：
    {
    "name": "小明",
    "gender": "male | female | other",
    "flag":"invalid",
    "education": [
    {
        "type": "undergraduate | master | doctor",
        "id": 2013010253,
        "start": 2013,
        "end": 2017,
        "departmentId": 00210,
        "department": "清华大学软件学院"
        "class": "软81"
    },
    {
        "type": "master",
        "id": 2017011210,
        "start": 2017,
        "end": null,
        "departmentId": 00207,
        "department": "清华大学精仪系"
        "class": "软81"
    }
    ]
    }
    失败返回：
    {
        “error”："原因"
    }
    '''
    Success = True
    Return = {}

    #print(request.POST)
    #获取请求数据
    if Success:
        try:
            OpenID = request.GET.get("userWechatId")
            #print(OpenID, Name, Place, Start, End, MaxUser)
        except:
            Success = False
    #print(OpenID,Name,Gender,Flag,Education)
    #print(request)

    #判断是否登录
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            if not Info:
                Success = False
                Return["error"] = "未登录"
        except:
            Success = False
    #print(Success)


    #调用数据库函数修改信息
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            #print(Info)
            if not Info:
                Success = False
        except:
            Success = False

    #print(Success)
    if Success == False and ("error" not in Return.keys()):
        Return["error"] = "others"
    if Success == True:
        Return = Info

    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def DeleteUser(request):
    '''
    描述：处理删除用户信息请求
    参数：request
    POST deleteUser?userWechatId=(String)   
    成功返回：{}
    
    失败返回：
    {
        “error”："原因"
    }
    似乎有问题，可能不会用这个接口
    '''
    Success = True
    Return = {}

    #print(request.POST)
    if Success:
        try:
            OpenID = request.GET.get("userWechatId")
            #print(OpenID, Name, Place, Start, End, MaxUser)
        except:
            Success = False
    #print(OpenID,Name,Gender,Flag,Education)
    #print(request)

    #判断是否登录
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            if not Info:
                Success = False
                Return["error"] = "未登录"
        except:
            Success = False
    #print(Success)


    #调用数据库函数修改信息
    if Success:
        try:
            Info = DatabaseManager.DeleteUser(OpenID)
            #print(Info)
            if Info == False:
                Success = False
        except:
            Success = False

    #print(Success)
    if Success == False and ("error" not in Return.keys()):
        Return["error"] = "others"

    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def StartActivity(request):
    '''
    描述：处理添加活动请求
    参数：request
    POST createAcitivity?userWechatId=(String)
    {
    “name”:"校友会第一次活动",
    "place":"北京",
    "start":"2019-9-26 09:30:00",
    "end":"2019-9-26 10:30:00",
    "maxUser":100
    }

    成功返回：
    {
    “id”:”0000001”(活动id)
    }
    失败返回：
    {
        “error”：”添加活动失败“
    }
    '''
    Success = True
    Return = {}



    Data = json.loads(request.body)
    #print(request.POST)
    #获取请求数据
    if Success:
        try:
            OpenID = request.GET.get("userWechatId")
            #print(OpenID)
            Name = Data["name"]
            #print(Name)
            Place = Data["place"]
            Start = Data["start"]
            End = Data["end"]
            MaxUser = int(Data["maxUser"])
            #print(OpenID, Name, Place, Start, End, MaxUser)

        except:
            Success = False
    #print(request)

    #判断是否登录
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            if not Info:
                Success = False
                Return["error"] = "未登录"
        except:
            Success = False


    #调用数据库函数添加活动
    if Success:
        try:
            Info = DatabaseManager.AddActivity(Name, Place, Start, End, MaxUser, OpenID)
            #print(Info)
            if Info["Success"] == False:
                Success = False
            else:
                Return["id"] = Info["id"]
        except:
            Success = False
    
    if Success == False:
        Return["error"] = "添加活动失败"
    
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def JoinActivity(request):
    '''
    描述：处理报名活动请求
    参数：request
    POST joinActivity?userWechatId=(String)&activityId=(String)
    成功返回：
    200 OK
    失败返回：
    400内容为：
    {“errmsg”: “(例)该活动人数已满”}
    '''
    Success = True
    Return = {}

    
    #获取请求数据
    if Success:
        try:
            OpenID = request.GET.get("userWechatId")
            ActivityID = request.GET.get("activityId")

        except:
            Success = False
    #print(request)

    #判断是否登录
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            if not Info:
                Success = False
                Return["errmsg"] = "未登录"
        except:
            Success = False



    #调用数据库函数添加活动
    if Success:
        try:
            Info = DatabaseManager.JoinActivity(OpenID,ActivityID)
            #print(Info)
            if Info["Success"] == False:
                Success = False
                Return["errmsg"] = Info["Reason"]
        except:
            Success = False
    if Success == False and ("errmsg" not in Return.keys()):
        Return["errmsg"] = "other"

    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def ChangeActivity(request):
    '''
    描述：处理报名活动请求
    参数：request
    POST modifyAcitivity?userWechatId=(String)&activityId=(String)
    {
    "name":"校友会第一次活动",
    "place":"北京",
    "start":"2019-9-26 09:30:00",
    "end":"2019-9-26 10:30:00",
    "maxUser":100
    }
    成功返回：
    {
        "id":"0000001"(活动id)
    }
    失败返回：HTTP 400
    {
        "errmsg": "例如活动ID不存在等文字错误描述"
    }
    '''
    Success = True
    Return = {}
    Data = json.loads(request.body)
    #获取请求数据
    if Success:
        try:
            OpenID = request.GET.get("userWechatId")
            ActivityID = request.GET.get("activityId")
            Name = Data["name"]
            Place = Data["place"]
            Start = Data["start"]
            End = Data["end"]
            MaxUser = int(Data["maxUser"])
        except:
            Success = False

    #判断是否登录
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            if not Info:
                Success = False
                Return["errmsg"] = "未登录"
        except:
            Success = False

    #判断是否有权限
    if Success:
        try:
            Info = DatabaseManager.JudgeCreator(OpenID, ActivityID)
            if Info == False:
                Success = False
                Return["errmsg"] = "没有权限"
        except:
            Success = False

    #调用数据库函数
    if Success:
        try:
            Info = DatabaseManager.ChangeActivity(ActivityID, Name, Place, Start, End, MaxUser)
            if Info["Success"] == False:
                Return["errmsg"] = Info["Reason"]
                Success = False
        except:
            Success = False
    
    if Success == False and ("errmsg" not in Return.keys()):
        Return["errmsg"] = "other"
    
    if Success == True:
        Return["id"] = ActivityID

    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response
    
def GetActivityList(request):
    '''
    描述：处理查看活动列表请求
    参数：request
    GET getAllActivity?userWechatId=(String)
    返回：活动列表
    {
    “activityList”:[
    {
            "id": 1,
            "name": "校友会第一次活动",
            "place": "北京",
            "start": "2019-09-26 09:30:00",
            "end": "2019-09-26 10:30:00",
            "maxUser": 100,
            "curUser": 1,
            "creator": "xxxxx"
    },
    {
            "id": 2,
            "name": "校友会第2次活动",
            "place": "北京",
            "start": "2019-09-26 09:30:00",
            "end": "2019-09-26 10:30:00",
            "maxUser": 100,
            "curUser": 1,
            "creator": "xxxxx"
    }
    ]
    }
    '''
    Success = True
    Return = {}
    Return["activityList"] = []
    #Data = json.loads(request.body)
    #获取请求数据
    if Success:
        try:
            OpenID = request.GET.get("userWechatId")
        except:
            Success = False

    #判断是否登录
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            if not Info:
                Success = False
        except:
            Success = False

    #调用数据库
    if Success:
        Return["activityList"] = DatabaseManager.ShowAllActivity()
    #print(Return)
    Response = JsonResponse(Return)
    return Response    

def QueryActivity(request):
    '''
    描述：处理查询单个活动信息请求
    参数：request
    Get getActivityInfo?userWechatId=(String)&activityId=(String)
    成功返回：
    {
    "id": 1,
    "name": "校友会第一次活动",
    "place": "北京",
    "start": "2019-09-26 09:30:00",
    "end": "2019-09-26 10:30:00",
    "maxUser": 100,
    "curUser": 1,
    "creator": "xxxxx"
    }
    失败返回：
    {
        “error”："原因"
    }
    '''
    Success = True
    Return = {}

    #print(request.POST)
    #获取请求数据
    if Success:
        try:
            OpenID = request.GET.get("userWechatId")
            ActivityID = request.GET.get("activityId")
            #print(OpenID, Name, Place, Start, End, MaxUser)
        except:
            Success = False
    #print(OpenID,Name,Gender,Flag,Education)
    #print(request)

    #判断是否登录
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            if not Info:
                Success = False
                Return["error"] = "未登录"
        except:
            Success = False
    #print(Success)


    #调用数据库函数修改信息
    if Success:
        try:
            Info = DatabaseManager.QueryActivity(ActivityID)
            #print(Info)
            if not Info:
                Success = False
        except:
            Success = False

    #print(Success)
    if Success == False and ("error" not in Return.keys()):
        Return["error"] = "others"
    if Success == True:
        Return = Info

    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response

def DeleteActivity(request):
    '''
    描述：处理删除活动信息请求
    参数：request
    POST deleteActivity?userWechatId=(String)&activityId=(String)    
    成功返回：{}
    
    失败返回：
    {
        “error”："原因"
    }
    '''
    Success = True
    Return = {}

    #print(request.POST)
    if Success:
        try:
            OpenID = request.GET.get("userWechatId")
            ActivityID = request.GET.get("activityId")
            #print(OpenID, Name, Place, Start, End, MaxUser)
        except:
            Success = False
    #print(OpenID,Name,Gender,Flag,Education)
    #print(request)

    #判断是否登录
    if Success:
        try:
            Info = DatabaseManager.QueryUser(OpenID)
            if not Info:
                Success = False
                Return["error"] = "未登录"
        except:
            Success = False
    #print(Success)

    #判断是否有权限
    if Success:
        try:
            Info = DatabaseManager.JudgeCreator(OpenID, ActivityID)
            if Info == False:
                Success = False
                Return["error"] = "没有权限"
        except:
            Success = False

    #调用数据库函数修改信息
    if Success:
        try:
            Info = DatabaseManager.DeleteActivity(ActivityID)
            #print(Info)
            if Info == False:
                Success = False
        except:
            Success = False

    #print(Success)
    if Success == False and ("error" not in Return.keys()):
        Return["error"] = "others"

    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response
