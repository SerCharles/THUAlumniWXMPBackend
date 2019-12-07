'''
处理搜索请求的函数集合
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
from Alumni.DatabaseManager import SearchAndRecommend


def SearchActivity(request):
    '''
    描述：处理输入关键词搜索活动请求
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
    SearchWord = ""
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            SearchWord = request.GET.get("searchWord")
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
            TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
            Info = TheSearcher.SearchInfo(SearchWord)
            #print(Info)
            if "activityList" not in Info:
                Success = False
                Reason = "搜索活动失败!"
                ErrorID = Constants.ERROR_CODE_NOT_FOUND
            elif Info["activityList"] == []:
                Success = False
                Reason = "未找到任何符合条件的活动！"
                ErrorID = Constants.ERROR_CODE_RECOMMEND
        except:
            Success = False
            Reason = "搜索活动失败！"
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

def SearchActivityAdvanced(request):
    '''
    描述：处理高级搜索活动请求
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
    SearchWord = ""
    Data = json.loads(request.body)
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
            Result, ErrorInfo = ActivityManager.AdvancedSearch(TheUserID, Data)
            #print(Info)
            if Result == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
            elif Result["activityList"] == []:
                Success = False
                Reason = "未找到任何符合条件的活动！"
                ErrorID = Constants.ERROR_CODE_RECOMMEND
        except:
            Success = False
            Reason = "搜索活动失败！"
            ErrorID = Constants.ERROR_CODE_UNKNOWN

    if Success:
        Return = Result
    else:
        Return["errid"] = ErrorID
        Return["errmsg"] = Reason
    Response = JsonResponse(Return)
    if Success == True:
        Response.status_code = 200
    else:
        Response.status_code = 400
    return Response 

def RecommendActivityByActivity(request):
    '''
    描述：处理按照活动推荐请求
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
    SearchWord = ""
    TheActivityID = 0
    #获取请求数据
    if Success:
        try:
            TheSession = request.GET.get("session")
            TheActivityID = request.GET.get("activityId")
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
            Info, ErrorInfo = SearchAndRecommend.RecommendActivityByActivity(TheUserID, TheActivityID)
            #print(Info)
            if Info == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
        except:
            Success = False
            Reason = "推荐活动失败！"
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

def RecommendActivityByUser(request):
    '''
    描述：处理按照用户推荐请求
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
    ErrorID = Cons = ""
    TheUserID = ""
    SearchWord = ""
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
            Info, ErrorInfo = SearchAndRecommend.RecommendActivityByUser(TheUserID)
            #print(Info)
            if Info == {}:
                Success = False
                Reason = ErrorInfo["reason"]
                ErrorID = ErrorInfo["code"]
        except:
            Success = False
            Reason = "推荐活动失败！"
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
