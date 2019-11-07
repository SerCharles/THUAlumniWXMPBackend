'''
处理数据库操作的函数集合

1：用户列表：存储用户除了教育信息外的信息
2：教育信息表：存储教育信息
3：历史记录表：存储历史记录
4：活动列表：存储活动信息
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
from django.db import models
from DataBase.models import User
from DataBase.models import Education
from DataBase.models import Activity
from DataBase.models import JoinInformation
from Alumni.constants import Constants


def TimeStringToTimeStamp(TimeString):
	'''
	描述：时间字符串转化为时间戳（秒）
	参数：时间字符串
	返回：时间戳（秒）（int）
	'''
	TimeArray = time.strptime(TimeString, "%Y-%m-%d %H:%M:%S")
	TimeStamp = int(time.mktime(TimeArray))
	return TimeStamp

def TimeStampToTimeString(TimeStamp):
	'''
	描述：时间戳（秒）转化为时间字符串
	参数：时间戳（秒）（int）
	返回：时间字符串
	'''
	TimeArray = time.localtime(TimeStamp) 
	TimeString = time.strftime("%Y-%m-%d %H:%M:%S", TimeArray)
	return TimeString

def GetCurrentTime():
	'''
	功能：获取当前时间戳
	参数：无
	返回：int类型，时间戳（秒）
    '''
	CurTime = int(time.time())
	return CurTime

def AddUser(ID, Name, Education):
	'''
	描述：添加一个用户的信息到数据库(OpenID已存在)	
	参数：用户OpenID，用户名，教育信息（字典数组）
	返回：成功{result：success}，失败{result：fail，reason：xxx, code:xxx}
	''' 
	Return = {}
	Code = Constants.UNDEFINED_NUMBER
	Success = True
	Reason = ""
	#把教育信息以外的东西插入数据库
	if Success:
		try:
			NewUser = User.objects.get(OpenID = ID)
			NewUser.Name = Name
			NewUser.save()
		except:
			Success = False
			Reason = "该用户的OpenID不存在！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	#print(Success)
	#把教育信息插入数据库
	if Success:
		try:
			for item in Education:
				if AddEducation(item, ID) == False:
					Success = False
					Reason = "教育信息参数不合法，添加失败！"
					Code = Constants.ERROR_CODE_INVALID_PARAMETER
					break
		except:
			Success = False
			Reason = "添加用户失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success: 
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def AddEducation(TheEducation, ID):
	'''
	描述：添加一条教育信息到数据库
	参数：一条教育信息(字典),用户openid
	返回：成功True，失败False
	'''
	Success = True
	#把教育信息以外的东西插入数据库
	TheStartYear = 0
	TheDepartment = ""
	TheType = ""
	if Success:
		try:
			TheStartYear = int(TheEducation["enrollmentYear"])
			TheDepartment = TheEducation["department"]
			if TheEducation["enrollmentType"] == "Undergraduate":
				TheType = "U"
			elif TheEducation["enrollmentType"] == "Master":
				TheType = "M"
			elif TheEducation["enrollmentType"] == "Doctor":
				TheType = "D"
			else:
				Success = False
		except:
			Success = False
	if Success:
		try:
			TheUser = User.objects.get(OpenID = ID)
			Education.objects.create(StartYear = TheStartYear, Department= TheDepartment, Type = TheType, Student = TheUser)
		except:
			Success = False
	return Success

def GetCurrentUser(TheSession):
	'''
	描述：给定session，获得当前用户OpenID
	参数：session
	返回：用户OpenID，如果没有返回None
	'''
	Success = True
	TheUserId = ""
	if Success:
		try:
			TheUser = User.objects.get(Session = TheSession)
			TheUserId = TheUser.OpenID
		except:
			Success = False
	if Success:
		return TheUserId
	else:
		return None

def QueryUser(ID):
	'''
	描述：给定用户id，查询用户具体信息
	参数：用户id
	返回：一个字典，里面有用户id，名字，性别，状态，教育信息（数组）
	如果没有就返回空字典
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
	'''
	Success = True
	Object = None
	#查询
	if Success:
		try:
			Object = User.objects.get(OpenID = ID) 
		except:
			Success = False
	#print(Info)

	Result = {}
	if Success:
		try:
			Result["name"] = Object.Name
		except:
			Success = False
	
	#处理教育信息数据
	if Success:
		try:
			Result["campusIdentity"] = QueryEducation(Object.Education.all())
		except:
			Success = False
	if Success == False:
		Result = {}
	return Result

def QueryEducation(Info):
	'''
	描述：查询用户的所有教育信息
	参数：数据库信息
	返回：全部教育信息，没有返回空
	'''
	Success = True
	Return = []
	print(Info)
	#处理教育信息以外的数据并且返回
	Result = []
	if Success:
		try:
			for item in Info:
				OneResult = {}
				OneResult["enrollmentYear"] = str(item.StartYear)
				OneResult["department"] = item.Department
				if item.Type == 'U':
					OneResult["enrollmentType"] = "Undergraduate"
				elif item.Type == 'M':
					OneResult["enrollmentType"] = "Master"
				elif item.Type == 'D':
					OneResult["enrollmentType"] = "Doctor"
				else:
					Success = False
					break
				Result.append(OneResult)
		except:
			Success = False
	if Success == False:
		Result = []
	return Result

def JudgeParameterValid(CurTime, StartTime, EndTime, StartSignTime, StopSignTime, CurUser, MinUser, MaxUser):
	'''
	描述：判断一个活动时间和人员情况是否合理
	参数：当前时间，活动开始结束时间，报名开始结束时间，当前最小最大人数
	返回：{result：success}/失败{result：fail，reason：xxx}
	合理：
	当前时间小于等于结束时间
	开始和开始报名时间都应该小于等于对应结束时间
	开始报名时间小于等于开始时间，结束报名时间小于等于结束时间
	最大人数大于等于3,最小人数小于等于最大人数，最大人数大于等于当前人数
	'''
	Success = True
	Reason = ""
	Return = {}
	if CurTime > EndTime:
		Success = False
		Reason = "当前时间应该小于等于结束时间！"
	
	if StartSignTime > StopSignTime:
		Success = False
		Reason = "报名开始时间应该小于等于报名结束时间！"	
	if StartTime > EndTime:
		Success = False
		Reason = "活动开始时间应该小于等于活动结束时间！"
	if StartSignTime > StartTime:
		Success = False
		Reason = "开始报名时间应该小于等于开始时间！"
	if StopSignTime > EndTime:
		Success = False
		Reason = "结束报名时间应该小于等于结束时间！"
	if MaxUser != Constants.UNDEFINED_NUMBER:
		if MaxUser < 3:
			Success = False
			Reason = "最大人数应该大于等于3！"
		if MinUser > MaxUser:
			Success = False
			Reason = "最小人数应该小于等于最大人数！"
		if CurUser > MaxUser:
			Success = False
			Reason = "当前人数应该小于等于最大人数！"		
	if Success == True:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
	return Return

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
	#把时间转化为时间戳
	if Success:
		try:
			CurTime = GetCurrentTime()
			StartTime = TimeStringToTimeStamp(Information["start"])
			EndTime = TimeStringToTimeStamp(Information["end"])
			if 'signupBeginAt' in Information:
				StartSignTime = TimeStringToTimeStamp(Information["signupBeginAt"])
			else:
				StartSignTime = CurTime
			if 'signupStopAt' in Information:
				StopSignTime = TimeStringToTimeStamp(Information["signupStopAt"])
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
			JudgeResult = JudgeParameterValid(CurTime, StartTime, EndTime, StartSignTime, StopSignTime, 1, TheMinUser, TheMaxUser)
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
	#print(CurTime, StartTime, EndTime, StartSignTime, StopSignTime)
	#print(Success)
	#插入数据库
	if Success:
		try:
			TheName = Information["name"]
			ThePlace = Information["place"]
			TheType = Information["type"]

			#TheCreator = User.objects.get(OpenID = ID) 
			#print(TheCreator.ID)
			NewActivity = Activity.objects.create(Name = TheName, Place = ThePlace, StartTime = StartTime, EndTime = EndTime, SignUpStartTime = StartSignTime,\
			SignUpEndTime = StopSignTime, MinUser = TheMinUser, MaxUser = TheMaxUser, CurrentUser = 0, Type = TheType, Status = TheStatus, CanBeSearched = TheSearched)
			NewActivity.save()
			ActivityID = NewActivity.ID
		except:
			Success = False
			Reason = "参数不合法，添加活动失败!"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#print(Success)
	#让creator加入活动
	if Success:
		try:
			#print(int(Return["id"]))
			JoinActivityResult = JoinActivity(ID, ActivityID, True)
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

def CheckUserJoinedActivity(TheUserID, TheActivityID):
	'''
	描述：给定用户openid和活动id，判断用户是否参加了这个活动
	参数：用户openid，活动id
	返回：已参加：True，没参加：False
	'''
	Success = True
	Return = False
	TheName = "Database.db"
	if Success:
		try:
			Info = []
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			Info = JoinInformation.objects.filter(UserId = TheUser, ActivityId = TheActivity)
			if len(Info) != 0:
				Return = True
		except:
			Success = False
	if Return == True or Success == False:
		return True
	else:
		return False

def QueryActivity(TheActivityID):
	'''
	描述：给定活动id，查询活动具体信息
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
			Result["start"] = TimeStampToTimeString(int(Info.StartTime))
			Result["end"] = TimeStampToTimeString(int(Info.EndTime))
			Result["signupBeginAt"] = TimeStampToTimeString(int(Info.SignUpStartTime))
			Result["signupStopAt"] = TimeStampToTimeString(int(Info.SignUpEndTime))
			Result["minUser"] = int(Info.MinUser)
			Result["maxUser"] = int(Info.MaxUser)
			Result["curUser"] = int(Info.CurrentUser)
			Result["type"] = Info.Type
			Result["status"] = int(Info.Status)
			if Info.CanBeSearched == False:
				Success = False
		except:
			Success = False
	if Success == False:
		Result = {}
	return Result

