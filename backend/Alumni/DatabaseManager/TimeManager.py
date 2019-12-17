'''
处理定时操作和消息推送的函数集合
包括定时更新数据库，定时推送消息
'''

from django.http import HttpResponse
from django.http import JsonResponse
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
#import numpy as np
#from io import BytesIO
import requests
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
from Alumni.LogicManager.Constants import Constants
from Alumni.LogicManager import GlobalFunctions
from Alumni.LogicManager import JudgeValid
from Alumni.DatabaseManager import SearchAndRecommend

# GlobalFunctions.SetAccessToken()
lastAccessTokenSetTime = 0

def ChangeActivityStatusByTime():
	'''
	描述：根据时间修改所有活动数据
	参数: 无
	返回：成功True， 失败False
	'''
	Success = True
	if Success:
		try:
			Info = Activity.objects.all()
		except:
			Success = False
	if Success:
		try:
			for item in Info:
				if item.StatusGlobal != Constants.ACTIVITY_STATUS_GLOBAL_NORMAL:
					continue
				TheCurrentTime = GlobalFunctions.GetCurrentTime()
				TheJoinStartTime = item.SignUpStartTime
				TheJoinEndTime = item.SignUpEndTime
				TheCheckStartTime = item.StartTime
				TheCheckEndTime = item.EndTime
				TheCurrentUser = item.CurrentUser
				TheMinUser = item.MinUser
				if item.StatusJoin == Constants.ACTIVITY_STATUS_JOIN_BEFORE:
					if GlobalFunctions.JudgeWhetherSameMinute(TheJoinStartTime):
						item.StatusJoin = Constants.ACTIVITY_STATUS_JOIN_CONTINUE
				if item.StatusJoin != Constants.ACTIVITY_STATUS_JOIN_STOPPED:
					if GlobalFunctions.JudgeWhetherSameMinute(TheJoinEndTime):
						item.StatusJoin = Constants.ACTIVITY_STATUS_JOIN_STOPPED
				if item.StatusCheck == Constants.ACTIVITY_STATUS_CHECK_BEFORE:
					if GlobalFunctions.JudgeWhetherSameMinute(TheCheckStartTime) and TheCurrentUser >= TheMinUser:
						item.StatusCheck = Constants.ACTIVITY_STATUS_CHECK_CONTINUE
				if item.StatusCheck != Constants.ACTIVITY_STATUS_CHECK_STOPPED:
					if GlobalFunctions.JudgeWhetherSameMinute(TheCheckEndTime):
						item.StatusCheck = Constants.ACTIVITY_STATUS_CHECK_STOPPED
				item.save()
		except:
			Success = False
	return Success

def ChangeActivityStatusFinish():
	'''
	描述：根据时间（23：59）修改所有当天结束的活动为finish，并且修改成员状态
	参数: 无
	返回：成功True， 失败False
	'''
	Success = True
	if GlobalFunctions.JudgeWhetherDayEnd() != True:
		return True
	if Success:
		try:
			Info = Activity.objects.all()
		except:
			Success = False
	if Success:
		try:
			for item in Info:
				if item.StatusGlobal != Constants.ACTIVITY_STATUS_GLOBAL_NORMAL:
					continue
				TheCheckEndTime = item.EndTime
				if GlobalFunctions.JudgeWhetherSameDay(TheCheckEndTime) != True:
					continue
				item.StatusGlobal = Constants.ACTIVITY_STATUS_GLOBAL_FINISH
				item.save()
				TheJoinActivityList = JoinInformation.objects.filter(ActivityId = item)
				for one in TheJoinActivityList:
					if one.Status == Constants.USER_STATUS_WAITVALIDATE:
						one.Status = Constants.USER_STATUS_REFUSED
					elif one.Status == Constants.USER_STATUS_JOINED:
						one.Status = Constants.USER_STATUS_FINISHED_WITHOUT_CHECK
					elif one.Status == Constants.USER_STATUS_CHECKED:
						one.Status = Constants.USER_STATUS_FINISHED
					one.save()
		except:
			Success = False
	return Success

