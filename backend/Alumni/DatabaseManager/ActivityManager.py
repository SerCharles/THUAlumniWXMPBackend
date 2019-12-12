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
from Alumni.LogicManager.Constants import Constants
from Alumni.LogicManager import GlobalFunctions
from Alumni.LogicManager import JudgeValid
from Alumni.DatabaseManager import SearchAndRecommend


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
	#把时间转化为时间戳,并且判断时间和人数是否合法
	if Success:
		try:
			CurTime = GlobalFunctions.GetCurrentTime()
			StartTime = GlobalFunctions.TimeStringToTimeStamp(Information["start"])
			EndTime = GlobalFunctions.TimeStringToTimeStamp(Information["end"])
			if 'signupBeginAt' in Information:
				StartSignTime = GlobalFunctions.TimeStringToTimeStamp(Information["signupBeginAt"])
			else:
				StartSignTime = CurTime
			if 'signupStopAt' in Information:
				StopSignTime = GlobalFunctions.TimeStringToTimeStamp(Information["signupStopAt"])
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
			JudgeResult = JudgeValid.JudgeParameterValid(CurTime, StartTime, EndTime, StartSignTime, StopSignTime, 1, TheMinUser, TheMaxUser)
			if "imageUrl" in Information:
				TheImageURL = Information["imageUrl"]
			else:
				TheImageURL = "UNDEFINED"		
			if JudgeResult["result"] != "success":
				Success = False
				Reason = JudgeResult["reason"]
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "输入的开始/结束/开始报名/报名截止时间不合理!"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	

	#判断活动状态，类型等是否合法
	if Success:
		try:
			TheStatusGlobal = int(Information["statusGlobal"])
			TheStatusJoin = int(Information["statusJoin"])
			TheStatusCheck = int(Information["statusCheck"])

			TheSearched = bool(Information["canBeSearched"])
			if TheStatusGlobal != Constants.ACTIVITY_STATUS_GLOBAL_NORMAL:
				Success = False
				Reason = "活动状态必须是正常状态！" 
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "参数不合法，添加活动失败!"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		try:
			TheType = Information["type"]
			if JudgeValid.JudgeActivityTypeValid(TheType) == False:
				Success = False
				Reason = "活动类型不合法，添加活动失败!"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER			
		except:
			Success = False
			Reason = "参数不合法，添加活动失败!"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER


	#获得标签,正文,头像
	if Success:
		try:
			TheTagsList = Information["tags"]
			TheDescription = Information["description"]
			if JudgeValid.JudgeTagListValid(TheTagsList) != True:
				Success = False
				Reason = "参数不合法，标签不能带有英文逗号！"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
			TheTags = GlobalFunctions.MergeTags(TheTagsList)		
		except:
			Success = False
			Reason = "参数不合法，添加活动失败!"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER

	#获得高级报名信息
	if Success:
		try:
		#判断是否合法
			TheGlobalRule = Information["rules"]["ruleType"]
			TheJudgeAdvanceRuleResult = JudgeValid.JudgeAdvancedRuleValid(Information["rules"])
			#print(TheJudgeAdvanceRuleResult)
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

	#print(CurTime, StartTime, EndTime, StartSignTime, StopSignTime)
	#print(Success)
	#插入数据库
	if Success:
		try:
			TheName = Information["name"]
			ThePlace = Information["place"]

			#TheCreator = User.objects.get(OpenID = ID) 
			#print(TheCreator.ID)
			TheCreateTime = GlobalFunctions.GetCurrentTime()
			NewActivity = Activity.objects.create(Name = TheName, Place = ThePlace, CreateTime = TheCreateTime, StartTime = StartTime, EndTime = EndTime, SignUpStartTime = StartSignTime,\
			SignUpEndTime = StopSignTime, MinUser = TheMinUser, MaxUser = TheMaxUser, CurrentUser = 0, Type = TheType, \
			StatusGlobal = TheStatusGlobal, StatusJoin = TheStatusJoin, StatusCheck = TheStatusCheck, CanBeSearched = TheSearched, \
			GlobalRule = TheGlobalRule, Tags = TheTags, Description = TheDescription, ImageURL = TheImageURL)
			NewActivity.save()
			ActivityID = NewActivity.ID

			TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
			TheSearcher.AddOneInfo(ActivityID, TheName + ',' + TheTags)
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
			JoinActivityResult = AddCreatorIntoActivity(ID, ActivityID)
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