def ShowAllActivity():
	'''
	描述：查询所有活动
	参数: 无
	返回：一个字典，里面就一个字典数组activityList，字典每个字典有活动具体信息
	如果没有就返回空字典
	'''
	#查询
	Success = True
	if Success:
		try:
			Info = Activity.objects.all()
		except:
			Success = False
	#处理数据并且返回
	Return = {}
	Result = []
	if Success:
		try:
			for item in Info:
				TheResult = {}
				TheResult["id"] = item.ID
				TheResult["name"] = item.Name
				TheResult["place"] = item.Place
				TheResult["start"] = TimeStampToTimeString(int(item.StartTime))
				TheResult["end"] = TimeStampToTimeString(int(item.EndTime))
				TheResult["signupBeginAt"] = TimeStampToTimeString(int(item.SignUpStartTime))
				TheResult["signupStopAt"] = TimeStampToTimeString(int(item.SignUpEndTime))
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
	else:
		Return = {}
	return Return

def ShowSelfActivity(TheUserID):
	'''
	描述：查询自己参与过的所有活动和历史记录
	参数: 自己的OpenID
	返回：一个字典，里面就一个字典数组activityList，字典每个字典有活动具体信息和自己的情况
	如果没有或者异常就返回空字典
	'''
	Result = {}
	Success = True
	ResultList = []
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
				TheResult = QueryActivity(item.ActivityId.ID)
				if TheResult == {}:
					Success = False
					break
				TheResult["id"] = item.ActivityId.ID
				TheResult["selfStatus"] = item.Status
				TheResult["selfRole"] = item.Role
				TheResult["joinTime"] = TimeStampToTimeString(item.JoinTime)
				if item.CheckTime != Constants.UNDEFINED_NUMBER:
					TheResult["checkTime"] = TimeStampToTimeString(item.CheckTime)
				ResultList.append(TheResult)
		except:
			Success = False
	if Success:
		Result["activityList"] = ResultList
	else:
		Result = {}
	return Result

