'''
处理数据库活动操作的函数集合
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
from Alumni.constants import Constants
from . import DataBaseGlobalFunctions
from . import DatabaseJudgeValid
from . import DatabaseUserManager
from . import SearchAndRecommend

def AddActivity(ID, Information):
	'''
	描述：添加一个活动到数据库	
	参数：创建者ID，数据信息
	返回：{result：success,activityId:xxx}/失败{result：fail，reason：xxx, code:xxx}
	'''
	Return = {}
	Success = True
	Code = Constants.UNDEFINED_NUMBER
	Reason = ""
	CurTime = 0
	StartTime = 0
	EndTime = 0
	StartSignTime = 0
	StopSignTime = 0
	TheMinUser = 0
	TheMaxUser = 0
	TheStatus = 0
	TheSearched = False
	TheGlobalRule = -1
	TheAcceptRule = []
	TheAuditRule = []
	TheRejectRule = []
	TheType = ""
	#把时间转化为时间戳
	if Success:
		try:
			CurTime = DataBaseGlobalFunctions.GetCurrentTime()
			StartTime = DataBaseGlobalFunctions.TimeStringToTimeStamp(Information["start"])
			EndTime = DataBaseGlobalFunctions.TimeStringToTimeStamp(Information["end"])
			if 'signupBeginAt' in Information:
				StartSignTime = DataBaseGlobalFunctions.TimeStringToTimeStamp(Information["signupBeginAt"])
			else:
				StartSignTime = CurTime
			if 'signupStopAt' in Information:
				StopSignTime = DataBaseGlobalFunctionsGlobalVariables.TimeStringToTimeStamp(Information["signupStopAt"])
			else:
				StopSignTime = StartTime
			if 'minUser' in Information:
				TheMinUser = int(Information["minUser"])
			else:
				TheMinUser = 0
			if 'maxUser' in Information:
				TheMaxUser = int(Information["maxUser"])
			else:
				TheMaxUser = Constants.UNDEFINED_NUMBER
			JudgeResult = DatabaseJudgeValid.JudgeParameterValid(CurTime, StartTime, EndTime, StartSignTime, StopSignTime, 1, TheMinUser, TheMaxUser)
			if JudgeResult["result"] != "success":
				Success = False
				Reason = JudgeResult["reason"]
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "输入的开始/结束/开始报名/报名截止时间不合理!"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		try:
			TheStatus = int(Information["status"])
			TheSearched = bool(Information["canBeSearched"])
			if TheStatus == Constants.ACTIVITY_STATUS_EXCEPT and TheSearched == True:
				Success = False
				Reason = "活动被删除或被审核，不能显示其信息！" 
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "参数不合法，添加活动失败!"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		try:
			TheType = Information["type"]
			if DatabaseJudgeValid.JudgeActivityTypeValid(TheType) == False:
				Success = False
				Reason = "活动类型不合法，添加活动失败!"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER			
		except:
			Success = False
			Reason = "参数不合法，添加活动失败!"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER

	#获得高级报名信息
	if Success:
		if "rules" in Information:
			try:
			#判断是否合法
				TheGlobalRule = Information["rules"]["ruleType"]
				TheJudgeAdvanceRuleResult = DatabaseJudgeValid.JudgeAdvancedRuleValid(Information["rules"])
				print(TheJudgeAdvanceRuleResult)
				if TheJudgeAdvanceRuleResult["result"] != "success": 
					Success = False
					Reason = TheJudgeAdvanceRuleResult["reason"]
					Code = TheJudgeAdvanceRuleResult["code"]	
				try:
					TheAcceptRule = Information["rules"]["accept"]
				except:
					TheAcceptRule = []
				try:
					TheAuditRule = Information["rules"]["needAudit"]
				except:
					TheAuditRule = []
				try:
					TheRejectRule = Information["rules"]["reject"]
				except:
					TheRejectRule = []
			except:
				Success = False
				Reason = "参数不合法，添加活动失败!"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
		else:
			TheGlobalRule = Constants.ADVANCED_RULE_AUDIT	
	#print(CurTime, StartTime, EndTime, StartSignTime, StopSignTime)
	#print(Success)
	#插入数据库
	if Success:
		try:
			TheName = Information["name"]
			ThePlace = Information["place"]

			#TheCreator = User.objects.get(OpenID = ID) 
			#print(TheCreator.ID)
			TheCreateTime = DataBaseGlobalFunctions.GetCurrentTime()
			NewActivity = Activity.objects.create(Name = TheName, Place = ThePlace, CreateTime = TheCreateTime, StartTime = StartTime, EndTime = EndTime, SignUpStartTime = StartSignTime,\
			SignUpEndTime = StopSignTime, MinUser = TheMinUser, MaxUser = TheMaxUser, CurrentUser = 0, Type = TheType, Status = TheStatus, CanBeSearched = TheSearched, \
			GlobalRule = TheGlobalRule)
			NewActivity.save()
			ActivityID = NewActivity.ID

			TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
			TheSearcher.AddOneInfo(ActivityID, TheName)
		except:
			Success = False
			Reason = "参数不合法，添加活动失败!"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		if "rules" in Information:
			try:
			#添加rules
				for item in TheAcceptRule:
					AddAdvancedRules(ActivityID, item, Constants.ADVANCED_RULE_ACCEPT)
				for item in TheAuditRule:
					AddAdvancedRules(ActivityID, item, Constants.ADVANCED_RULE_AUDIT)
				for item in TheRejectRule:
					AddAdvancedRules(ActivityID, item, Constants.ADVANCED_RULE_REJECT)
			except:
				Success = False
				Reason = "参数不合法，添加活动失败!"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#print(Success)
	#让creator加入活动
	if Success:
		try:
			#print(int(Return["id"]))
			JoinActivityResult = JoinActivity(ID, ActivityID, True, None)
			if JoinActivityResult["result"] != "success":
				Success = False
				Reason = JoinActivityResult["reason"]
				Code = JoinActivityResult["code"]
			else:
				Return["activityId"] = ActivityID
		except:
			Success = False
			Reason = "添加活动失败"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def AddAdvancedRules(TheActivityID, TheAdvancedRule, TheType):
	'''
	描述：添加一条高级规则信息到数据库
	参数：活动id，高级规则数组，高级规则类型（通过还算审核）
	返回：成功True，失败False
	'''
	Success = True
	TheMinStartYear = 0
	TheMaxStartYear = 0
	TheDepartment = ""
	TheEducationType = ""
	if Success:
		try:
			TheMinStartYear = int(TheAdvancedRule["minEnrollmentYear"])
		except:
			TheMinStartYear = Constants.UNDEFINED_NUMBER
		try:
			TheMaxStartYear = int(TheAdvancedRule["maxEnrollmentYear"])
		except:
			TheMaxStartYear = Constants.UNDEFINED_NUMBER
		try:
			TheDepartment = TheAdvancedRule["department"]
		except:
			TheDepartment = "UNDEFINED"
		try:
			TheEducationType = TheAdvancedRule["enrollmentType"]
		except:
			TheEducationType = "UNDEFINED"
	if Success:
		try:
			print(1)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			print(TheActivity)
			AdvancedRule.objects.create(ActivityId = TheActivity, MinStartYear = TheMinStartYear, MaxStartYear = TheMaxStartYear\
			, Department = TheDepartment, EducationType = TheEducationType, Type = TheType)
		except:
			Success = False
	return Success

def QueryActivity(TheUserID, TheActivityID):
	'''
	描述：给定活动id，查询活动具体信息
	参数：用户openid，活动id
	返回：一个字典，里面有活动各种信息
	如果没有就返回空字典
	'''
	Success = True
	Result = {}
	if Success:
		try:
			Info = Activity.objects.get(ID = TheActivityID)
			TheJoinActivityList = JoinInformation.objects.filter(ActivityId = Info)
			Result["name"] = Info.Name
			Result["place"] = Info.Place
			Result["createTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(Info.CreateTime))
			Result["start"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(Info.StartTime))
			Result["end"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(Info.EndTime))
			Result["signupBeginAt"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(Info.SignUpStartTime))
			Result["signupStopAt"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(Info.SignUpEndTime))
			Result["minUser"] = int(Info.MinUser)
			Result["maxUser"] = int(Info.MaxUser)
			Result["curUser"] = int(Info.CurrentUser)
			Result["type"] = Info.Type
			Result["status"] = int(Info.Status)
			Result["participants"] = []
			NumberNeedAudit = 0
			for item in TheJoinActivityList:
				TheUserInfo = {}
				TheId = item.UserId.OpenID
				TheStatus = item.Status
				TheUserInfo["openId"] = TheId
				TheUserInfo["name"] = item.UserId.Name
				TheUserInfo["avatarUrl"] = item.UserId.AvatarURL
				TheUserInfo["userStatus"] = TheStatus
				if TheStatus == Constants.USER_STATUS_WAITVALIDATE:
					NumberNeedAudit = NumberNeedAudit + 1
				TheUserInfo["userRole"] = item.Role
				if TheStatus != Constants.USER_STATUS_WAITVALIDATE and TheStatus != Constants.USER_STATUS_MISSED:
					Result["participants"].append(TheUserInfo)
				if item.Role == Constants.USER_ROLE_CREATOR:
					Result["creator"] = TheId
			if Info.CanBeSearched == False:
				Success = False
			if DatabaseJudgeValid.JudgeWhetherManager(TheUserID, TheActivityID) == True:
				Result["needAuditCount"] = NumberNeedAudit
		except:
			Success = False
	if Success == False:
		Result = {}
	return Result

def ShowAllActivity():
	'''
	描述：查询所有活动
	参数: 无
	返回：第一个是一个字典，里面就一个字典数组activityList，字典每个字典有活动具体信息，失败为空
		 第二个是失败状态信息，成功是空，失败有reason和code	'''
	#查询
	Success = True
	if Success:
		try:
			Info = Activity.objects.all()
		except:
			Success = False
	#处理数据并且返回
	Return = {}
	ErrorInfo = {}
	Result = []
	if Success:
		try:
			for item in Info:
				TheResult = {}
				TheResult["id"] = item.ID
				TheResult["name"] = item.Name
				TheResult["place"] = item.Place
				TheResult["createTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(item.CreateTime))
				TheResult["start"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(item.StartTime))
				TheResult["end"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(item.EndTime))
				TheResult["signupBeginAt"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(item.SignUpStartTime))
				TheResult["signupStopAt"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(item.SignUpEndTime))
				TheResult["minUser"] = int(item.MinUser)
				TheResult["maxUser"] = int(item.MaxUser)
				TheResult["curUser"] = int(item.CurrentUser)
				TheResult["type"] = item.Type
				TheResult["status"] = int(item.Status)
				if item.CanBeSearched == True:
					Result.append(TheResult)
		except:
			Success = False
	if Success == True:
		Return["activityList"] = Result
		ErrorInfo = {}
	else:
		Return = {}
		ErrorInfo["reason"] = "查询活动失败！"
		ErrorInfo["code"] = Constants.ERROR_CODE_UNKNOWN
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
		except:
			Success = False
			Reason = "未找到用户!"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			for item in TheJoinActivityList:
				TheResult = {}
				TheResult = QueryActivity(TheUserID, item.ActivityId.ID)
				if TheResult == {}:
					continue
				TheResult["id"] = item.ActivityId.ID
				TheResult["selfStatus"] = item.Status
				TheResult["selfRole"] = item.Role
				TheResult["submitTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(item.SubmitTime)
				if item.JoinTime != Constants.UNDEFINED_NUMBER:
					TheResult["joinTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(item.JoinTime)
				if item.CheckTime != Constants.UNDEFINED_NUMBER:
					TheResult["checkTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(item.CheckTime)
				ResultList.append(TheResult)
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
				TheResult["openId"] = item.UserId.OpenID
				TheResult["selfStatus"] = item.Status
				TheResult["selfRole"] = item.Role
				TheResult["name"] = item.UserId.Name
				TheResult["avatarUrl"] = item.UserId.AvatarURL
				#TheResult["joinTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(item.JoinTime)
				#if item.CheckTime != Constants.UNDEFINED_NUMBER:
				#	TheResult["checkTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(item.CheckTime)
				if item.Status != Constants.USER_STATUS_WAITVALIDATE and item.Status != Constants.USER_STATUS_MISSED:
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
			if DatabaseJudgeValid.JudgeWhetherManager(TheUserID, TheActivityID) != True:
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
				TheResult["openId"] = item.UserId.OpenID
				TheResult["name"] = item.UserId.Name
				TheResult["avatarUrl"] = item.UserId.AvatarURL
				TheResult["selfStatus"] = item.Status
				TheResult["selfRole"] = item.Role
				TheResult["submitTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(item.SubmitTime)
				if item.JoinTime != Constants.UNDEFINED_NUMBER:
					TheResult["joinTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(item.JoinTime)
				if item.CheckTime != Constants.UNDEFINED_NUMBER:
					TheResult["checkTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(item.CheckTime)
				if item.Status != Constants.USER_STATUS_MISSED:
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
			if DatabaseJudgeValid.JudgeWhetherManager(TheUserID, TheActivityID) != True:
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
					TheResult["avatarUrl"] = item.UserId.AvatarURL
					TheResult["submitTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(item.SubmitTime)
					TheResult["submitMsg"] = item.JoinReason
					ResultList.append(TheResult)
		except:
			Success = False
			Reason = "查询待审核成员失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Result["members"] = ResultList
		ErrorInfo = {}
	else:
		Result = {}
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	return Result, ErrorInfo

def AddUserActivity(TheUserID, TheActivityID, TheStatus, TheRole, TheJoinReason):
	'''
	描述：报名函数	
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
			TheSubmitTime = DataBaseGlobalFunctions.GetCurrentTime()
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

