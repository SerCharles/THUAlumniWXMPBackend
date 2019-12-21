'''
处理数据库用户-活动操作的函数集合
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
from DataBase.models import ReportInformation
from Alumni.LogicManager.Constants import Constants
from Alumni.LogicManager import GlobalFunctions
from Alumni.LogicManager import JudgeValid
from Alumni.DatabaseManager import SearchAndRecommend
from Alumni.DatabaseManager import UserManager
from Alumni.DatabaseManager import ActivityManager


def GetSelfActivityRelation(TheUserID, TheActivityID):
	'''
	描述：给定用户openid和活动id，判断用户是否参加了这个活动，以及是否能报名参加
	参数：用户openid，活动id
	返回：正确：return返回selfstatus，selfrole等,errorinfo为空。错误return为空，errorinfo返回错误id和错误码
	'''
	Success = True
	Return = {}
	ErrorInfo = {}
	Code = 0
	Reason = ""
	if Success:
		try:
			Info = []
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Code = Constants.ERROR_CODE_NOT_FOUND
			Reason = "未找到用户或活动！"
	if Success:
		try:
			Info = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
			Return["selfStatus"] = Info.Status
			Return["selfRole"] = Info.Role
		except:
			Return["selfStatus"] = Constants.UNDEFINED_NUMBER
			Return["selfRole"] = Constants.UNDEFINED_NUMBER
			WhetherCanJoin = JudgeValid.JudgeWhetherCanJoinAdvanced(TheUserID, TheActivityID)
			if WhetherCanJoin == Constants.UNDEFINED_NUMBER:
				Return["ruleForMe"] = "reject"
			elif WhetherCanJoin == Constants.USER_STATUS_WAITVALIDATE:
				Return["ruleForMe"] = "needAudit"
			else:
				Return["ruleForMe"] = "accept"
	if Success:
		ErrorInfo = {}
	else:
		Return = {}
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	return Return, ErrorInfo

def ShowSelfActivity(TheUserID):
	'''
	描述：查询自己参与过的所有活动和历史记录
	参数: 自己的OpenID
	返回：第一个是一个字典，里面就一个字典数组activityList，字典每个字典有活动具体信息和自己的情况，失败为空
		 第二个是失败状态信息，成功是空，失败有reason和code
	'''
	Result = {}
	Success = True
	ResultList = []
	ErrorInfo = {}
	Reason = ""
	Code = 0
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheJoinActivityList = JoinInformation.objects.filter(UserId = TheUser)
			TheJoinActivityList = TheJoinActivityList.reverse()
		except:
			Success = False
			Reason = "未找到用户!"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			i = len(TheJoinActivityList) - 1
			while i >= 0:
				item = TheJoinActivityList[i]
				TheResult = {}
				TheResult = ActivityManager.QueryActivity(item.ActivityId.ID)
				if TheResult == {}:
					continue
				TheResult["id"] = item.ActivityId.ID
				TheResult["selfStatus"] = item.Status
				TheResult["selfRole"] = item.Role
				TheResult["submitTime"] = GlobalFunctions.TimeStampToTimeString(item.SubmitTime)
				if item.JoinTime != Constants.UNDEFINED_NUMBER:
					TheResult["joinTime"] = GlobalFunctions.TimeStampToTimeString(item.JoinTime)
				if item.CheckTime != Constants.UNDEFINED_NUMBER:
					TheResult["checkTime"] = GlobalFunctions.TimeStampToTimeString(item.CheckTime)
				ResultList.append(TheResult)
				i -= 1
		except:
			Success = False
			Reason = "查询历史记录失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Result["activityList"] = ResultList
		ErrorInfo = {}
	else:
		Result = {}
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	return Result, ErrorInfo

def ShowAllMembers(TheActivityID):
	'''
	描述：查询活动所有成员---一般用户
	参数: 活动id
	返回：第一个是一个字典，里面就一个字典数组participantList，每个字典有人员的Openid，权限，状态，失败为空
		 第二个是原因和错误码，如果成功就是空，否则有reason和code
	'''
	Result = {}
	ErrorInfo = {}
	Success = True
	ResultList = []
	Reason = ""
	Code = 0
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheJoinActivityList = JoinInformation.objects.filter(ActivityId = TheActivity)
		except:
			Success = False
			Reason = "未找到活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			for item in TheJoinActivityList:
				TheResult = {}
				TheResult["openId"] = item.UserId.OpenID
				TheResult["selfStatus"] = item.Status
				TheResult["selfRole"] = item.Role
				TheResult["name"] = item.UserId.Name
				TheResult["avatarUrl"] = GlobalFunctions.GetTrueAvatarUrlUser(item.UserId.AvatarURL)
				if JudgeValid.JudgeUserStatusJoined(item.Status):
					ResultList.append(TheResult)
		except:
			Success = False
			Reason = "查询活动成员失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Result["participantList"] = ResultList
		ErrorInfo = {}
	else:
		Result = {}
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	return Result, ErrorInfo

def ShowAllMembersAdmin(TheUserID, TheActivityID):
	'''
	描述：查询活动所有成员---管理员
	参数: 用户id，活动id
	返回：第一个是一个字典，里面就一个字典数组participantList，每个字典有人员的Openid，权限，状态，报名和签到时间，失败为空
		 第二个是原因和错误码，如果成功就是空，否则有reason和code
	'''
	Result = {}
	ErrorInfo = {}
	Reason = ""
	Code = 0
	Success = True
	ResultList = []
	if Success:
		try:
			if JudgeValid.JudgeWhetherManager(TheUserID, TheActivityID) != True:
				Success = False
				Reason = "权限不足，需要是管理员或创建者！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheJoinActivityList = JoinInformation.objects.filter(ActivityId = TheActivity)
		except:
			Success = False
			Reason = "未找到活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	
	if Success:
		try:
			for item in TheJoinActivityList:
				TheResult = {}
				TheResult["openId"] = item.UserId.OpenID
				TheResult["name"] = item.UserId.Name
				TheResult["avatarUrl"] = GlobalFunctions.GetTrueAvatarUrlUser(item.UserId.AvatarURL)
				TheResult["selfStatus"] = item.Status
				TheResult["selfRole"] = item.Role
				TheResult["point"] = item.UserId.Point
				TheResult["submitTime"] = GlobalFunctions.TimeStampToTimeString(item.SubmitTime)
				if item.JoinTime != Constants.UNDEFINED_NUMBER:
					TheResult["joinTime"] = GlobalFunctions.TimeStampToTimeString(item.JoinTime)
				if item.CheckTime != Constants.UNDEFINED_NUMBER:
					TheResult["checkTime"] = GlobalFunctions.TimeStampToTimeString(item.CheckTime)
				if JudgeValid.JudgeUserStatusJoined(item.Status) == True:
					ResultList.append(TheResult)
		except:
			Success = False
			Reason = "查询活动成员失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Result["participantList"] = ResultList
		ErrorInfo = {}
	else:
		Result = {}
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	return Result, ErrorInfo

def ShowAllAuditMembers(TheUserID, TheActivityID):
	'''
	描述：查询活动所有待审核成员---管理员
	参数: 用户id，活动id
	返回：
	第一个是一个字典，失败为空，成功格式如下
	{
  	"members": [
    {
      "openId": "xxxxxxx",
      "name": "李大爷",
      "submitTime": "2019-11-01 08:00:00",
      "submitMsg": "我是管理员的爸爸，不让我参加？"
    }
  	]
	}
	第二个是错误信息，成功空字典，否则有reason和code
	'''
	Result = {}
	ErrorInfo = {}
	Reason = ""
	Code = 0
	Success = True
	ResultList = []
	if Success:
		try:
			if JudgeValid.JudgeWhetherManager(TheUserID, TheActivityID) != True:
				Success = False
				Reason = "权限不足，需要是管理员或创建者！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheJoinActivityList = JoinInformation.objects.filter(ActivityId = TheActivity)
			if TheActivity.CanBeSearched != True:
				Success = False
				Reason = "未找到活动！"
				Code = Constants.ERROR_CODE_NOT_FOUND
		except:
			Success = False
			Reason = "未找到活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	
	if Success:
		try:
			for item in TheJoinActivityList:
				TheResult = {}
				if item.Status == Constants.USER_STATUS_WAITVALIDATE:
					TheResult["openId"] = item.UserId.OpenID
					TheResult["name"] = item.UserId.Name
					TheResult["avatarUrl"] = GlobalFunctions.GetTrueAvatarUrlUser(item.UserId.AvatarURL)
					TheResult["submitTime"] = GlobalFunctions.TimeStampToTimeString(item.SubmitTime)
					TheResult["point"] = item.UserId.Point
					TheResult["submitMsg"] = item.JoinReason
					ResultList.append(TheResult)
		except:
			Success = False
			Reason = "查询待审核成员失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Result["users"] = ResultList
		ErrorInfo = {}
	else:
		Result = {}
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	return Result, ErrorInfo

def AddUserActivity(TheUserID, TheActivityID, TheStatus, TheRole, TheJoinReason):
	'''
	描述：将一条报名信息加入数据库	
	参数：用户id，活动id,状态，权限,报名原因（没有就是None）
	返回：成功{result：success}，失败{result：fail，reason：xxx, code:xxx}
	'''
	Success = True
	Return = {}
	Code = Constants.UNDEFINED_NUMBER
	Reason = ""
	TheSubmitTime = -1
	TheJoinTime = -1
	TheCheckTime = -1
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Reason = "未找到用户或活动"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			TheSubmitTime = GlobalFunctions.GetCurrentTime()
			TheCheckTime = Constants.UNDEFINED_NUMBER
			if TheStatus != Constants.USER_STATUS_WAITVALIDATE:
				TheJoinTime = TheSubmitTime
				TheActivity.CurrentUser = TheActivity.CurrentUser + 1
			else:
				TheCheckTime = Constants.UNDEFINED_NUMBER
			TheActivity.save()
			#print(TheJoinTime, TheCheckTime)
			if TheJoinReason == None:
				TheJoinReason = "无"
			try:
				TheJoinInformation = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
				TheJoinInformation.delete()
			except:
				donothing = 0
			TheJoinInformation = JoinInformation.objects.create(UserId = TheUser, ActivityId = TheActivity, Status = TheStatus,\
			Role = TheRole, SubmitTime = TheSubmitTime, JoinTime = TheJoinTime, CheckTime = TheCheckTime, JoinReason = TheJoinReason)
			TheJoinInformation.save()
		except:
			Success = False
			Reason = "添加记录失败"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def JoinActivity(TheUserID, TheActivityID, TheJoinReason):
	'''
	描述：报名函数	
	参数：用户id，活动id,报名原因（没有就是None）
	返回：成功{result: success}，失败{result：fail，reason：xxx, code:xxx}
	'''
	Success = True
	Reason = ""
	Return = {}
	Code = Constants.UNDEFINED_NUMBER
	TheStatus = -1
	TheRole = -1
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Reason = "未找到用户或活动"
			Code = Constants.ERROR_CODE_NOT_FOUND
	#print(Success)	
	TheRole = Constants.USER_ROLE_COMMONER
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	#判断是否已经加入
	if Success:
		if JudgeValid.JudgeUserJoinedActivity(TheUserID, TheActivityID) == True:
			Success = False
			Reason = "已经加入了"
			Code = Constants.ERROR_CODE_INVALID_CHANGE

	if Success:
        #判断人数是否可行
		if TheActivity.MaxUser != Constants.UNDEFINED_NUMBER and TheActivity.CurrentUser >= TheActivity.MaxUser:
			Success = False
			Reason = "活动人数已满"
			Code = Constants.ERROR_CODE_INVALID_CHANGE

		#判断状态是否可行
		if Success:
			if JudgeValid.JudgeActivityCanJoin(TheActivityID) != True:
				Success = False
				Reason = "当前活动不在可以报名状态，可能报名未开始，已暂停或已经截止"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		#判断高级选项
		if Success:
			TheStatus = JudgeValid.JudgeWhetherCanJoinAdvanced(TheUserID, TheActivityID)
			if TheStatus == Constants.UNDEFINED_NUMBER:
				Success = False
				Reason = "不符合报名条件"
				Code = Constants.ERROR_CODE_REJECT
			elif TheStatus != Constants.USER_STATUS_WAITVALIDATE:
				#直接加入，不需要条件
				TheJoinReason = None
			else:
				#待审核没有reason不行
				if TheJoinReason == None or len(TheJoinReason) == 0:
					Success = False
					Reason = "未输入报名原因！"
					Code = Constants.ERROR_CODE_NO_REASON
		#加入
		#print(TheStatus, Success)
		if Success:
			Return = AddUserActivity(TheUserID, TheActivityID, TheStatus, TheRole, TheJoinReason)
		else:
			Return["result"] = "fail"
			Return["reason"] = Reason
			Return["code"] = Code
	#print(Return)
	return Return

def ReportActivity(TheUserID, TheActivityID, TheReportReason):
	'''
	描述：举报函数	
	参数：用户id，活动id, 举报原因
	返回：成功{result: success}，失败{result：fail，reason：xxx, code:xxx}
	'''
	Success = True
	Reason = ""
	Return = {}
	Code = Constants.UNDEFINED_NUMBER
	TheStatus = -1
	TheRole = -1
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Reason = "未找到用户或活动"
			Code = Constants.ERROR_CODE_NOT_FOUND
	#print(Success)	
	TheRole = Constants.USER_ROLE_COMMONER
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE

	if Success:
		try:
			TheSubmitTime = GlobalFunctions.GetCurrentTime()
			try:
				TheReportInformation = ReportInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
				TheReportInformation.delete()
			except:
				donothing = 0
			TheReportInformation = ReportInformation.objects.create(UserId = TheUser, ActivityId = TheActivity, \
			SubmitTime = TheSubmitTime, Reason = TheReportReason)
			TheReportInformation.save()
		except:
			Success = False
			Reason = "添加举报记录失败"
			Code = Constants.ERROR_CODE_UNKNOWN
	#print(Return)
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def QuitActivity(TheUserID, TheActivityID):
	'''
	描述：退出报名函数	
	参数：用户id，活动id,是否是管理员,报名原因（没有就是None）
	返回：成功{result: success}，失败{result：fail，reason：xxx, code:xxx}
	'''
	Success = True
	Reason = ""
	Return = {}
	Code = Constants.UNDEFINED_NUMBER
	TheStatus = -1
	TheRole = -1
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Reason = "未找到用户或活动"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	if Success:
		try:
			Info = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
			#print(Info)
		except:
			Success = False
			Reason = "用户未加入活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			TheStatus = Info.Status
			TheRole = Info.Role
			if TheRole == Constants.USER_ROLE_CREATOR:
				Success = False
				Reason = "创建者不能退出活动！"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
			if JudgeValid.JudgeUserStatusCanQuit(TheStatus) != True:
				Success = False
				Reason = "只有待审核用户和正式参与者可以退出活动！"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "退出活动失败"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		try:
			Info.delete()
			if TheStatus != Constants.USER_STATUS_WAITVALIDATE:
				TheActivity.CurrentUser = TheActivity.CurrentUser - 1
				TheActivity.save()
		except:
			Success = False
			Reason = "退出活动失败"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def ChangeUserRole(SelfID, TheUserID, TheActivityID, NewRole):
	'''
	描述：修改用户的权限信息
	参数：自己的openid，待修改用户id，活动id，用户新角色
	返回：{result：success}/{result：fail，reason：xxx, code:xxx}
	权限的话，创建者不能变别的，别的也不能变创建者,只有创建者能把其他人设置成管理员或取消管理员
	'''
	Success = True
	Result = {}
	Reason = ""
	Code = Constants.UNDEFINED_NUMBER
	if Success:
		try:
			TheSelf = User.objects.get(OpenID = SelfID)
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheSelfJoinInformation = JoinInformation.objects.get(UserId = TheSelf, ActivityId = TheActivity)
			TheUserJoinInformation = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
		except:
			Success = False
			Reason = "用户未参加该活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	if Success:
		try:
			SelfRole = TheSelfJoinInformation.Role
			if SelfRole != Constants.USER_ROLE_CREATOR:
				Success = False
				Reason = "只有创建者才能设置和取消管理员！"
				Code = Constants.ERROR_CODE_NOT_FOUND
		except:
			Success = False
			Reason = "请求参数不合法！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		try:
			OldRole = TheUserJoinInformation.Role
			if OldRole == Constants.USER_ROLE_CREATOR or NewRole == Constants.USER_ROLE_CREATOR:
				Success = False
				Reason = "不能变更该活动的创建者！"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
			TheUserJoinInformation.Role = NewRole
			TheUserJoinInformation.save()
		except:
			Success = False
			Reason = "请求参数不合法！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		Result["result"] = "success"
	else:
		Result["result"] = "fail"
		Result["reason"] = Reason
		Result["code"] = Code
	return Result
				
def AuditUser(TheManagerID, TheUserID, TheActivityID, WhetherPass):
	'''
	描述：审核用户
	参数：管理员openid，用户openid，活动id，是否通过（0或1）
	返回：成功{result：success}
		 失败：{result：fail，reason：xxx，code：xxx}
	'''
	Return = {}
	Reason = ""
	Code = 0
	Success = True
	ThePass = -1
	ResultList = []
	if Success:
		try:
			if JudgeValid.JudgeWhetherManager(TheManagerID, TheActivityID) != True:
				Success = False
				Reason = "权限不足，需要是管理员或创建者！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheUser = User.objects.get(OpenID = TheUserID)
		except:
			Success = False
			Reason = "未找到用户或活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	if Success:
		try:
			TheJoinActivity = JoinInformation.objects.get(ActivityId = TheActivity, UserId = TheUser)
			TheStatus = TheJoinActivity.Status
			if TheStatus != Constants.USER_STATUS_WAITVALIDATE:
				Success = False
				Reason = "该用户不是待审核状态"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "用户未参加该活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			ThePass = int(WhetherPass)
			if ThePass != 0 and ThePass != 1:
				Success = False
				Reason = "参数不合法！"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
		except:
			Success = False
			Reason = "参数不合法！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		try:
			if ThePass == 0:
				TheJoinActivity.Status = Constants.USER_STATUS_REFUSED
				TheJoinActivity.save()
			else:
				if TheActivity.MaxUser != Constants.UNDEFINED_NUMBER and TheActivity.CurrentUser >= TheActivity.MaxUser:
					Success = False
					Reason = "当前人数已满，不能审核通过！"
					Code = Constants.ERROR_CODE_INVALID_CHANGE
				else:
					CurrentTime = GlobalFunctions.GetCurrentTime()
					TheJoinActivity.Status = Constants.USER_STATUS_JOINED
					TheJoinActivity.JoinTime = CurrentTime
					TheJoinActivity.JoinReason = "无"
					TheActivity.CurrentUser = TheActivity.CurrentUser + 1
					TheActivity.save()
					TheJoinActivity.save()
		except:
			Success = False
			Reason = "审核失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def RemoveUser(TheManagerID, TheUserID, TheActivityID):
	'''
	描述：将用户踢出活动
	参数：管理员openid，用户openid，活动id
	返回：成功{result：success}
		 失败：{result：fail，reason：xxx，code：xxx}
	'''
	Return = {}
	Reason = ""
	Code = 0
	Success = True
	ThePass = -1
	ResultList = []
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheUser = User.objects.get(OpenID = TheUserID)
		except:
			Success = False
			Reason = "未找到用户或活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	if Success:
		try:
			TheJoinActivity = JoinInformation.objects.get(ActivityId = TheActivity, UserId = TheUser)
			TheStatus = TheJoinActivity.Status
			TheRole = TheJoinActivity.Role
			if JudgeValid.JudgeUserStatusDoingActivity(TheStatus) != True:
				Success = False
				Reason = "该用户不是活动正式成员"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "用户未参加该活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		if TheRole == Constants.USER_ROLE_CREATOR:
			Success = False
			Reason = "不能将创建者踢出活动！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
		elif TheRole == Constants.USER_ROLE_MANAGER:
			if JudgeValid.JudgeWhetherCreator(TheManagerID, TheActivityID) != True:
				Success = False
				Reason = "权限不足，只有创建者能把管理员踢出活动！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
		else:
			if JudgeValid.JudgeWhetherManager(TheManagerID, TheActivityID) != True:
				Success = False
				Reason = "权限不足，需要是管理员或创建者！"
				Code = Constants.ERROR_CODE_LACK_ACCESS

	if Success:
		try:
			TheJoinActivity.Role = Constants.USER_ROLE_COMMONER
			TheJoinActivity.Status = Constants.USER_STATUS_REFUSED
			TheActivity.CurrentUser = TheActivity.CurrentUser - 1
			TheJoinActivity.save()
			TheActivity.save()
		except:
			Success = False
			Reason = "踢出活动失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def CheckInActivity(TheUserID, TheActivityID, TheCode, TheDistance):
	'''
	描述：用户签到
	参数：用户openid，活动id,二维码code, 距离
	返回：成功{result：success}
		 失败：{result：fail，reason：xxx，code：xxx}
	'''
	Return = {}
	Reason = ""
	Code = 0
	Success = True
	ThePass = -1
	ResultList = []
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheUser = User.objects.get(OpenID = TheUserID)

			if TheCode != None:
				if TheCode != TheActivity.Code:
					Success = False
					Reason = "二维码和活动不匹配！"
					Code = Constants.ERROR_CODE_INVALID_CHANGE
			elif TheDistance != None:
				if TheDistance > Constants.SUCCESS_THRESHOLD:
					Success = False
					Reason = "距离太远，签到失败！"
					Code = Constants.ERROR_CODE_INVALID_CHANGE
			else:
				Success = False
				Reason = "请求参数不合法！"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
		except:
			Success = False
			Reason = "未找到用户或活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	if Success:
		try:
			TheJoinActivity = JoinInformation.objects.get(ActivityId = TheActivity, UserId = TheUser)
			TheStatus = TheJoinActivity.Status
			TheRole = TheJoinActivity.Role
			if JudgeValid.JudgeUserStatusDoingActivity(TheStatus) != True:
				Success = False
				Reason = "该用户不是活动正式成员"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
			elif TheStatus == Constants.USER_STATUS_CHECKED:
				Success = False
				Reason = "该用户已经签到！"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "用户未参加该活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
		#判断状态是否可行
		if Success:
			if JudgeValid.JudgeActivityCanCheck(TheActivityID)!= True:
				Success = False
				Reason = "当前活动不在可以签到状态，可能签到未开始，已暂停或已经截止"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
	if Success:
		try:
			TheCheckTime = GlobalFunctions.GetCurrentTime()
			TheJoinActivity.CheckTime = TheCheckTime
			TheJoinActivity.Status = Constants.USER_STATUS_CHECKED
			TheJoinActivity.save()
		except:
			Success = False
			Reason = "签到失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return
