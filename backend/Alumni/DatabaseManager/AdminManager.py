'''
处理管理员请求的数据库函数
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
from django.contrib.auth.hashers import make_password, check_password
from DataBase.models import User
from DataBase.models import Education
from DataBase.models import Activity
from DataBase.models import JoinInformation
from DataBase.models import GlobalVariables
from DataBase.models import AdvancedRule
from DataBase.models import Department
from DataBase.models import EducationType
from DataBase.models import ActivityType
from DataBase.models import Picture
from DataBase.models import Admin
from DataBase.models import ReportInformation
from Alumni.LogicManager.Constants import Constants
from Alumni.LogicManager import GlobalFunctions
from Alumni.LogicManager import JudgeValid
from Alumni.DatabaseManager import ActivityManager

def JudgeWhetherAdminLogin(TheSession):
	'''
	描述：判断管理员是否登录
	参数：session
	返回：是true否false
	'''  
	Success = True
	if TheSession == "UNDEFINED":
		Success = False
	if Success:
		try:
			TheAdmin = Admin.objects.get(Session = TheSession)
		except:
			Success = False
	return Success

def AddAdmin(TheUsername, ThePassword):
	'''
	添加用户的后门函数
	'''
	try:
		TheAdmin = Admin.objects.get(Username = TheUsername)
		TheAdmin.Password = make_password(ThePassword)
		TheAdmin.save()
	except:
		Admin.objects.create(Username = TheUsername, Password = make_password(ThePassword))    

def Login(TheUsername, ThePassword):
	'''
	描述：管理员登录的数据库函数
	参数：用户名，密码
	返回：成功{result：success}
		 失败：{result：fail，reason：xxx，code：xxx}
		 成功还有session
	'''
	Success = True
	Reason = ""
	TheSession = ""
	Code = 0
	Return = {}
	print(TheUsername, ThePassword)
	if Success:
		try:
			TheAdmin = Admin.objects.get(Username = TheUsername)
		except:
			Success = False
			Reason = "帐号不存在！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	print(Success)
	if Success:
		try:
			if check_password(ThePassword, TheAdmin.Password) != True:
				Success = False
				Reason = "密码不正确！"  
				Code = Constants.ERROR_CODE_NOT_FOUND
		except:
			Success = False
			Reason = "帐号不存在！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			TheSession = GlobalFunctions.GenerateSessionID()
			TheAdmin.Session = TheSession
			TheAdmin.save()
		except:
			Success = False
			Reason = "登录失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
		Return["session"] = TheSession
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def Logout(TheSession):
	'''
	描述：管理员登出的数据库函数
	参数：session
	返回：成功{result：success}
		 失败：{result：fail，reason：xxx，code：xxx}
		 成功还有session
	'''
	Success = True
	Reason = ""
	Code = 0
	Return = {}
	if Success:
		try:
			TheAdmin = Admin.objects.get(Session = TheSession)
		except:
			Success = False
			Reason = "帐号不存在！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			TheAdmin.Session = "UNDEFINED"
			TheAdmin.save()
		except:
			Success = False
			Reason = "登出失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def ShowAllActivity(TheLastID, TheMostNumber):
	'''
	描述：查询所有活动
	参数: 最后一个id，最多显示的数目
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

def ChangeActivityStatus(TheInfo):
	'''
	描述：修改活动状态
	参数: 字典，存储待修改活动状态
	返回：第一个是一个字典，里面就一个字典数组activityList，字典每个字典有活动具体信息，失败为空
		 第二个是失败状态信息，成功是空，失败有reason和code	
	'''
	Success = True
	Reason = ""
	Code = 0
	TheActivityID = 0
	Return = {}
	if Success:
		try:
			TheActivityID = TheInfo["id"]
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Reason = "活动不存在！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			if "statusGlobal" in TheInfo:
				if JudgeValid.JudgeActivityStatusGlobalValid(TheInfo["statusGlobal"]) != True:
					Success = False
					Reason = "活动全局状态不合法！"
					Code = Constants.ERROR_CODE_INVALID_PARAMETER
				TheActivity.StatusGlobal = TheInfo["statusGlobal"]
			if "statusJoin" in TheInfo:
				if JudgeValid.JudgeActivityStatusJoinValid(TheInfo["statusJoin"]) != True:
					Success = False
					Reason = "活动加入状态不合法！"
					Code = Constants.ERROR_CODE_INVALID_PARAMETER
				TheActivity.StatusJoin = TheInfo["statusJoin"]
			if "statusCheck" in TheInfo:
				if JudgeValid.JudgeActivityStatusCheckValid(TheInfo["statusCheck"]) != True:
					Success = False
					Reason = "活动签到状态不合法！"
					Code = Constants.ERROR_CODE_INVALID_PARAMETER
				TheActivity.StatusCheck = TheInfo["statusCheck"]  
			TheActivity.save()
		except:
			Success = False
			Reason = "修改参数不合法！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return
		