def CheckActivitySendMessage():
    '''
	描述：根据时间判断是否要推送活动即将开始的消息，并且控制消息的发送
	参数: 无
	返回：无
	'''
    Success = True
    if Success:
        if(int(time.time()) - lastAccessTokenSetTime > 5400):
            GlobalFunctions.SetAccessToken()
    if Success:
        try:
            Info = Activity.objects.all()
        except:
            Success = False
    if Success:
        try:
            for item in Info:
                if item.StatusGlobal != Constants.ACTIVITY_STATUS_GLOBAL_NORMAL:
                    continue
                TheStartTime = item.StartTime
                if GlobalFunctions.JudgeWhetherSameMinute(TheStartTime - Constants.TIME_BEFORE_MESSAGE_ACTIVITY_WILL_START_HOUR):
                    SendTimedMessageActivity(item.ID, Constants.MESSAGE_TYPE_ACTIVITY_WILL_START_HOUR)
                elif GlobalFunctions.JudgeWhetherSameMinute(TheStartTime - Constants.TIME_BEFORE_MESSAGE_ACTIVITY_WILL_START_MINUTE):
                    SendTimedMessageActivity(item.ID, Constants.MESSAGE_TYPE_ACTIVITY_WILL_START_MINUTE)
        except:
            Success = False
    return Success

def SendTimedMessage(TheActivityItem, TheUserItem, TheMessageType):
    '''
	描述：推送活动消息函数
	参数: 活动的对象，用户对象，消息类型（作为数字定义在constants.py里）
	返回：无
	'''
    Success = True
    obj = {}
    data = {}
    pagePrefix = "/pages/ActivityList/ActivityDetail/ActivityDetail?activityId="
    if Success:
        try:
            if (TheMessageType == Constants.MESSAGE_TYPE_ACTIVITY_CHANGE or
                    TheMessageType == Constants.MESSAGE_TYPE_KICK or
                    TheMessageType == Constants.MESSAGE_TYPE_ACTIVITY_CANCEL or
                    TheMessageType == Constants.MESSAGE_TYPE_ACTIVITY_FORBIDDEN):
                obj["template_id"] = "LEoLo9UsF2by_4UGypKf2v7YLXeYRRGGjskOa0iJzZY"
                data["thing2"] = {"value": TheActivityItem.Name}
                data["date4"] = {"value": time.strftime("%Y{y}%m{m}%d{d} %H:%M", time.localtime(TheActivityItem.StartTime)).format(y='年', m='月', d='日')}
                data["thing5"] = {"value": TheActivityItem.Place}
                detail = None
                if (TheMessageType == Constants.MESSAGE_TYPE_KICK):
                    detail = "您被活动主办方踢出了该活动。"
                elif (TheMessageType == Constants.MESSAGE_TYPE_ACTIVITY_CANCEL):
                    detail = "活动主办方取消了该活动。"
                elif (TheMessageType == Constants.MESSAGE_TYPE_ACTIVITY_FORBIDDEN):
                    detail = "由于违规行为，该活动已被封禁。"
                elif (TheMessageType == Constants.MESSAGE_TYPE_ACTIVITY_CHANGE):
                    detail = "活动安排发生了变更。点击可查看详情。"
                data["thing6"] = {"value": detail}
            elif (TheMessageType == Constants.MESSAGE_TYPE_AUDIT_PASS or TheMessageType == Constants.MESSAGE_TYPE_AUDIT_FAIL):
                obj["template_id"] = "j9EPrZx9MAQ5SjbN1aCYHImxymn6ZEziJLgQEcbuXSk"
                data["thing2"] = {"value": TheActivityItem.Name}
                data["date3"] = {"value": time.strftime("%Y{y}%m{m}%d{d} %H:%M", time.localtime(TheActivityItem.StartTime)).format(y='年', m='月', d='日')}
                if(TheMessageType == Constants.MESSAGE_TYPE_AUDIT_PASS):
                    data["thing7"] = {"value": "您的加入申请已被通过"}
                    data["phrase1"] = {"value": "通过"}
                elif (TheMessageType == Constants.MESSAGE_TYPE_AUDIT_FAIL):
                    data["thing7"] = {"value": "如有疑问请联系活动主办方。"}
                    data["phrase1"] = {"value": "不通过"}
            elif (TheMessageType == Constants.MESSAGE_TYPE_ACTIVITY_WILL_START_HOUR):
                obj["template_id"] = "u-UA76noUE9_9g2ZVX53W9DQKz3x-Tn1914KHphfRXM"
                data["thing7"] = {"value": "您报名的活动将在明天举行，请合理安排行程"}
                data["thing4"] = {"value": TheActivityItem.Name}
                data["date3"] = {"value": time.strftime("%Y{y}%m{m}%d{d} %H:%M", time.localtime(TheActivityItem.StartTime)).format(y='年', m='月', d='日')}
                data["thing6"] = {"value": TheActivityItem.Place}
            elif (TheMessageType == Constants.MESSAGE_TYPE_ACTIVITY_WILL_START_MINUTE):
                obj["template_id"] = "u-UA76noUE9_9g2ZVX53Wz3QZ-IgE4ECwLVxWLIJlZ8"
                data["thing7"] = {"value": "您报名的活动即将举行，请按时到场并签到"}
                data["thing4"] = {"value": TheActivityItem.Name}
                data["date5"] = {"value": time.strftime("%Y{y}%m{m}%d{d} %H:%M", time.localtime(TheActivityItem.StartTime)).format(y='年', m='月', d='日')}
                data["thing6"] = {"value": TheActivityItem.Place}
            else:
                Success = False
                Reason = "没有对应的消息类型"
        except:
            Success = False
            Reason = "产生消息阶段异常"

    if Success:
        try:
            obj["touser"] = TheUserItem.OpenID
            obj["page"] = pagePrefix + str(TheActivityItem.ID)
            obj["data"] = data
        except:
            Success = False
            Reason = "产生消息阶段2异常"

    if Success:
        try:
            url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token=" + GlobalFunctions.GetAccessToken()
            TheRequest = requests.post(url, data = json.dumps(obj), timeout = (5,10), allow_redirects = True)
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
                elif TheJson["errcode"] != 0:
                    Success = False
                    ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
                    Reason = TheJson["errmsg"]
        except:
            Success = False
            ErrorId = Constants.ERROR_CODE_NETWORK_ERROR
            Reason = "网络繁忙，访问微信失败！"

    return Success

