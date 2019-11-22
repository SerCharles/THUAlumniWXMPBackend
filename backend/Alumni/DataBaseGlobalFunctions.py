'''
各种全局重要函数，比如生成session，时间获取与转格式，获取小程序基本信息等
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


def GenerateSessionID():
	'''
	描述：生成随机session
	参数：无
	返回：session
	'''
	while True:
		length = random.randint(10,50)
		TheSession =  ''.join(random.sample(string.ascii_letters + string.digits + '!@#$%^&*()', length))
		print(TheSession)
		try:
			TheUser = User.objects.get(Session = TheSession)
		except:
			break
	return TheSession

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

def GetAppIDWechat():
	'''
	描述：获取小程序APPID（微信）
	参数：无
	返回：一个列表，小程序appid和secretid
	'''	
	Return = {}
	try:
		TheAppID = GlobalVariables.objects.get(id = 1)
		Return["appid"] = TheAppID.AppId
		Return["secret"] = TheAppID.SecretId
	except:
		Return = {}
	return Return

def GetAppIDThis():
	'''
	描述：获取小程序APPID（这个app）
	参数：无
	返回：一个列表，小程序appid和secretid
	'''	
	Return = {}
	try:
		TheAppID = GlobalVariables.objects.get(id = 2)
		Return["appId"] = TheAppID.AppId
		Return["appSecret"] = TheAppID.SecretId
	except:
		Return = {}
	return Return

def AddDepartment(TheDepartment):
	'''
	描述：如果院系不存在，就添加一个
	参数：名称
	返回：合法True不合法False
	'''
	try:
		FindDepartment = Department.objects.get(Name = TheDepartment)
	except:
		Department.objects.create(Name = TheDepartment)

def AddActivityType(TheType):
	'''
	描述：如果活动类型不存在，就添加一个
	参数：名称
	返回：无
	'''
	try:
		FindType = ActivityType.objects.get(Name = TheType)
	except:
		ActivityType.objects.create(Name = TheType)

def AddEducationType(TheType):
	'''
	描述：如果教育类型不存在，就添加一个
	参数：名称
	返回：无
	'''
	try:
		FindType = EducationType.objects.get(Name = TheType)
	except:
		EducationType.objects.create(Name = TheType)

def ShowAllEducationType():
	'''
	描述：查找数据库里所有的教育类型
	参数：无
	返回：一个json字典，代表所有教育类型，格式如下
	{
		"types": []
	}
	失败返回空字典
	'''
	Return = {}
	Success = True
	TheTypeList = []
	if Success:
		try:
			AllTypes = EducationType.objects.filter()
			for TypeItem in AllTypes:
				TheTypeName = TypeItem.Name
				TheTypeList.append(TheTypeName)
		except:
			Success = False
	if Success:
		Return["types"] = TheTypeList
	else:
		Return = {}
	return Return

def ShowAllDepartment():
	'''
	描述：查找数据库里所有的院系类型
	参数：无
	返回：一个json字典，代表所有院系类型，格式如下
	{
		"departments": []
	}
	失败返回空字典
	'''
	Return = {}
	Success = True
	TheDepartmentList = []
	if Success:
		try:
			AllDepartments = Department.objects.filter()
			for DepartmentItem in AllDepartments:
				TheName = DepartmentItem.Name
				TheDepartmentList.append(TheName)
		except:
			Success = False
	if Success:
		Return["departments"] = TheDepartmentList
	else:
		Return = {}
	return Return

def ShowAllActivityType():
	'''
	描述：查找并拆分数据库里所有的活动类型
	参数：无
	返回：一个json字典，代表所有活动类型，格式如下
	{
  	"types": [
    {
      "name": "个人活动",
      "children": [
        {
          "name": "聚餐"
        },
        {
          "name": "聚餐"
        }
      ]
    }
  	],
  	"level": 2
	}
	失败返回空字典
	'''
	Return = {}
	Success = True
	TheLevel = 0
	TheTypeList = []
	if Success:
		try:
			AllTypes = ActivityType.objects.filter()
			for TypeItem in AllTypes:
				TheTypeLevels = TypeItem.Name.split('-')
				CurrentTypeList = TheTypeList
				if len(TheTypeLevels) > TheLevel:
					TheLevel = len(TheTypeLevels)
				for i in range(len(TheTypeLevels)):
					item = TheTypeLevels[i]
					WhetherFind = False
					for others in CurrentTypeList:
						if others["name"] == item:
							#找到层次了
							WhetherFind = True
							if "children" in others:
								CurrentTypeList = others["children"]
							else:
								others["children"] = []
								CurrentTypeList = others["children"]
							break
					if WhetherFind == False:
						NewDictionary = {}
						NewDictionary["name"] = item
						if i != len(TheTypeLevels) - 1:
							NewDictionary["children"] = []
						CurrentTypeList.append(NewDictionary)
						if i != len(TheTypeLevels) - 1:
							CurrentTypeList = CurrentTypeList[-1]["children"]
		
		except:
			Success = False
	if Success:
		Return["types"] = TheTypeList
		Return["level"] = TheLevel
	else:
		Return = {}
	return Return