def ShowAllMembers(TheActivityID):
	'''
	描述：查询活动所有成员
	参数: 活动id
	返回：一个字典，里面就一个字典数组participantList，字典每个字典有人员的Openid，权限，状态，报名和签到时间
	如果没有就返回空字典
	'''
	Result = {}
	Success = True
	ResultList = []
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			TheJoinActivityList = JoinInformation.objects.filter(ActivityId = TheActivity)
		except:
			Success = False
	
	if Success:
		try:
			for item in TheJoinActivityList:
				TheResult = {}
				TheResult["openId"] = item.UserId.OpenID
				TheResult["selfStatus"] = item.Status
				TheResult["selfRole"] = item.Role
				TheResult["joinTime"] = TimeStampToTimeString(item.JoinTime)
				if item.CheckTime != Constants.UNDEFINED_NUMBER:
					TheResult["checkTime"] = TimeStampToTimeString(item.CheckTime)
				ResultList.append(TheResult)
		except:
			Success = False
	if Success:
		Result["participantList"] = ResultList
	else:
		Result = {}
	return Result

def AddUserActivity(TheUserID, TheActivityID, TheStatus, TheRole):
	'''
	描述：报名函数	
	参数：用户id，活动id,状态，权限
	返回：成功{result：success}，失败{result：fail，reason：xxx, code:xxx}
	'''
	Success = True
	Return = {}
	Code = Constants.UNDEFINED_NUMBER
	Reason = ""
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
			TheActivity.CurrentUser = TheActivity.CurrentUser + 1
			TheActivity.save()
			TheJoinTime = GetCurrentTime()
			if TheStatus != Constants.USER_STATUS_WAITVALIDATE:
				TheCheckTime = TheJoinTime
			else:
				TheCheckTime = Constants.UNDEFINED_NUMBER
			#print(TheJoinTime, TheCheckTime)
			TheJoinInformation = JoinInformation.objects.create(UserId = TheUser, ActivityId = TheActivity, Status = TheStatus,\
			Role = TheRole, JoinTime = TheJoinTime, CheckTime = TheCheckTime)
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

