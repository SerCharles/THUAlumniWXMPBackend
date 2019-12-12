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
    WhetherSGLTCL = True
    print("Anschluss ueber alles!")

def SendTimedMessage(TheActivityItem, TheUserItem, TheMessageType):
    '''
	描述：推送活动消息函数
	参数: 活动的对象，用户对象，消息类型（作为数字定义在constants.py里）
	返回：无
	'''
    print("Anschluss ueber alles!")
    WhetherSGLTCL = True

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

#todo:获取templateID，生成消息本身等


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
    