def AddCreatorIntoActivity(CreatorID, TheActivityID):
	'''
	描述：将创建者加入活动
	参数：创建者id，活动id
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
			TheUser = User.objects.get(OpenID = CreatorID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Reason = "未找到创建者或活动"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			TheSubmitTime = GlobalFunctions.GetCurrentTime()
			TheJoinTime = GlobalFunctions.GetCurrentTime()
			TheCheckTime = GlobalFunctions.GetCurrentTime()
			TheJoinReason = "无"
			TheStatus = Constants.USER_STATUS_CHECKED
			TheRole = Constants.USER_ROLE_CREATOR
			try:
				TheJoinInformation = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
				TheJoinInformation.delete()
			except:
				donothing = 0
			TheJoinInformation = JoinInformation.objects.create(UserId = TheUser, ActivityId = TheActivity, Status = TheStatus,\
			Role = TheRole, SubmitTime = TheSubmitTime, JoinTime = TheJoinTime, CheckTime = TheCheckTime, JoinReason = TheJoinReason)
			TheJoinInformation.save()
			TheActivity.CurrentUser = TheActivity.CurrentUser + 1
			TheActivity.save()
		except:
			Success = False
			Reason = "将创建者加入活动失败"
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
			#print(1)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			#print(TheActivity)
			AdvancedRule.objects.create(ActivityId = TheActivity, MinStartYear = TheMinStartYear, MaxStartYear = TheMaxStartYear\
			, Department = TheDepartment, EducationType = TheEducationType, Type = TheType)
		except:
			Success = False
	return Success

def QueryActivity(TheActivityID):
	'''
	描述：给定活动id，查询活动基本信息
	参数：活动id
	返回：一个字典，里面有活动各种信息
	如果没有就返回空字典
	'''
	Success = True
	Result = {}
	if Success:
		try:
			Info = Activity.objects.get(ID = TheActivityID)
			Result["name"] = Info.Name
			Result["place"] = Info.Place
			Result["createTime"] = GlobalFunctions.TimeStampToTimeString(int(Info.CreateTime))
			Result["start"] = GlobalFunctions.TimeStampToTimeString(int(Info.StartTime))
			Result["end"] = GlobalFunctions.TimeStampToTimeString(int(Info.EndTime))
			Result["signupBeginAt"] = GlobalFunctions.TimeStampToTimeString(int(Info.SignUpStartTime))
			Result["signupStopAt"] = GlobalFunctions.TimeStampToTimeString(int(Info.SignUpEndTime))
			Result["minUser"] = int(Info.MinUser)
			Result["maxUser"] = int(Info.MaxUser)
			Result["curUser"] = int(Info.CurrentUser)
			Result["type"] = Info.Type
			Result["statusGlobal"] = int(Info.StatusGlobal)
			Result["statusJoin"] = int(Info.StatusJoin)
			Result["statusCheck"] = int(Info.StatusCheck)
			Result["tags"] = GlobalFunctions.SplitTags(Info.Tags)
			Result["imageUrl"] = GlobalFunctions.GetTrueAvatarUrlActivity(Info.ImageURL)
		except:
			Success = False
	if Success == False:
		Result = {}
	return Result

def ShowAllAdvancedRules(TheActivityID):
	'''
	描述：给定活动id，查询活动高级报名信息
	参数：活动id
	返回：一个字典，里面有高级报名信息的三个数组
	如果没有就返回空字典
	'''
	Success = True
	Result = {}
	AcceptRules = []
	AuditRules = []
	RejectRules = []
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			#print(len(TheActivity.AdvancedRule.all()))
			for item in TheActivity.AdvancedRule.all():
				#print(1)
				TheInfo = {}
				if item.MinStartYear != Constants.UNDEFINED_NUMBER:
					TheInfo["minEnrollmentYear"] = item.MinStartYear
				if item.MaxStartYear != Constants.UNDEFINED_NUMBER:
					TheInfo["maxEnrollmentYear"] = item.MaxStartYear
				if item.Department != "UNDEFINED":
					TheInfo["department"] = item.Department
				if item.EducationType != "UNDEFINED":
					TheInfo["enrollmentType"] = item.EducationType
				if item.Type == Constants.ADVANCED_RULE_ACCEPT:
					AcceptRules.append(TheInfo)
				elif item.Type == Constants.ADVANCED_RULE_AUDIT:
					AuditRules.append(TheInfo)
				elif item.Type == Constants.ADVANCED_RULE_REJECT:
					RejectRules.append(TheInfo)
			if AcceptRules != []:
				Result["accept"] = AcceptRules
			if AuditRules != []:
				Result["needAudit"] = AuditRules
			if RejectRules != []:
				Result["reject"] = RejectRules
		except:
			Success = False
	if Success:
		return Result
	else:
		return {}

def ShowOneActivity(TheUserID, TheActivityID):
	'''
	描述：给定活动id，查询活动具体信息
	参数：用户id和活动id
	返回：一个字典，里面有活动各种信息，错误信息
	成功：错误信息空
	失败：返回字典空，错误信息存在
	'''
	Success = True
	Result = {}
	ErrorInfo = {}
	Reason = ""
	Code = 0
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Reason = "未找到该活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND

	if Success:
		Result = QueryActivity(TheActivityID)
		if Result == {}:
			Success = False
			Reason = "查询活动失败！"
			Code = Constants.ERROR_CODE_UNKNOWN

	if Success:
		try:
			Result["canBeSearched"] = TheActivity.CanBeSearched
			TheJoinActivityList = JoinInformation.objects.filter(ActivityId = TheActivity)
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
				if JudgeValid.JudgeUserStatusJoined(TheStatus):
					Result["participants"].append(TheUserInfo)
				if item.Role == Constants.USER_ROLE_CREATOR:
					Result["creator"] = TheId
			if JudgeValid.JudgeWhetherManager(TheUserID, TheActivityID) == True:
				Result["needAuditCount"] = NumberNeedAudit
		except:
			Success = False
			Reason = "查询活动失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		try:	
			Result["rules"] = {}
			Result["rules"] = ShowAllAdvancedRules(TheActivityID)
			Result["rules"]["ruleType"] = TheActivity.GlobalRule
		except:
			Success = False
			Reason = "查询活动失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		return Result, {}
	else:
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
		return {}, ErrorInfo

def ShowAllActivity(TheLastID, TheMostNumber):
	'''
	描述：查询所有活动
	参数: 最后一个id，最后显示的数目
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
	#print(TheLastID, TheMostNumber)
	if Success:
		try:
			CurrentNumber = 0
			i = len(Info) - 1
			while i >= 0:
				item = Info[i]
				if TheLastID != Constants.UNDEFINED_NUMBER:
					if item.ID >= TheLastID:
						i -= 1
						continue
				TheResult = {}
				TheResult["id"] = item.ID
				TheResult["name"] = item.Name
				TheResult["place"] = item.Place
				TheResult["createTime"] = GlobalFunctions.TimeStampToTimeString(int(item.CreateTime))
				TheResult["start"] = GlobalFunctions.TimeStampToTimeString(int(item.StartTime))
				TheResult["end"] = GlobalFunctions.TimeStampToTimeString(int(item.EndTime))
				TheResult["signupBeginAt"] = GlobalFunctions.TimeStampToTimeString(int(item.SignUpStartTime))
				TheResult["signupStopAt"] = GlobalFunctions.TimeStampToTimeString(int(item.SignUpEndTime))
				TheResult["minUser"] = int(item.MinUser)
				TheResult["maxUser"] = int(item.MaxUser)
				TheResult["curUser"] = int(item.CurrentUser)
				TheResult["type"] = item.Type
				TheResult["statusGlobal"] = int(item.StatusGlobal)
				TheResult["statusJoin"] = int(item.StatusJoin)
				TheResult["statusCheck"] = int(item.StatusCheck)
				TheResult["tags"] = GlobalFunctions.SplitTags(item.Tags)
				TheResult["imageUrl"] = GlobalFunctions.GetTrueAvatarUrlActivity(item.ImageURL)

				if JudgeValid.JudgeActivityCanBeSearched(item.ID):
					Result.append(TheResult)
					CurrentNumber = CurrentNumber + 1
					if TheMostNumber != Constants.UNDEFINED_NUMBER and CurrentNumber >= TheMostNumber:
						break
				i -= 1
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