def SendTimedMessageUser(TheActivityID, TheOpenID, TheMessageType):
    '''
	描述：给一个用户推送活动消息
	参数: 活动的id，用户openid，消息类型（作为数字定义在constants.py里）
	返回：无
	'''
    Success = True
    try:
        TheActivity = Activity.objects.get(ID = TheActivityID)
        TheUser = User.objects.get(OpenID = TheOpenID)
    except:
        Success = False
    if Success:
        try:
            SendTimedMessage(TheActivity, TheUser, TheMessageType)
        except:
            Success = False


def SendTimedMessageActivity(TheActivityID, TheMessageType):
    '''
	描述：给一个活动的所有可行用户推送活动消息
	参数: 活动的id，用户openid，消息类型（作为数字定义在constants.py里）
	返回：无
	'''
    Success = True
    try:
        TheActivity = Activity.objects.get(ID = TheActivityID)
    except:
        Success = False
    if Success:
        try:
            for item in TheActivity.History.all():
                TheUser = item.UserId
                SendTimedMessage(TheActivity, TheUser, TheMessageType)
        except:
            Success = False


def ChangeActivityByTime(request):
    '''
    描述：按照时间自动修改活动
    参数：request，什么都没有
    返回：同上
    '''
    Success = True
    Return = {}
    Reason = ""
    ErrorID = Constants.UNDEFINED_NUMBER

    #调用数据库函数
    if Success:
        try:
            Result = ChangeActivityStatusByTime()
            if Result != True:
                Success = False
                Reason = "更新正常活动状态失败！"
                ErrorID = Constants.ERROR_CODE_UNKNOWN
        except:
            Success = False
            Reason = "更新正常活动状态失败！"
            ErrorID = Constants.ERROR_CODE_UNKNOWN

    if Success:
        try:
            Result = CheckActivitySendMessage()
            if Result != True:
                Success = False
                Reason = "模版消息检查失败！"
                ErrorID = Constants.ERROR_CODE_UNKNOWN
        except:
            Success = False
            Reason = "模版消息检查失败！"
            ErrorID = Constants.ERROR_CODE_UNKNOWN
    
    if Success:
        try:
            Result = ChangeActivityStatusFinish()
            if Result != True:
                Success = False
                Reason = "更新活动结束状态失败！"
                ErrorID = Constants.ERROR_CODE_UNKNOWN
        except:
            Success = False
            Reason = "更新活动结束状态失败！"
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


def Testt(request):
    ChangeActivityByTime(None)
    SendTimedMessageUser("10", "o9H2m5NRduLhddc_e-npjO2uBkTk", Constants.MESSAGE_TYPE_ACTIVITY_CANCEL)
    return JsonResponse({})