def ShowOneActivity(TheActivityID):
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
		Result = ActivityManager.QueryActivity(TheActivityID)
		if Result == {}:
			Success = False
			Reason = "查询活动失败！"
			Code = Constants.ERROR_CODE_UNKNOWN

	if Success:
		try:
			TheJoinActivityList = JoinInformation.objects.filter(ActivityId = TheActivity)
			Result["participants"] = []
			NumberNeedAudit = 0
			for item in TheJoinActivityList:
				TheUserInfo = {}
				TheId = item.UserId.OpenID
				TheStatus = item.Status
				TheUserInfo["openId"] = TheId
				TheUserInfo["name"] = item.UserId.Name
				TheUserInfo["avatarUrl"] = GlobalFunctions.GetTrueAvatarUrlUser(item.UserId.AvatarURL)
				TheUserInfo["userStatus"] = TheStatus
				TheUserInfo["userRole"] = item.Role
				if JudgeValid.JudgeUserStatusJoined(TheStatus):
					Result["participants"].append(TheUserInfo)
				if item.Role == Constants.USER_ROLE_CREATOR:
					Result["creator"] = TheId
				if item.Status == Constants.USER_STATUS_WAITVALIDATE:
					NumberNeedAudit += 1
			Result["needAuditCount"] = NumberNeedAudit
		except:
			Success = False
			Reason = "查询活动失败！"
			Code = Constants.ERROR_CODE_UNKNOWN

	if Success:
		try:
			TheReportActivityList = ReportInformation.objects.filter(ActivityId = TheActivity)
			Result["reporters"] = []
			for item in TheReportActivityList:
				TheUserInfo = {}
				TheUserInfo["openId"] = item.UserId.OpenID
				TheUserInfo["name"] = item.UserId.Name
				TheUserInfo["avatarUrl"] = GlobalFunctions.GetTrueAvatarUrlUser(item.UserId.AvatarURL)
				Result["reporters"].append(TheUserInfo)
			Result["reportCount"] = len(Result["reporters"])
		except:
			Success = False
			Reason = "查询活动失败！"
			Code = Constants.ERROR_CODE_UNKNOWN

	if Success:
		try:	
			Result["rules"] = {}
			Result["rules"] = ActivityManager.ShowAllAdvancedRules(TheActivityID)
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

def ShowAllReports(TheLastSeenID, TheMostNumber):
	'''
	描述：查询所有举报信息
	参数: 最后一个id，最多显示的数目
	返回：第一个是一个字典，里面就一个字典数组reportList，字典每个字典有举报具体信息，失败为空
		 第二个是失败状态信息，成功是空，失败有reason和code	'''
	#查询
	Success = True
	if Success:
		try:
			Info = ReportInformation.objects.all()
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
				if TheLastSeenID != Constants.UNDEFINED_NUMBER:
					if item.ID >= TheLastSeenID:
						i -= 1
						continue
				TheResult = {}
				TheResult["id"] = item.ID
				TheResult["submitTime"] = GlobalFunctions.TimeStampToTimeString(int(item.SubmitTime))
				TheResult["submitMsg"] = item.Reason
				TheResult["name"] = item.UserId.Name
				TheResult["openId"] = item.UserId.OpenID
				TheResult["avatarUrl"] = GlobalFunctions.GetTrueAvatarUrlUser(item.UserId.AvatarURL)
				TheResult["activityName"] = item.ActivityId.Name
				TheResult["activityId"] = item.ActivityId.ID
				TheResult["imageUrl"] = GlobalFunctions.GetTrueAvatarUrlActivity(item.ActivityId.ImageURL)
				Result.append(TheResult)
				CurrentNumber = CurrentNumber + 1
				if TheMostNumber != Constants.UNDEFINED_NUMBER and CurrentNumber >= TheMostNumber:
					break
				i -= 1
		except:
			Success = False
	if Success == True:
		Return["reportList"] = Result
		ErrorInfo = {}
	else:
		Return = {}
		ErrorInfo["reason"] = "查询举报失败！"
		ErrorInfo["code"] = Constants.ERROR_CODE_UNKNOWN
	return Return, ErrorInfo