def ShowActivityDetail(TheActivityID):
	'''
	描述：查询活动详情
	参数：用户openid，活动id，待修改信息
	返回：{result：success, description: xxx}/{result：fail，reason：xxx, code:xxx}
	'''
	Success = True
	Return = {}
	Reason = ""
	TheDescription = ""
	Code = Constants.UNDEFINED_NUMBER
	#判断是否能找到这个活动
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Reason = "未找到活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			TheDescription = TheActivity.Description
		except:
			Success = False
			Reason = "未找到活动详情！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success == False:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	else:
		Return["result"] = "success"
		Return["description"] = TheDescription
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
			if JudgeValid.JudgeWhetherCreator(TheUserID, TheActivityID) != True:
				Success = False
				Reason = "没有权限,只有管理员才能删除活动！！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
		except:
			Success = False
			Code = Constants.ERROR_CODE_NOT_FOUND
			Reason = "未找到该活动！"
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
		if TheActivity.StatusCheck != Constants.ACTIVITY_STATUS_CHECK_BEFORE:
			Success = False
			Reason = "签到已经开始，不能删除活动！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	if Success:
		TheActivity.StatusGlobal = Constants.ACTIVITY_STATUS_GLOBAL_EXCEPT
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
	Return = {}
	Reason = ""
	Code = Constants.UNDEFINED_NUMBER
	ChangeDictionary = {}
	#判断是否能找到这个活动
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = Information["id"])
			if JudgeValid.JudgeWhetherManager(TheUserID, Information["id"]) != True:
				Success = False
				Reason = "没有修改权限，需要是管理员或者创建者！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
		except:
			Success = False
			Reason = "没有修改权限"
			Code = Constants.ERROR_CODE_LACK_ACCESS
	if Success:
		if JudgeValid.JudgeActivityNormal(Information["id"]) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	#读取修改数据
	WhetherJudgeTime = False
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
				WhetherJudgeTime = True
				ChangeDictionary["start"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["start"]))
			else:
				ChangeDictionary["start"] = TheActivity.StartTime
			if "end" in Information:
				WhetherJudgeTime = True
				ChangeDictionary["end"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["end"]))
			else:
				ChangeDictionary["end"] = TheActivity.EndTime
			if "signupBeginAt" in Information:
				WhetherJudgeTime = True
				ChangeDictionary["signupBeginAt"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["signupBeginAt"]))
			else:
				ChangeDictionary["signupBeginAt"] = TheActivity.SignUpStartTime	
			if "signupStopAt" in Information:
				WhetherJudgeTime = True
				ChangeDictionary["signupStopAt"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["signupStopAt"]))
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
			if "statusGlobal" in Information:
				ChangeDictionary["statusGlobal"] = Information["statusGlobal"]
			else:
				ChangeDictionary["statusGlobal"] = TheActivity.StatusGlobal	
			if "statusJoin" in Information:
				ChangeDictionary["statusJoin"] = Information["statusJoin"]
			else:
				ChangeDictionary["statusJoin"] = TheActivity.StatusJoin		
			if "statusCheck" in Information:
				ChangeDictionary["statusCheck"] = Information["statusCheck"]
			else:
				ChangeDictionary["statusCheck"] = TheActivity.StatusCheck				
			if "canBeSearched" in Information:
				ChangeDictionary["canBeSearched"] = bool(Information["canBeSearched"])
			else:
				ChangeDictionary["canBeSearched"] = TheActivity.CanBeSearched
			if "imageUrl" in Information:
				ChangeDictionary["imageUrl"] = Information["imageUrl"]
			else:
				ChangeDictionary["imageUrl"] = TheActivity.ImageURL

			if "tags" in Information:
				if JudgeValid.JudgeTagListValid(Information["tags"]) != True:
					Success = False
					Reason = "参数不合法，标签不能带有英文逗号！"
					Code = Constants.ERROR_CODE_INVALID_PARAMETER
				ChangeDictionary["tags"] = GlobalFunctions.MergeTags(Information["tags"])
			else:
				ChangeDictionary["tags"] = TheActivity.Tags
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
			ChangeDictionary["curTime"] = GlobalFunctions.GetCurrentTime()
			ChangeDictionary["curUser"] = TheActivity.CurrentUser

		except:
			Success = False
			Reason = "待修改数据格式不合法"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#print(Success)
	#判断活动type修改后是否有效
	if Success:
		try:
			if JudgeValid.JudgeActivityTypeValid(ChangeDictionary["type"]) != True:
				Success = False
				Reason = "活动类型不合法"			
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
		except:
			Success = False
			Reason = "待修改数据格式不合法"			
			Code = Constants.ERROR_CODE_INVALID_PARAMETER				
	#判断时间，人数等修改后是否有效
	if Success and WhetherJudgeTime:
		try:
			JudgeResult = JudgeValid.JudgeParameterValid(ChangeDictionary["curTime"], ChangeDictionary["start"], ChangeDictionary["end"], \
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
			JudgeResult = JudgeValid.JudgeActivityStatusChangeValid(TheActivity.StatusGlobal, ChangeDictionary["statusGlobal"])
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
				JudgeResult = JudgeValid.JudgeAdvancedRuleValid(ChangeDictionary["rules"])
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
			TheActivity.StatusGlobal = ChangeDictionary["statusGlobal"]
			TheActivity.StatusJoin = ChangeDictionary["statusJoin"]
			TheActivity.StatusCheck = ChangeDictionary["statusCheck"]
			TheActivity.CanBeSearched = ChangeDictionary["canBeSearched"]
			TheActivity.GlobalRule = ChangeDictionary["ruleType"]
			TheActivity.Tags = ChangeDictionary["tags"]
			TheActivity.ImageURL = ChangeDictionary["imageUrl"]
			TheActivity.save()

			TheSearcher = SearchAndRecommend.WhooshSearcher.Create()
			TheSearcher.UpdateOneInfo(Information["id"], TheActivity.Name + ',' + TheActivity.Tags)
		except:
			Success = False
			Reason = "修改数据失败"
			Code = Constants.ERROR_CODE_UNKNOWN
	
	if Success:
		try:
			#print(ChangeDictionary["rules"], Information["id"])
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

def ChangeActivityDetail(TheUserID, TheActivityID, Information):
	'''
	描述：修改活动详情
	参数：用户openid，活动id，待修改信息
	返回：{result：success}/{result：fail，reason：xxx, code:xxx}
	'''
	Success = True
	Return = {}
	Reason = ""
	Code = Constants.UNDEFINED_NUMBER
	#判断是否能找到这个活动
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			if JudgeValid.JudgeWhetherManager(TheUserID, TheActivityID) != True:
				Success = False
				Reason = "没有修改权限，需要是管理员或者创建者！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
		except:
			Success = False
			Reason = "没有修改权限"
			Code = Constants.ERROR_CODE_LACK_ACCESS
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	if Success:
		try:
			TheDescription = Information["description"]
			TheActivity.Description = TheDescription
			TheActivity.save()
		except:
			Success = False
			Reason = "参数不合法，修改失败！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
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
			#print(TheRules)
			for item in TheRules:
				#print(item)
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

def AdvancedSearch(TheUserID, Information, TheLastSeenID, TheMost):
	'''
	描述：高级检索
	参数：用户openid，检索信息,上一个id，最多
	返回：Result, errorinfo
	'''
	Success = True
	Return = {}
	ErrorInfo = {}
	Reason = ""
	Code = Constants.UNDEFINED_NUMBER
	SearchDictionary = {}
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
		except:
			Success = False
			Reason = "用户不存在！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#读取修改数据
	if Success:
		try:
			if "place" in Information:
				SearchDictionary["place"] = Information["place"]
			else:
				SearchDictionary["place"] = ""
			if "startMin" in Information:
				SearchDictionary["startMin"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["startMin"]))
			else:
				SearchDictionary["startMin"] = 0
			if "startMax" in Information:
				SearchDictionary["startMax"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["startMax"]))
			else:
				SearchDictionary["startMax"] = Constants.MAX_NUMBER
			if "endMin" in Information:
				SearchDictionary["endMin"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["endMin"]))
			else:
				SearchDictionary["endMin"] = 0
			if "endMax" in Information:
				SearchDictionary["endMax"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["endMax"]))
			else:
				SearchDictionary["endMax"] = Constants.MAX_NUMBER
			if "signupBeginAtMin" in Information:
				SearchDictionary["signupBeginAtMin"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["signupBeginAtMin"]))
			else:
				SearchDictionary["signupBeginAtMin"] = 0
			if "signupBeginAtMax" in Information:
				SearchDictionary["signupBeginAtMax"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["signupBeginAtMax"]))
			else:
				SearchDictionary["signupBeginAtMax"] = Constants.MAX_NUMBER
			if "signupStopAtMin" in Information:
				SearchDictionary["signupStopAtMin"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["signupStopAtMin"]))
			else:
				SearchDictionary["signupStopAtMin"] = 0
			if "signupStopAtMax" in Information:
				SearchDictionary["signupStopAtMax"] = int(GlobalFunctions.TimeStringToTimeStamp(Information["signupStopAtMax"]))
			else:
				SearchDictionary["signupStopAtMax"] = Constants.MAX_NUMBER		
			if "type" in Information:
				SearchDictionary["type"] = Information["type"]
			else:
				SearchDictionary["type"] = ""	
			if "statusGlobal" in Information:
				SearchDictionary["statusGlobal"] = Information["statusGlobal"]
			else:
				SearchDictionary["statusGlobal"] = Constants.UNDEFINED_NUMBER	
			if "statusJoin" in Information:
				SearchDictionary["statusJoin"] = Information["statusJoin"]
			else:
				SearchDictionary["statusJoin"] = Constants.UNDEFINED_NUMBER		
			if "statusCheck" in Information:
				SearchDictionary["statusCheck"] = Information["statusCheck"]
			else:
				SearchDictionary["statusCheck"] = Constants.UNDEFINED_NUMBER				
			if "selfStatus" in Information:
				SearchDictionary["selfStatus"] = Information["selfStatus"]
			else:
				SearchDictionary["selfStatus"] = Constants.UNDEFINED_NUMBER - 1
			if "ruleForMe" in Information:
				SearchDictionary["ruleForMe"] = Information["ruleForMe"]
			else:
				SearchDictionary["ruleForMe"] = Constants.UNDEFINED_NUMBER - 1
		except:
			Success = False
			Reason = "高级检索格式不合法"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		try:
			JudgeResult = {}
			JudgeResult = JudgeValid.JudgeSearchStatusValid(SearchDictionary["statusGlobal"], SearchDictionary["statusJoin"], \
			SearchDictionary["statusCheck"], SearchDictionary["selfStatus"], SearchDictionary["ruleForMe"])
			if JudgeResult["result"] != "success":
				Success = False
				Reason = JudgeResult["reason"]
				Code = JudgeResult["code"]
			JudgeResult = JudgeValid.JudgeSearchTimeValid(SearchDictionary["startMin"], SearchDictionary["startMax"])
			if JudgeResult["result"] != "success":
				Success = False
				Reason = "最小开始时间必须小于等于最大开始时间！"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
			JudgeResult = JudgeValid.JudgeSearchTimeValid(SearchDictionary["endMin"], SearchDictionary["endMax"])
			if JudgeResult["result"] != "success":
				Success = False
				Reason = "最小结束时间必须小于等于最大结束时间！"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
			JudgeResult = JudgeValid.JudgeSearchTimeValid(SearchDictionary["signupBeginAtMin"], SearchDictionary["signupBeginAtMax"])
			if JudgeResult["result"] != "success":
				Success = False
				Reason = "最小开始报名时间必须小于等于最大开始报名时间！"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
			JudgeResult = JudgeValid.JudgeSearchTimeValid(SearchDictionary["signupStopAtMin"], SearchDictionary["signupStopAtMax"])
			if JudgeResult["result"] != "success":
				Success = False
				Reason = "最小结束报名时间必须小于等于最大结束报名时间！"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
		except:
			Success = False
			Reason = "高级检索格式不合法"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	SearchResult = []
	#查询时间，地点，状态，直接数据库函数
	if Success:
		try:
			QuerySet = Activity.objects.all() 
			Conditions = {'StartTime__gte': SearchDictionary["startMin"], 'StartTime__lte': SearchDictionary["startMax"],\
			'EndTime__gte': SearchDictionary["endMin"], 'EndTime__lte': SearchDictionary["endMax"],\
			'SignUpStartTime__gte': SearchDictionary["signupBeginAtMin"], 'SignUpStartTime__lte': SearchDictionary["signupBeginAtMax"],\
			'SignUpEndTime__gte': SearchDictionary["signupStopAtMin"], 'SignUpEndTime__lte': SearchDictionary["signupStopAtMax"]}
			if SearchDictionary["statusGlobal"] != Constants.UNDEFINED_NUMBER:
				Conditions['StatusGlobal'] = SearchDictionary["statusGlobal"]
			if SearchDictionary["statusJoin"] != Constants.UNDEFINED_NUMBER:
				Conditions['StatusJoin'] = SearchDictionary["statusJoin"]
			if SearchDictionary["statusCheck"] != Constants.UNDEFINED_NUMBER:
				Conditions['StatusCheck'] = SearchDictionary["statusCheck"]
			if SearchDictionary["place"] != '':
				Conditions["Place__icontains"] = SearchDictionary["place"]
			SearchResult = QuerySet.filter(**Conditions)
		except:
			Success = False
			Reason = "高级检索失败"
			Code = Constants.ERROR_CODE_UNKNOWN

	#查询活动类型，加入后结果等
	NewSearchResult = []
	if Success:
		try:
			i = len(SearchResult) - 1
			while i >= 0:
				item = SearchResult[i]
				WhetherMatch = True
				if SearchDictionary["type"] != "":
					if JudgeValid.JudgeActivityTypeMatch(SearchDictionary["type"], item.Type) != True:
						WhetherMatch = False
				if SearchDictionary["selfStatus"] != Constants.UNDEFINED_NUMBER - 1:
					TheStatus = JudgeValid.GetSelfStatus(TheUserID, item.ID)
					if TheStatus != SearchDictionary["selfStatus"]:
						WhetherMatch = False
				if SearchDictionary["ruleForMe"] != Constants.UNDEFINED_NUMBER - 1:
					TheRule = JudgeValid.GetSelfJoinStatus(TheUserID, item.ID)
					if TheRule != SearchDictionary["ruleForMe"]:
						WhetherMatch = False
				if JudgeValid.JudgeActivityCanBeSearched(item.ID) != True:
					WhetherMatch = False
				if WhetherMatch == True:
					print(item.ID)
					TheInfo = QueryActivity(item.ID)
					TheInfo["id"] = item.ID
					NewSearchResult.append(TheInfo)
				i -= 1
		except:
			Success = False
			Reason = "高级检索失败"
			Code = Constants.ERROR_CODE_UNKNOWN

	ReturnList = []
	#分页显示
	if Success:
		CurrentNum = 0
		WhetherFindStart = False
		if TheLastSeenID == Constants.UNDEFINED_NUMBER:
			WhetherFindStart = True
		for item in NewSearchResult:
			if WhetherFindStart == True:
				if TheMost != Constants.UNDEFINED_NUMBER and CurrentNum >= TheMost:
					break
				ReturnList.append(item)
				CurrentNum += 1 
			if TheLastSeenID != Constants.UNDEFINED_NUMBER and item["id"] == TheLastSeenID:
				WhetherFindStart = True
				

	#print(NewSearchResult)
	if Success == False:
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	else:
		Return["activityList"] = ReturnList
		ErrorInfo = {}
	return Return, ErrorInfo