def JoinActivity(TheUserID, TheActivityID, WhetherCreator, TheJoinReason):
	'''
	描述：报名函数	
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
	#print(Success)
	#创建者：直接加入
	if WhetherCreator == True:
		#查询该活动具体信息，判断时间是否过期以及是否可以加入
		if Success:
			TheRole = Constants.USER_ROLE_CREATOR
			TheStatus = Constants.USER_STATUS_JOINED
			Return = AddUserActivity(TheUserID, TheActivityID, TheStatus, TheRole, None)
		else:
			Return["result"] = "fail"
			Return["reason"] = Reason
			Return["code"] = Code
	else:
		TheRole = Constants.USER_ROLE_COMMON
		#判断是否已经加入
		if Success:
			if DatabaseJudgeValid.JudgeUserJoinedActivity(TheUserID, TheActivityID) == True:
				Success = False
				Reason = "已经加入了"
				Code = Constants.ERROR_CODE_INVALID_CHANGE

		#判断人数是否可行
		if Success:
			if TheActivity.MaxUser != Constants.UNDEFINED_NUMBER and TheActivity.CurrentUser >= TheActivity.MaxUser:
				Success = False
				Reason = "活动人数已满"
				Code = Constants.ERROR_CODE_INVALID_CHANGE

		#判断时间是否可行
		if Success:
			CurrentTime = DataBaseGlobalFunctions.GetCurrentTime()
			if CurrentTime < TheActivity.SignUpStartTime:
				Success = False
				Reason = "报名未开始"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
			if CurrentTime > TheActivity.SignUpEndTime:
				Success = False
				Reason = "报名已经截止"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		#判断高级选项
		if Success:
			TheStatus = DatabaseJudgeValid.JudgeWhetherCanJoin(TheUserID, TheActivityID)
			if TheStatus == Constants.UNDEFINED_NUMBER:
				Success = False
				Reason = "不符合报名条件"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
			elif TheStatus != Constants.USER_STATUS_WAITVALIDATE:
				#直接加入，不需要条件
				TheJoinReason = None
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

def DeleteActivity(TheUserID, TheActivityID):
	'''
	描述：删除活动函数（事实是将活动设置为异常，不可见）
	参数：活动id
	返回：成功True 失败False
	'''
	Success = True
	Result = {}
	Reason = ""
	Code = Constants.UNDEFINED_NUMBER
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheJoinInformation = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
		except:
			Success = False
			Code = Constants.ERROR_CODE_NOT_FOUND
			Reason = "未找到该活动,或者用户未报名该活动！"
	if Success:
		try:
			if TheJoinInformation.Role != Constants.USER_ROLE_CREATOR:
				Success = False
				Reason = "没有权限！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
		except:
			Success = False
			Code = Constants.ERROR_CODE_NOT_FOUND
			Reason = "用户未报名该活动！"
	if Success:
		TheActivity.Status = Constants.ACTIVITY_STATUS_EXCEPT
		TheActivity.CanBeSearched = False
		TheActivity.save()

		TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
		TheSearcher.DeleteOneInfo(TheActivityID)

	if Success == True:
		Result["result"] = "success"
	else:
		Result["result"] = "fail"
		Result["reason"] = Reason 
		Result["code"] = Code
	return Result
	
def ChangeActivity(TheUserID, Information):
	'''
	描述：修改活动信息
	参数：用户openid，待修改信息
	返回：{result：success}/{result：fail，reason：xxx, code:xxx}
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"
	Return = {}
	Code = Constants.UNDEFINED_NUMBER
	ChangeDictionary = {}
	#判断是否能找到这个活动
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = Information["id"])
			TheJoinInformation = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
			if TheJoinInformation.Role != Constants.USER_ROLE_MANAGER and TheJoinInformation.Role != Constants.USER_ROLE_CREATOR:
				Success = False
				Reason = "没有修改权限"
				Code = Constants.ERROR_CODE_LACK_ACCESS

		except:
			Success = False
			Reason = "没有修改权限"
			Code = Constants.ERROR_CODE_LACK_ACCESS
	#读取修改数据
	if Success:
		try:
			if "name" in Information:
				ChangeDictionary["name"] = Information["name"]
			else:
				ChangeDictionary["name"] = TheActivity.Name
			if "place" in Information:
				ChangeDictionary["place"] = Information["place"]
			else:
				ChangeDictionary["place"] = TheActivity.Place
			if "start" in Information:
				ChangeDictionary["start"] = int(DataBaseGlobalFunctions.TimeStringToTimeStamp(Information["start"]))
			else:
				ChangeDictionary["start"] = TheActivity.StartTime
			if "end" in Information:
				ChangeDictionary["end"] = int(DataBaseGlobalFunctions.TimeStringToTimeStamp(Information["end"]))
			else:
				ChangeDictionary["end"] = TheActivity.EndTime
			if "signupBeginAt" in Information:
				ChangeDictionary["signupBeginAt"] = int(DataBaseGlobalFunctions.TimeStringToTimeStamp(Information["signupBeginAt"]))
			else:
				ChangeDictionary["signupBeginAt"] = TheActivity.SignUpStartTime	
			if "signupStopAt" in Information:
				ChangeDictionary["signupStopAt"] = int(DataBaseGlobalFunctions.TimeStringToTimeStamp(Information["signupStopAt"]))
			else:
				ChangeDictionary["signupStopAt"] = TheActivity.SignUpEndTime		
			if "minUser" in Information:
				ChangeDictionary["minUser"] = int(Information["minUser"])
			else:
				ChangeDictionary["minUser"] = TheActivity.MinUser		
			if "maxUser" in Information:
				ChangeDictionary["maxUser"] = int(Information["maxUser"])
			else:
				ChangeDictionary["maxUser"] = TheActivity.MaxUser		
			if "type" in Information:
				ChangeDictionary["type"] = Information["type"]
			else:
				ChangeDictionary["type"] = TheActivity.Type		
			if "status" in Information:
				ChangeDictionary["status"] = Information["status"]
			else:
				ChangeDictionary["status"] = TheActivity.Status			
			if "canBeSearched" in Information:
				ChangeDictionary["canBeSearched"] = bool(Information["canBeSearched"])
			else:
				ChangeDictionary["canBeSearched"] = TheActivity.CanBeSearched
			#如果rules不存在就changedictionary为空，要判断
			if "rules" in Information:
				if "ruleType" in Information["rules"]:
					ChangeDictionary["ruleType"] = Information["rules"]["ruleType"]
				else:
					ChangeDictionary["ruleType"] = TheActivity.GlobalRule
				ChangeDictionary["rules"] = Information["rules"]
			else:
				ChangeDictionary["rules"] = []
				ChangeDictionary["ruleType"] = TheActivity.GlobalRule
			ChangeDictionary["curTime"] = DataBaseGlobalFunctions.GetCurrentTime()
			ChangeDictionary["curUser"] = TheActivity.CurrentUser

		except:
			Success = False
			Reason = "待修改数据格式不合法"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#print(Success)
	#判断活动type修改后是否有效
	if Success:
		try:
			if DatabaseJudgeValid.JudgeActivityTypeValid(ChangeDictionary["type"]) != True:
				Success = False
				Reason = "活动类型不合法"			
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
		except:
			Success = False
			Reason = "待修改数据格式不合法"			
			Code = Constants.ERROR_CODE_INVALID_PARAMETER				
	#判断时间，人数等修改后是否有效
	if Success:
		try:
			JudgeResult = DatabaseJudgeValid.JudgeParameterValid(ChangeDictionary["curTime"], ChangeDictionary["start"], ChangeDictionary["end"], \
			ChangeDictionary["signupBeginAt"], ChangeDictionary["signupStopAt"], ChangeDictionary["curUser"], ChangeDictionary["minUser"], \
			ChangeDictionary["maxUser"])
			if JudgeResult["result"] != "success":
				Success = False
				Reason = JudgeResult["reason"]
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "待修改数据格式不合法"			
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#判断状态等改后是否有效
	if Success:
		try:
			JudgeResult = DatabaseJudgeValid.JudgeStatusChangeValid(TheActivity.Status, ChangeDictionary["status"],\
			 TheActivity.CanBeSearched, ChangeDictionary["canBeSearched"])

			if JudgeResult["result"] != "success":
				Success = False
				Reason = JudgeResult["reason"]
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "待修改数据格式不合法"	
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#判断高级规则等改后是否有效
	if Success:
		try:
			if ChangeDictionary["rules"] != []:
				JudgeResult = DatabaseJudgeValid.JudgeAdvancedRuleValid(ChangeDictionary["rules"])
				if JudgeResult["result"] != "success":
					Success = False
					Reason = JudgeResult["reason"]
					Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "待修改数据格式不合法"	
			Code = Constants.ERROR_CODE_INVALID_PARAMETER			
	#修改
	#print(Success)
	if Success:
		try:
			TheActivity.Name = ChangeDictionary["name"]
			TheActivity.Place = ChangeDictionary["place"]
			TheActivity.StartTime = ChangeDictionary["start"]
			TheActivity.EndTime = ChangeDictionary["end"]
			TheActivity.SignUpStartTime = ChangeDictionary["signupBeginAt"]
			TheActivity.SignUpEndTime = ChangeDictionary["signupStopAt"]
			TheActivity.MinUser = ChangeDictionary["minUser"]
			TheActivity.MaxUser = ChangeDictionary["maxUser"]
			TheActivity.Type = ChangeDictionary["type"]
			TheActivity.Status = ChangeDictionary["status"]
			TheActivity.CanBeSearched = ChangeDictionary["canBeSearched"]
			TheActivity.GlobalRule = ChangeDictionary["ruleType"]
			TheActivity.save()

			TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
			TheSearcher.UpdateOneInfo(Information["id"], TheActivity.Name)
		except:
			Success = False
			Reason = "修改数据失败"
			Code = Constants.ERROR_CODE_UNKNOWN
	
	
	if Success:
		try:
			print(ChangeDictionary["rules"], Information["id"])
			if ChangeDictionary["rules"] != []:
				#修改高级报名规则
				if ChangeAdvancedRules(Information["id"], ChangeDictionary["rules"]) != True:
					Success = False
					Reason = "修改数据失败"
					Code = Constants.ERROR_CODE_UNKNOWN	
		except:
			Success = False
			Reason = "修改数据失败"
			Code = Constants.ERROR_CODE_UNKNOWN

	if Success == False:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	else:
		Return["result"] = "success"
	return Return

