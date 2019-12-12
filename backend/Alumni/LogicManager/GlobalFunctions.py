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
import qrcode 
import requests
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
from DataBase.models import Picture
from DataBase.models import Admin
from DataBase.models import ReportInformation
from Alumni.LogicManager.Constants import Constants

#时间相关函数
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

def JudgeWhetherDayEnd():
	'''
	功能：判断当时是否是一天23点59分
	参数：无
	返回：True是，False否
	'''
	CurTime = int(time.time())
	TimeArray = time.localtime(CurTime) 
	TimeString = time.strftime("%Y-%m-%d %H:%M:%S", TimeArray)
	print(TimeString[-8:-3])
	if TimeString[-8:-3] == "23:59":
		return True
	else:
		return False

def JudgeWhetherSameDay(TimeStamp):
	'''
	功能：在23：59判断是否某时间在当天
	参数：待判断时间戳
	返回：True是，False否
	'''
	CurTime = int(time.time())
	if CurTime + 60 >= TimeStamp and CurTime - TimeStamp < 86400:
		return True
	else:
		return False

def JudgeWhetherSameMinute(TimeStamp):
	CurTime = int(time.time())
	if CurTime >= TimeStamp and CurTime - TimeStamp < 60:
		return True
	else:
		return False

#登录相关函数
def GenerateSessionID():
	'''
	描述：生成随机session
	参数：无
	返回：session
	'''
	while True:
		length = random.randint(10,50)
		TheSession =  ''.join(random.sample(string.ascii_letters + string.digits, length))
		#print(TheSession)
		try:
			TheUser = User.objects.get(Session = TheSession)
			TheManager = Admin.objects.get(Session = TheSession)
		except:
			break
	return TheSession

def GenerateActivityCode():
	'''
	描述：生成随机活动code
	参数：无
	返回：code
	'''
	while True:
		length = random.randint(10,50)
		TheSession =  ''.join(random.sample(string.ascii_letters + string.digits, length))
		#print(TheSession)
		try:
			TheUser = Activity.objects.get(Code = TheSession)
		except:
			break
	return TheSession

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

def SetAccessToken():
	'''
	描述：设置（从微信服务器拉取access token）
	参数：无
	返回：成功true失败False，后面有原因
	'''	
	Success = True
	Return = {}
	TheParam = {}
	Reason = "--------"
	if Success:
		try:
			TheAppID = GlobalVariables.objects.get(id = 1)
			TheParam["appid"] = TheAppID.AppId
			TheParam["secret"] = TheAppID.SecretId
			TheParam["grant_type"] = "client_credential"
		except:	
			Success = False
	if Success:
		if 1:
			TheRequest = requests.get("https://api.weixin.qq.com/cgi-bin/token", params = TheParam, timeout = (5,10), allow_redirects = True)
		else:
			Success = False
			Reason = "网络繁忙，访问超时！"      
	if Success:
		try:
			if TheRequest.status_code < 200 or TheRequest.status_code >= 400:
				Success = False
				Reason = "网络繁忙，访问微信失败！！"
			TheJson = TheRequest.json()
			print(TheJson)
			if "errcode" in TheJson:
				if TheJson["errcode"] != 0:
					Success = False
				else:
					TheAppID.AccessToken = TheJson["access_token"]
					TheAppID.save()
			else:
				TheAppID.AccessToken = TheJson["access_token"]
				TheAppID.save()
		except:
			Success = False  
	return Success, Reason

def GetAccessToken():
	'''
	描述：获得access token
	参数：无
	返回：accesstoken，字符串,如果失败返回UNDEFINED
	'''	
	Return = {}
	try:
		TheAppID = GlobalVariables.objects.get(id = 1)
		return TheAppID.AccessToken
	except:
		return "UNDEFINED"

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

#院系，活动类型，教育类型相关函数
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

def MergeTags(TheTagList):
	'''
	描述：将标签合并到一起存储，不同标签用英文逗号切分
	参数：标签列表
	返回：合并的标签
	'''
	TheTag = ""
	for i in range(len(TheTagList)):
		TheTag += TheTagList[i]
		if i != len(TheTagList) - 1:
			TheTag += ','
	return TheTag

def SplitTags(TheTag):
	'''
	描述：将合并到一起存储的标签切分
	参数：合并的标签
	返回：标签列表
	'''
	return TheTag.split(',')


def SplitFileName(TheFileName):
	'''
	描述：切分文件名
	参数：文件名
	返回：没有扩展名的文件名+扩展名
	'''
	TheExtention = '.' + TheFileName.split('.')[-1]
	TheMainFileName = TheFileName[ : 0 - len(TheExtention)]
	return TheMainFileName, TheExtention

def GetTrueAvatarUrlUser(TheURL):
	'''
	描述：获取用户头像，如果有就正常返回，否则返回默认
	参数：数据库里存储的用户头像
	返回：成功：url，失败：none
	'''
	if TheURL != "UNDEFINED":
		return TheURL
	try:
		TheAvatar = Picture.objects.get(ID = 0)
		TheCreateTime = TheAvatar.CreateTime
		TheFileName = TheAvatar.Image.name
		TheURL = '/media/' + TheFileName
		return TheURL
	except:
		return None

def GetTrueAvatarUrlActivity(TheURL):
	'''
	描述：获取活动头像，如果有就正常返回，否则返回默认
	参数：数据库里存储的活动头像
	返回：成功：url，失败：none
	'''
	if TheURL != "UNDEFINED":
		return TheURL
	try:
		TheAvatar = Picture.objects.get(ID = 1)
		TheCreateTime = TheAvatar.CreateTime
		TheFileName = TheAvatar.Image.name
		TheURL = '/media/' + TheFileName
		return TheURL
	except:
		return None

def UploadPicture(TheData):
	'''
	描述：上传图片
	参数：数据
	返回：result-success还是fail，fail需要原因和错误码，success需要url
	'''
	FileEXT = TheData.name.split('.').pop()
	Result = {}
	Success = True
	Reason = ""
	Code = 0
	TheURL = ""
	try:
		TheCreateTime = GetCurrentTime()
		NewPicture = Picture.objects.create(Image = TheData, CreateTime = TheCreateTime)
		NewPicture.save()
		TheMainFileName, TheExtention = SplitFileName(TheData.name)
		TheURL = '/media/' + TheMainFileName + '_' + str(TheCreateTime) + TheExtention
	except:
		Success = False
		Code = Constants.ERROR_CODE_UNKNOWN
		Reason = "上传图片失败！"
	if Success:
		Result["result"] = "success"
		Result["url"] = TheURL
	else:
		Result["result"] = "fail"
		Result["reason"] = Reason
		Result["code"] = Code
	return Result

#二维码相关函数
def GetQRCodeDir(TheActivityID):
	'''
	描述：获取二维码文件的文件名
	参数：活动id
	返回：文件名
	'''
	TheDirectory = 'media/QRCode'
	if not os.path.exists(TheDirectory):
		os.makedirs(TheDirectory)
	TheFileName = TheDirectory + '/' + str(TheActivityID) + '.png'
	if os.path.exists(TheFileName):
		os.remove(TheFileName)
	return TheFileName

def GenerateQRCode(TheActivityID, TheCode):
	'''
	描述：生成活动对应的二维码
	参数：活动id,活动code
	返回：二维码文件名
	'''
	TheImage = qrcode.make(TheCode)
	TheFileName = GetQRCodeDir(TheActivityID)
	TheImage.save(TheFileName)
	return TheFileName


	