def ShowActivityReports(TheActivityID):
	'''
	描述：查询所有举报信息
	参数: 活动id
	返回：第一个是一个字典，里面就一个字典数组reportList，字典每个字典有举报具体信息，失败为空
		 第二个是失败状态信息，成功是空，失败有reason和code	'''
	#查询
	Success = True
	Reason = ""
	Code = Constants.UNDEFINED_NUMBER
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			Info = TheActivity.ReportList.all()
		except:
			Success = False
			Reason = "未找到该活动！"
			Code = Constants.ERROR_CODE_NOT_FOUND
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
				TheResult = {}
				TheResult["id"] = item.ID
				TheResult["submitTime"] = GlobalFunctions.TimeStampToTimeString(int(item.SubmitTime))
				TheResult["submitMsg"] = item.Reason
				TheResult["name"] = item.UserId.Name
				TheResult["openId"] = item.UserId.OpenID
				TheResult["avatarUrl"] = GlobalFunctions.GetTrueAvatarUrlUser(item.UserId.AvatarURL)
				Result.append(TheResult)
				i -= 1
		except:
			Success = False
			Reason = "查询举报失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success == True:
		Return["reportList"] = Result
		ErrorInfo = {}
	else:
		Return = {}
		ErrorInfo["reason"] = Reason
		ErrorInfo["code"] = Code
	return Return, ErrorInfo

def DeleteOneReport(TheReportID):
	'''
	描述：删除单一举报信息
	参数: 举报id
	返回：成功 success，失败 fail+code+reason
	'''
	Success = True
	Reason = ""
	Code = 0
	Return = {}
	if Success:
		try:
			TheReport = ReportInformation.objects.get(ID = TheReportID)
			TheReport.delete()
		except:
			Success = False
			Reason = "未找到此举报信息！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def DeleteActivityReport(TheActivityID):
	'''
	描述：删除单一活动的所有举报信息
	参数: 活动id
	返回：成功 success，失败 fail+code+reason
	'''
	Success = True
	Reason = ""
	Code = 0
	Return = {}
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheReportList = TheActivity.ReportList.all()
		except:
			Success = False
			Reason = "未找到此活动信息！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			for item in TheReportList:
				item.delete()
		except:
			Success = False
			Reason = "删除举报信息失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def ShowAllUsers(TheLastSeenID, TheMostNumber):
	'''
	描述：查询所有用户
	参数: 最后一个id，最多显示的数目
	返回：第一个是一个字典，里面就一个字典数组userList，字典每个字典有用户具体信息，失败为空
		 第二个是失败状态信息，成功是空，失败有reason和code	
	'''
	#查询
	Success = True
	if Success:
		try:
			Info =	User.objects.all()
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
				if TheLastSeenID != Constants.UNDEFINED_NUMBER:
					if item.ID >= TheLastSeenID:
						i -= 1
						continue
				TheResult = {}
				TheResult["id"] = item.ID
				TheResult["name"] = item.Name
				TheResult["openId"] = item.OpenID
				TheResult["avatarUrl"] = GlobalFunctions.GetTrueAvatarUrlUser(item.AvatarURL)
				TheResult["status"] = item.Status
				Result.append(TheResult)
				CurrentNumber = CurrentNumber + 1
				if TheMostNumber != Constants.UNDEFINED_NUMBER and CurrentNumber >= TheMostNumber:
					break
				i -= 1
		except:
			Success = False
	if Success == True:
		Return["userList"] = Result
		ErrorInfo = {}
	else:
		Return = {}
		ErrorInfo["reason"] = "查询用户失败！"
		ErrorInfo["code"] = Constants.ERROR_CODE_UNKNOWN
	return Return, ErrorInfo

def ChangeUser(TheOpenID, TheStatus):
	'''
	描述：修改用户状态（封禁，解封）
	参数: 用户id，状态
	返回：成功 success，失败 fail+code+reason
	'''
	Success = True
	Reason = ""
	Code = 0
	Return = {}
	if Success:
		try:
			TheUser = User.objects.get(OpenID = TheOpenID)
		except:
			Success = False
			Reason = "未找到此用户！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			if TheStatus == 1:
				TheUser.Status = True
			elif TheStatus == 0:
				TheUser.Status = False
			else:
				Success = False
				Reason = "参数不合法！"
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
			TheUser.save()
		except:
			Success = False
			Reason = "修改用户信息失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return