def ChangeAdvancedRules(TheActivityID, NewRules):
	'''
	描述：修改高级报名规则
	参数：活动id，新的高级报名规则
	返回：成功True失败False
	'''
	Success = True
	TheAcceptRule = []
	TheAuditRule = []
	TheRejectRule = []
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheRules = AdvancedRule.objects.filter(ActivityId = TheActivity)
			print(TheRules)
			for item in TheRules:
				print(item)
				item.delete()
		except:
			Success = False
	if Success:
		try:
			TheAcceptRule = NewRules["accept"]
		except:
			TheAcceptRule = []
		try:
			TheAuditRule = NewRules["needAudit"]
		except:
			TheAuditRule = []
		try:
			TheRejectRule = NewRules["reject"]
		except:
			TheRejectRule = []
	if Success:
		try:
			#添加rules
			for item in TheAcceptRule:
				AddAdvancedRules(TheActivityID, item, Constants.ADVANCED_RULE_ACCEPT)
			for item in TheAuditRule:
				AddAdvancedRules(TheActivityID, item, Constants.ADVANCED_RULE_AUDIT)
			for item in TheRejectRule:
				AddAdvancedRules(TheActivityID, item, Constants.ADVANCED_RULE_REJECT)
		except:
			Success = False
	return Success

def ChangeJoinInformation(TheUserID, TheActivityID, NewStatus, NewRole):
	'''
	描述：修改用户的状态和权限信息
	参数：openid，活动id,新状态，新角色
	返回：{result：success}/{result：fail，reason：xxx, code:xxx}
	状态的话，只能由小变大
	权限的话，创建者不能变别的，别的也不能变创建者
	'''
	Success = True
	Result = {}
	Reason = ""
	Code = Constants.UNDEFINED_NUMBER
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheJoinInformation = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
		except:
			Success = False
			Reason = "该用户未参加该活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			OldStatus = TheJoinInformation.Status
			OldRole = TheJoinInformation.Role
			if OldRole == Constants.USER_ROLE_CREATOR or NewRole == Constants.USER_ROLE_CREATOR:
				if OldRole != NewRole:
					Success = False
					Reason = "不能变更该活动的创建者！"
					Code = Constants.ERROR_CODE_INVALID_CHANGE
			if OldStatus > NewStatus:
				Success = False
				Reason = "用户状态的修改时间顺序不合法！"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
			TheJoinInformation.Role = NewRole
			TheJoinInformation.Status = NewStatus
			TheJoinInformation.save()
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