def UploadActivityQRCode(TheUserID, TheActivityID):
	'''
	描述：上传活动二维码
	参数：用户openid，活动id
	返回：结果，图片文件名（失败是None）
	'''
	Success = True
	Result = {}
	Reason = ""
	TheImageName = ""
	Code = Constants.UNDEFINED_NUMBER
	print(TheUserID, TheActivityID)
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			if JudgeValid.JudgeWhetherManager(TheUserID, TheActivityID) != True:
				Success = False
				Reason = "没有权限,只有管理员才能设置活动二维码！！"
				Code = Constants.ERROR_CODE_LACK_ACCESS
		except:
			Success = False
			Code = Constants.ERROR_CODE_NOT_FOUND
			Reason = "未找到该活动！"
	print(Success)
	if Success:
		if JudgeValid.JudgeActivityNormal(TheActivityID) != True: 
			Success = False
			Reason = "活动状态为异常或结束，不能操作！"
			Code = Constants.ERROR_CODE_INVALID_CHANGE
	if Success:
		TheNewCode = GlobalFunctions.GenerateActivityCode()
		TheActivity.Code = TheNewCode
		TheActivity.save()
		TheImageName = GlobalFunctions.GenerateQRCode(TheActivityID, TheNewCode)
	if Success == True:
		Result["result"] = "success"
	else:
		Result["result"] = "fail"
		Result["reason"] = Reason 
		Result["code"] = Code
		TheImageName = None
	return Result, TheImageName