def JudgeWhetherCanJoin(UserID, ActivityID):
	'''
	描述：判断高级报名是否成功，以及成功后结果
	参数：用户和活动ID
	返回：用户加入活动的状态---不允许加入(返回-1），直接允许加入，待审核
	'''
	return Constants.USER_STATUS_WAITVALIDATE

def JoinActivity(TheUserID, TheActivityID, WhetherCreator):
	'''
	描述：报名函数	
	参数：用户id，活动id,是否是管理员
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
		#查询该活动具体信息，判断时间是否过期以及是否可以加入人
		if Success:
			TheRole = Constants.USER_ROLE_CREATOR
			TheStatus = Constants.USER_STATUS_JOINED
			Return = AddUserActivity(TheUserID, TheActivityID, TheStatus, TheRole)
		else:
			Return["result"] = "fail"
			Return["reason"] = Reason
			Return["code"] = Code
	else:
		TheRole = Constants.USER_ROLE_COMMON
		#判断是否已经加入
		if Success:
			if CheckUserJoinedActivity(TheUserID, TheActivityID) == True:
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
			CurrentTime = GetCurrentTime()
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
			TheStatus = JudgeWhetherCanJoin(TheUserID, TheActivityID)
			if TheStatus == -1:
				Success = False
				Reason = "不符合报名条件"
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		#加入
		if Success:
			Return = AddUserActivity(TheUserID, TheActivityID, TheStatus, TheRole)
		else:
			Return["result"] = "fail"
			Return["reason"] = Reason
			Return["code"] = Code
	print(Return)
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
	if Success == True:
		Result["result"] = "success"
	else:
		Result["result"] = "fail"
		Result["reason"] = Reason 
		Result["code"] = Code
	return Result

def JudgeStatusValid(OldStatus, NewStatus, OldCanSee, NewCanSee):
	'''
	描述：判断一个状态和可见变更是否合理
	参数：旧新状态，可见性
	返回：{result：success}/{result：fail，reason：xxx}
	合理：
	0不能修改到其余状态
	1-7中，只有修改到0,3->2, 6->5这三个大号到小号的变更合理，其余不合理
	0状态必定不可见
	'''
	Success = True
	Return = {}
	Reason = ""
	try:
		if Success == True:
			if OldStatus == Constants.ACTIVITY_STATUS_EXCEPT and NewStatus != Constants.ACTIVITY_STATUS_EXCEPT:
				Success = False
				Reason = "活动已经被删除或封杀！"
		if Success == True:
			if OldStatus > NewStatus and NewStatus != Constants.ACTIVITY_STATUS_EXCEPT:
				if OldStatus == Constants.ACTIVITY_STATUS_SIGNINPAUSED and NewStatus == Constants.ACTIVITY_STATUS_SIGNIN:
					Success = True
				elif OldStatus == Constants.ACTIVITY_STATUS_SIGNUPPAUSED and NewStatus == Constants.ACTIVITY_STATUS_SIGNUP:
					Success = True
				else:
					Success = False
					Reason = "状态修改的时间顺序有误！"
		if Success == True:
			if NewStatus == Constants.ACTIVITY_STATUS_EXCEPT and NewCanSee == True:
				Success = False
				Reason = "活动被删除或被审核，不能显示其信息！"
	except:
		Success = False
		Reason = "参数非法！"
	if Success == True:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
	return Return
	
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
				ChangeDictionary["start"] = int(TimeStringToTimeStamp(Information["start"]))
			else:
				ChangeDictionary["start"] = TheActivity.StartTime
			if "end" in Information:
				ChangeDictionary["end"] = int(TimeStringToTimeStamp(Information["end"]))
			else:
				ChangeDictionary["end"] = TheActivity.EndTime
			if "signupBeginAt" in Information:
				ChangeDictionary["signupBeginAt"] = int(TimeStringToTimeStamp(Information["signupBeginAt"]))
			else:
				ChangeDictionary["signupBeginAt"] = TheActivity.SignUpStartTime	
			if "signupStopAt" in Information:
				ChangeDictionary["signupStopAt"] = int(TimeStringToTimeStamp(Information["signupStopAt"]))
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
			ChangeDictionary["curTime"] = GetCurrentTime()
			ChangeDictionary["curUser"] = TheActivity.CurrentUser
		except:
			Success = False
			Reason = "待修改数据格式不合法"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#判断修改后是否有效
	if Success:
		try:
			JudgeResult = JudgeParameterValid(ChangeDictionary["curTime"], ChangeDictionary["start"], ChangeDictionary["end"], \
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
	#判断修改后是否有效
	if Success:
		try:
			JudgeResult = JudgeStatusValid(TheActivity.Status, ChangeDictionary["status"],\
			 TheActivity.CanBeSearched, ChangeDictionary["canBeSearched"])
			if JudgeResult["result"] != "success":
				Success = False
				Reason = JudgeResult["reason"]
				Code = Constants.ERROR_CODE_INVALID_CHANGE
		except:
			Success = False
			Reason = "待修改数据格式不合法"	
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#修改
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
			TheActivity.save()
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
				

	