def ChangeUserStatus(TheSelfID, Information):
	'''
	描述：修改另一个用户的状态和权限信息
	参数：自己的openid，待修改信息字典（必定有对方id和活动id，可能有新状态和新角色）
	返回：{result：success}/{result：fail，reason：xxx, code:xxx}
	合理：只有自己是创建者和管理员才可以设置用户selfRole和selfStatus
	管理员只能设置非管理员也非创建者的用户的selfStatus
	---------只能把0改成1或5(报名审核),以及把1，2，3改成5(踢出活动)
	创建者可以设置除了自己外所有用户selfRole和selfStatus
	------设置selfStatus的方式和管理员一样，设置selfRole可以把管理员变成普通用户，也可以把普通用户(仅限状态为1，2，3的用户)变成管理员
	'''
	Success = True
	Return = {}
	Reason = ""
	Code = Constants.UNDEFINED_NUMBER
	if Success:
		try:
			TheSelf = User.objects.get(OpenID = TheSelfID)
			TheUser = User.objects.get(OpenID = Information["openId"])
			TheActivity = Activity.objects.get(ID = int(Information["activityId"]))
			SelfJoinInformation = JoinInformation.objects.get(UserId = TheSelf, ActivityId = TheActivity)
			TheJoinInformation = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
		except:
			Success = False
			Reason = "未找到相应的用户或活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			if SelfJoinInformation.Role <= TheJoinInformation.Role:
				Success = False
				Reason = "权限不足，创建者能修改除自己以外其他用户报名信息，管理员只能修改一般用户报名信息，一般用户无法修改他人报名信息！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
			OldStatus = TheJoinInformation.Status
			OldRole = TheJoinInformation.Role
			NewStatus = 0
			NewRole = 0
			if "newStatus" in Information:
				NewStatus = Information["newStatus"]
			else:
				NewStatus = OldStatus
			if "newRole" in Information:
				NewRole = Information["newRole"]
			else:
				NewRole = OldRole
			if OldStatus != NewStatus:
				if OldStatus == Constants.USER_STATUS_WAITVALIDATE:
					if NewStatus != Constants.USER_STATUS_JOINED and NewStatus != Constants.USER_STATUS_MISSED:
						Success = False
						Reason = "修改用户状态有误，只能进行报名审核通过，审核不通过，以及踢出活动操作"
						Code = Constants.ERROR_CODE_INVALID_CHANGE
				elif OldStatus == Constants.USER_STATUS_JOINED or OldStatus == Constants.USER_STATUS_NOTCHECKED\
				or OldStatus == Constants.USER_STATUS_CHECKED:
					if NewStatus != Constants.USER_STATUS_MISSED:
						Success = False
						Reason = "修改用户状态有误，只能进行报名审核通过，审核不通过，以及踢出活动操作"	
						Code = Constants.ERROR_CODE_INVALID_CHANGE
			if OldRole != NewRole:
				if SelfJoinInformation.Role != Constants.USER_ROLE_CREATOR:
					Success = False
					Reason = "只有创建者可以修改用户权限！"
					Code = Constants.ERROR_CODE_LACK_ACCESS
				if OldRole == Constants.USER_ROLE_CREATOR or NewRole == Constants.USER_ROLE_CREATOR:
					Success = False
					Reason = "不能变更该活动的创建者！"
					Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "请求参数不合法！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		try:
			TheResult = ChangeJoinInformation(TheUser.OpenID, TheActivity.ID, NewStatus, NewRole)
			if TheResult["result"] != "success":
				Success = False
				Reason = TheResult["reason"]
				Code = TheResult["code"]
		except:
			Success = False
			Reason = "请求参数不合法！"	
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return
				
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
			if DatabaseJudgeValid.JudgeWhetherManager(TheManagerID, TheActivityID) != True:
				Success = False
				Reason = "权限不足，需要是管理员或创建者！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheUser = User.objects.get(OpenID = TheUserID)
			if TheActivity.CanBeSearched != True:
				Success = False
				Reason = "未找到活动！"
				Code = Constants.ERROR_CODE_NOT_FOUND
		except:
			Success = False
			Reason = "未找到用户或活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
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
				TheJoinActivity.Status = Constants.USER_STATUS_MISSED
				TheJoinActivity.JoinReason = "无"
				TheJoinActivity.save()
				#todo:拒绝消息
			else:
				if TheActivity.MaxUser != Constants.UNDEFINED_NUMBER and TheActivity.CurrentUser >= TheActivity.MaxUser:
					Success = False
					Reason = "当前人数已满，不能审核通过！"
					Code = Constants.ERROR_CODE_INVALID_CHANGE
				else:
					CurrentTime = DataBaseGlobalFunctions.GetCurrentTime()
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

