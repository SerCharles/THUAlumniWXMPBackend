'''
处理用户操作的数据库函数集合
处理登录，查询用户信息的各种数据库函数
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


def AddUserID(TheOpenID, TheSessionKey, TheSession):
	'''
	描述：添加一个用户的openid，session等到数据库
	参数：openid，sessionkey，session
	返回：成功：{
  	"result": "success",
  	"session": "123456abcdef",
  	"openId": "asfsfs"
	}
	result：如果用户之前不存在，是success。如果用户之前存在，是exist。
	'''
	Return = {}
	try:
		TheExistUser = User.objects.get(OpenID = TheOpenID)
		TheExistUser.Session = TheSession
		TheExistUser.SessionKey = TheSessionKey
		TheExistUser.save()
		if TheExistUser.Valid == True:
			Return["result"] = "exist"
			Return["session"] = TheSession
			Return["openId"] = TheOpenID
		else:
			Return["result"] = "success"
			Return["session"] = TheSession
			Return["openId"] = TheOpenID
	except:
		User.objects.create(OpenID = TheOpenID, Session = TheSession, SessionKey = TheSessionKey, \
		Name = "UNDEFINED", RequestID = "UNDEFINED", AvatarURL = "UNDEFINED", Valid = False)
		Return["result"] = "success"
		Return["session"] = TheSession
		Return["openId"] = TheOpenID
	return Return

def AddRequestID(TheSession, TheRequestID):
	'''
	描述：添加一个用户的requestID到数据库
	参数：session, requestid
	返回：成功：true 失败 false
	'''
	try:
		TheUser = User.objects.get(Session = TheSession)
		TheUser.RequestID = TheRequestID
		TheUser.save()
		return True
	except:
		return False

def SetAvatarURL(TheOpenID, TheURL):
	'''
	描述：添加一个用户的头像url到数据库
	参数：openid, 头像url
	返回：成功：true 失败 false
	'''
	try:
		TheUser = User.objects.get(OpenID = TheOpenID)
		TheUser.AvatarURL = TheURL
		TheUser.save()
		return True
	except:
		return False

def AddUser(TheInfo):
	'''
	描述：添加一个用户的信息到数据库(requestId已存在)	
	参数：字典数组
	返回：成功{result：success}，失败{result：fail，reason：xxx, code:xxx}
	''' 
	Return = {}
	Code = Constants.UNDEFINED_NUMBER
	Success = True
	Reason = ""
	TheRequestID = ""
	TheName = ""
	TheEducation = []
	TheOpenID = ""
	#把教育信息以外的东西插入数据库
	if Success:
		try:
			TheRequestID = TheInfo["requestId"]
			TheUserInfo = TheInfo["user"]
		except:
			Success = False
			Reason = "请求参数非法！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		try:
			NewUser = User.objects.get(RequestID = TheRequestID)
		except:
			Success = False
			Reason = "该RequestID不存在，可能是伪造的！"
			Code = Constants.ERROR_CODE_NOT_FOUND
	if Success:
		try:
			TheName = TheUserInfo["legalIdentity"]["legalName"]
			TheEducation = TheUserInfo["campusIdentity"]
		except:
			Success = False
			Reason = "用户拒绝了该请求！！"
			Code = Constants.ERROR_CODE_DENIAL
	if Success:
		try:
			TheOpenID = NewUser.OpenID
			NewUser.Name = TheName
			NewUser.save()
		except:
			Success = False
			Reason = "参数不合法，添加失败！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	#print(Success)
	#把教育信息插入数据库
	if Success:
		try:
			for item in TheEducation:
				if AddEducation(item, TheOpenID) == False:
					Success = False
					Reason = "教育信息参数不合法，添加失败！"
					Code = Constants.ERROR_CODE_INVALID_PARAMETER
					break
		except:
			Success = False
			Reason = "添加用户失败！"
			Code = Constants.ERROR_CODE_UNKNOWN
	if Success:
		NewUser.Valid = True
		NewUser.save()
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
	TheStartYear = 0
	TheDepartment = ""
	TheType = ""
	if Success:
		try:
			TheStartYear = int(TheEducation["enrollmentYear"])
			TheDepartment = TheEducation["department"]
			TheType = TheEducation["enrollmentType"]
		except:
			Success = False
	if Success:
		try:
			TheUser = User.objects.get(OpenID = ID)
			Education.objects.create(StartYear = TheStartYear, Department = TheDepartment, Type = TheType, Student = TheUser)
			#如果有数据库中不存在的教育信息，插入
			GlobalFunctions.AddEducationType(TheType)
			GlobalFunctions.AddDepartment(TheDepartment)
		except:
			Success = False
	return Success

def GetCurrentUser(TheSession):
	'''
	描述：给定session，获得当前用户OpenID--用于判断登录
	参数：session
	返回：用户OpenID，如果没有返回None
	'''
	Success = True
	TheUserId = ""
	if Success:
		try:
			TheUser = User.objects.get(Session = TheSession)
			TheUserId = TheUser.OpenID
			if TheUser.Valid == False:
				Success = False
		except:
			Success = False
	if Success:
		return TheUserId
	else:
		return None

def GetCurrentUserInQueryUser(TheSession):
	'''
	描述：给定session，获得当前用户OpenID--用于判断登录,仅用于获取用户信息时
	参数：session
	返回：{result：success/fail} 
	如果成功，带一个字段：openId
	如果失败，带字段：reason，code
	'''
	Success = True
	Reason = ""
	Code = 0
	TheUserId = ""
	Return = {}
	if Success:
		try:
			TheUser = User.objects.get(Session = TheSession)
			TheUserId = TheUser.OpenID
			if TheUser.Valid == False:
				Success = False
				Reason = "用户没有用户信息，可能是回调接口未即时返回"
				Code = Constants.ERROR_CODE_NOT_STORED
		except:
			Success = False
			Reason = "用户未登录！"
			Code = Constants.ERROR_CODE_LOGIN_ERROR
	if Success:
		Return["result"] = "success"
		Return["openId"] = TheUserId
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

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
			Result["avatarUrl"]	= GlobalFunctions.GetTrueAvatarUrlUser(Object.AvatarURL)
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
	#print(Info)
	#处理教育信息以外的数据并且返回
	Result = []
	if Success:
		try:
			for item in Info:
				OneResult = {}
				OneResult["enrollmentYear"] = str(item.StartYear)
				OneResult["department"] = item.Department
				OneResult["enrollmentType"] = item.Type
				#print(OneResult)
				Result.append(OneResult)
		except:
			Success = False
	if Success == False:
		Result = []
	return Result