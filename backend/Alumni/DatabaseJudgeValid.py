'''
判断各种数据库操作是否合法
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

def JudgeDepartmentValid(TheDepartment):
	'''
	描述：判断院系名称是否合法
	参数：名称
	返回：合法True不合法False
	'''
	Success = True
	try:
		FindDepartment = Department.objects.get(Name = TheDepartment)
	except:
		Success = False
	return Success

def JudgeActivityTypeValid(TheType):
	'''
	描述：判断活动类型是否合法
	参数：名称
	返回：合法True不合法False
	'''
	Success = True
	try:
		FindType = ActivityType.objects.get(Name = TheType)
		#print(FindType)
	except:
		Success = False
	return Success

def JudgeEducationTypeValid(TheType):
	'''
	描述：判断教育类型是否合法
	参数：名称
	返回：合法True不合法False
	'''
	Success = True
	try:
		FindType = EducationType.objects.get(Name = TheType)
	except:
		Success = False
	return Success


def JudgeUserJoinedActivity(TheUserID, TheActivityID):
	'''
	描述：给定用户openid和活动id，判断用户是否参加了这个活动
	参数：用户openid，活动id
	返回：已参加或失败：True，未参加：False
	'''
	Success = True
	Return = False
	if Success:
		try:
			Info = []
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			Info = JoinInformation.objects.filter(UserId = TheUser, ActivityId = TheActivity)
			if len(Info) != 0:
				#if Info.Status != Constants.USER_STATUS_MISSED:
				Return = True
		except:
			Success = False
	if Return == True or Success == False:
		return True
	else:
		return False

def JudgeWhetherManager(TheUserID, TheActivityID):
	'''
	描述：判断一个用户是否是活动管理员
	是True，不是或失败False
	'''
	Success = True
	Return = False
	if Success:
		try:
			Info = []
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			Info = JoinInformation.objects.filter(UserId = TheUser, ActivityId = TheActivity)
			if Info[0].Role == Constants.USER_ROLE_CREATOR or Info[0].Role == Constants.USER_ROLE_MANAGER:
				Return = True
		except:
			Success = False
	if Return == True and Success == True:
		return True
	else:
		return False

def JudgeCanBeSeen(TheActivityID):
	'''
	描述：判断一个活动是否可见
	是True，不是或失败False
	'''
	try:
		TheActivity = Activity.objects.get(ID = TheActivityID)
		if TheActivity.CanBeSearched == True:
			return True
		else:
			return False
	except:
		return False

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

def JudgeStatusChangeValid(OldStatus, NewStatus, OldCanSee, NewCanSee):
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

def JudgeSingleRuleValid(TheRule):
	'''
	描述：判断一条高级报名规则是否合法
	参数：规则
	返回：{result：success}/失败{result：fail，reason：xxx, code:xxx}
	'''
	Success = True
	Reason = ""
	Code = 0
	Return = {}
	if Success:
		try:
			ItemType = TheRule["enrollmentType"]
			if JudgeEducationTypeValid(ItemType) != True:
				Success = False
				Reason = "高级报名规则不合法，教育类型不合法"					
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
		except:
			ItemType = None
	if Success:
		try:
			ItemDepartment = TheRule["department"]
			if JudgeDepartmentValid(ItemDepartment) != True:
				Success = False
				Reason = "高级报名规则不合法，院系不合法"					
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
		except:
			ItemDepartment = None
	if Success:
		try:
			ItemStart = int(item["minEnrollmentYear"])
		except:
			ItemStart = None
		try:
			ItemEnd = int(item["maxEnrollmentYear"])
		except:
			ItemEnd = None
		if ItemStart != None and ItemEnd != None:
			if ItemStart > ItemEnd:
				Success = False
				Reason = "高级报名规则不合法，入学年份最小值应该小于等于最大值"					
				Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def JudgeRuleCollide(RuleA, RuleB):
	'''
	描述：判断两条高级报名规则是否冲突
	参数：两条规则
	返回：冲突True不冲突False
	'''
	TypeCollide = False
	DepartmentCollide = False
	TimeCollide = False
	try:
		ItemTypeA = RuleA["enrollmentType"]
	except:
		ItemTypeA = None
	try:
		ItemTypeB = RuleB["enrollmentType"]
	except:
		ItemTypeB = None
	if ItemTypeA != None and ItemTypeB != None:
		if ItemTypeA == ItemTypeB:
			TypeCollide = True
	else:
		TypeCollide = True

	try:
		ItemDepartmentA = RuleA["department"]
	except:
		ItemDepartmentA = None
	try:
		ItemDepartmentB = RuleB["department"]
	except:
		ItemDepartmentB = None
	if ItemDepartmentA != None and ItemDepartmentB != None:
		if ItemDepartmentA == ItemDepartmentB:
			DepartmentCollide = True
	else:
		DepartmentCollide = True	

	try:
		ItemMinA = int(RuleA["minEnrollmentYear"])
	except:
		ItemMinA = Constants.UNDEFINED_NUMBER
	try:
		ItemMaxA = int(RuleA["maxEnrollmentYear"])
	except:
		ItemMaxA = Constants.MAX_NUMBER
	try:
		ItemMinB = int(RuleB["minEnrollmentYear"])
	except:
		ItemMinB = Constants.UNDEFINED_NUMBER
	try:
		ItemMaxB = int(RuleB["maxEnrollmentYear"])
	except:
		ItemMaxB = Constants.MAX_NUMBER
	if ItemMaxA < ItemMinB or ItemMinA > ItemMaxB:
		TimeCollide = False
	else:
		TimeCollide = True
	
	if TimeCollide and DepartmentCollide and TypeCollide:
		return True
	else:
		return False

def JudgeRuleMatch(TheRule, TheEducation):
	'''
	描述：判断一条高级报名规则和一条教育信息是否匹配
	参数：规则和教育信息
	返回：匹配True不匹配False
	'''
	TypeCollide = False
	DepartmentCollide = False
	TimeCollide = False
	print(TheRule, TheEducation)
	TheRuleType = TheRule.EducationType
	if TheRule.EducationType == "UNDEFINED":
		TheRuleType = None
	TheEducationType = TheEducation.Type
	if TheRuleType != None:
		if TheRuleType == TheEducationType:
			TypeCollide = True
	else:
		TypeCollide = True

	TheRuleDepartment = TheRule.Department
	if TheRule.Department == "UNDEFINED":
		TheRuleDepartment = None
	TheEducationDepartment = TheEducation.Department
	if TheRuleDepartment  != None:
		if TheRuleDepartment  == TheEducationDepartment:
			DepartmentCollide = True
	else:
		DepartmentCollide = True

	TheRuleMinTime = TheRule.MinStartYear
	TheRuleMaxTime = TheRule.MaxStartYear
	if TheRuleMaxTime == Constants.UNDEFINED_NUMBER:
		TheRuleMaxTime = Constants.MAX_NUMBER
	TheEducationTime = TheEducation.StartYear
	if TheEducationTime >= TheRuleMinTime and TheEducationTime <= TheRuleMaxTime:
		TimeCollide = True
	
	print(TimeCollide, DepartmentCollide, TypeCollide)

	if TimeCollide and DepartmentCollide and TypeCollide:
		return True
	else:
		return False

def JudgeAdvancedRuleValid(Rule):
	'''
	描述：判断一组高级报名规则是否合理
	参数：当前规则
	返回：{result：success}/失败{result：fail，reason：xxx, code:xxx}
	合理：
	接受，审核，拒绝三个数组不能有交叉
	min < max
	学院名称合法
	教育类型合法
	'''
	TheAcceptRule = []
	TheAuditRule = []
	TheRejectRule = []
	Return = {}
	Success = True
	Reason = ""
	Code = 0
	try:
		TheAcceptRule = Rule["accept"]
	except:
		TheAcceptRule = []
	try:
		TheAuditRule = Rule["needAudit"]
	except:
		TheAuditRule = []
	try:
		TheRejectRule = Rule["reject"]
	except:
		TheRejectRule = []
	
	if Success:
		try:
			for item in TheAcceptRule:
				JudgeResult = JudgeSingleRuleValid(item)
				if JudgeResult["result"] != "success":
					Success = False
					Reason = JudgeResult["reason"]
					Code = JudgeResult["code"]
				for others in TheAuditRule:
					if JudgeRuleCollide(item, others) == True:
						Success = False
						Reason = "高级报名规则不合法，接受规则不能与审核规则冲突"
						Code = Constants.ERROR_CODE_INVALID_PARAMETER	
				for others in TheRejectRule:
					if JudgeRuleCollide(item, others) == True:
						Success = False
						Reason = "高级报名规则不合法，接受规则不能与拒绝规则冲突"
						Code = Constants.ERROR_CODE_INVALID_PARAMETER	

			for item in TheAuditRule:
				JudgeResult = JudgeSingleRuleValid(item)
				if JudgeResult["result"] != "success":
					Success = False
					Reason = JudgeResult["reason"]
					Code = JudgeResult["code"]

				for others in TheRejectRule:
					if JudgeRuleCollide(item, others) == True:
						Success = False
						Reason = "高级报名规则不合法，审核规则不能与拒绝规则冲突"
						Code = Constants.ERROR_CODE_INVALID_PARAMETER	

			for item in TheRejectRule:
				JudgeResult = JudgeSingleRuleValid(item)
				if JudgeResult["result"] != "success":
					Success = False
					Reason = JudgeResult["reason"]
					Code = JudgeResult["code"]
		except:
			Success = False
			Reason = "高级报名规则不合法，参数不合法！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def JudgeWhetherCanJoin(TheUserID, TheActivityID):
	'''
	描述：判断高级报名是否成功，以及成功后结果
	参数：用户和活动ID
	返回：用户加入活动的状态---不允许加入(返回-1），直接允许加入(1)，待审核(0)
	'''
	Finished = False
	TheStatus = Constants.UNDEFINED_NUMBER
	DefaultReturn = Constants.UNDEFINED_NUMBER
	JudgeAccept = True
	JudgeAudit = True
	JudgeReject = True
	if Finished == False:
		try:
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			return Constants.UNDEFINED_NUMBER
	if TheActivity.GlobalRule == Constants.ADVANCED_RULE_ACCEPT:
		JudgeAccept = False
		DefaultReturn = Constants.USER_STATUS_JOINED
	elif TheActivity.GlobalRule == Constants.ADVANCED_RULE_AUDIT:
		JudgeAudit = False
		DefaultReturn = Constants.USER_STATUS_WAITVALIDATE
	elif TheActivity.GlobalRule == Constants.ADVANCED_RULE_REJECT:
		JudgeReject = False
		DefaultReturn = Constants.UNDEFINED_NUMBER	

	#判断审核
	if Finished == False and JudgeAudit == True:
		for item in TheActivity.AdvancedRule.all():
			#print(item)
			if item.Type != Constants.ADVANCED_RULE_AUDIT:
				continue
			for others in TheUser.Education.all():
				if JudgeRuleMatch(item, others):
					Finished = True
					TheStatus = Constants.USER_STATUS_WAITVALIDATE
					return TheStatus
	#判断通过
	if Finished == False and JudgeAccept == True:
		for item in TheActivity.AdvancedRule.all():
			if item.Type != Constants.ADVANCED_RULE_ACCEPT:
				continue
			for others in TheUser.Education.all():
				if JudgeRuleMatch(item, others):
					Finished = True
					TheStatus = Constants.USER_STATUS_JOINED
					return TheStatus

	#判断拒绝
	if Finished == False and JudgeReject == True:
		for item in TheActivity.AdvancedRule.all():
			if item.Type != Constants.ADVANCED_RULE_REJECT:
				continue
			for others in TheUser.Education.all():
				if JudgeRuleMatch(item, others):
					Finished = True
					TheStatus = Constants.UNDEFINED_NUMBER
					return TheStatus		
	#返回默认值
	return DefaultReturn