def GetUserActivityWords(TheUserID):
	'''
	描述：获取用户参与全部活动的文字
	参数: 用户id
	返回：
	成功：文字描述构成的数组 失败：空
	'''
	Success = True
	TheWordList = []
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheJoinActivityList = JoinInformation.objects.filter(UserId = TheUser)
		except:
			Success = False	
	if Success:
		try:
			for item in TheJoinActivityList:
				TheResult = {}
				TheResult = QueryActivity(TheUserID, item.ActivityId.ID)
				#print(TheResult)
				if "name" in TheResult:
					TheWordList.append(TheResult["name"])
		except:
			Success = False
	if Success:
		return TheWordList
	else:
		return []

def RemoveJoinedActivity(TheUserID, TheActivityList):
	'''
	描述：移除用户参与过的活动
	参数: 用户openid，活动列表
	返回：新的活动列表，失败返回空列表
	'''
	Success = True
	Return = {}
	NewActivityList = []
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
		except:
			Success = False	
	if Success:
		try:
			for item in TheActivityList["activityList"]:
				TheActivityID = int(item["id"])
				#print(TheUserID, TheActivityID)
				if DatabaseJudgeValid.JudgeUserJoinedActivity(TheUserID, TheActivityID) != True:
					NewActivityList.append(item)
		except:
			Success = False
	if Success:
		Return["activityList"] = NewActivityList
	else:
		Return = {}
	return Return

def RemoveSelfFromList(TheActivityID, TheActivityList):
	'''
	描述：移除活动本身
	参数: 活动id，活动列表
	返回：新的活动列表，失败返回空列表
	'''
	Success = True
	Return = {}
	NewActivityList = []
	if Success:
		try:
			for item in TheActivityList["activityList"]:
				NewActivityID = int(item["id"])
				#print(TheUserID, TheActivityID)
				if int(TheActivityID) != NewActivityID:
					NewActivityList.append(item)
		except:
			Success = False
	if Success:
		Return["activityList"] = NewActivityList
	else:
		Return = {}
	return Return

def RecommendActivityByActivity(TheUserID, TheActivityID):
	'''
	描述：根据活动推荐其他活动
	参数: 用户ID，活动id
	返回：
	第一个是一个字典，失败为空，成功格式同返回全部活动
	第二个是错误信息，成功空字典，否则有reason和code
	'''
	Result = {}
	ErrorInfo = {}
	ReturnInfo = {}
	BufReturnInfo = {}
	RawReturnInfo = {}
	Reason = ""
	Code = 0
	Success = True
	ResultList = []
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
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
			TheName = TheActivity.Name
			TheWordList = []
			TheWordList.append(TheName)
			TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
			RawReturnInfo = TheSearcher.Recommend(TheWordList)
			#print(RawReturnInfo)
			BufReturnInfo = RemoveJoinedActivity(TheUserID, RawReturnInfo)
			ReturnInfo = RemoveSelfFromList(TheActivityID, BufReturnInfo)
			if "activityList" not in ReturnInfo:
				Success = False
				Reason = "推荐活动失败！"
				Code = Constants.ERROR_CODE_UNKNOWN
			elif ReturnInfo["activityList"] == []:
				Success = False
				Reason = "未找到类似的活动，推荐活动失败！"
				Code = Constants.ERROR_CODE_NOT_FOUND
		except:
			Success = False
			Reason = "推荐活动失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Result = ReturnInfo
		ErrorInfo = {}
	else:
		Result = {}
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	return Result, ErrorInfo

def RecommendActivityByUser(TheUserID):
	'''
	描述：根据用户推荐其他活动
	参数: 用户id
	返回：
	第一个是一个字典，失败为空，成功格式同返回全部活动
	第二个是错误信息，成功空字典，否则有reason和code
	'''
	Result = {}
	ErrorInfo = {}
	RawReturnInfo = {}
	ReturnInfo = {}
	Reason = ""
	Code = 0
	Success = True
	ResultList = []
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
		except:
			Success = False
			Reason = "未找到用户！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	
	if Success:
		try:
			TheWordList = []
			TheWordList = GetUserActivityWords(TheUserID)
			TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
			RawReturnInfo = TheSearcher.Recommend(TheWordList)
			ReturnInfo = RemoveJoinedActivity(TheUserID, RawReturnInfo)
			if "activityList" not in ReturnInfo:
				Success = False
				Reason = "推荐活动失败！"
				Code = Constants.ERROR_CODE_UNKNOWN
			elif ReturnInfo["activityList"] == []:
				Success = False
				Reason = "未找到类似的活动，推荐活动失败！"
				Code = Constants.ERROR_CODE_NOT_FOUND
		except:
			Success = False
			Reason = "推荐活动失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Result = ReturnInfo
		ErrorInfo = {}
	else:
		Result = {}
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	return Result, ErrorInfo

