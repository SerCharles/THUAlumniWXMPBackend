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
from Alumni.LogicManager.Constants import Constants
from Alumni.LogicManager import GlobalFunctions

#用户是否状态正常
def JudgeUserValid(TheOpenID):
	'''
	描述：判断用户状态是否正常
	参数：用户openid
	返回：正常True不正常False
	'''
	try:
		TheUser = User.objects.get(OpenID = TheOpenID)
	except:
		return False

	try:
		if TheUser.Status == True:
			return True
		else:
			return False
	except:
		return False


#院系，活动类型，教育类型等合法性判定
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

#活动状态判断
def JudgeActivityCanBeSearched(TheActivityID):
	'''
	描述：判断一个活动是否可见---仅用于列表返回和搜索
	是True，不是或失败False
	'''
	try:
		TheActivity = Activity.objects.get(ID = TheActivityID)
		if TheActivity.CanBeSearched == True and TheActivity.StatusGlobal != Constants.ACTIVITY_STATUS_GLOBAL_EXCEPT:
			return True
		else:
			return False
	except:
		return False

def JudgeActivityNormal(TheActivityID):
	'''
	描述：判断一个活动是否在正常状态（不能是结束或者异常）
	参数：活动ID
	返回：是True，不是或失败False
	'''
	Success = True
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			if TheActivity.StatusGlobal == Constants.ACTIVITY_STATUS_GLOBAL_NORMAL:
				Success = True
			else:
				Success = False
		except:
			Success = False
	return Success

def JudgeActivityCanJoin(TheActivityID):
	'''
	描述：判断一个活动是否可以报名（不能是结束或者异常）
	参数：活动ID
	返回：是True，不是或失败False
	'''
	Success = True
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			if TheActivity.StatusGlobal == Constants.ACTIVITY_STATUS_GLOBAL_NORMAL \
			and TheActivity.StatusJoin == Constants.ACTIVITY_STATUS_JOIN_CONTINUE:
				Success = True
			else:
				Success = False
		except:
			Success = False
	return Success

def JudgeActivityCanCheck(TheActivityID):
	'''
	描述：判断一个活动是否可以签到（不能是结束或者异常）
	参数：活动ID
	返回：是True，不是或失败False
	'''
	Success = True
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			if TheActivity.StatusGlobal == Constants.ACTIVITY_STATUS_GLOBAL_NORMAL \
			and TheActivity.StatusCheck == Constants.ACTIVITY_STATUS_CHECK_CONTINUE:
				Success = True
			else:
				Success = False
		except:
			Success = False
	return Success

def JudgeActivityStatusChangeValid(OldStatus, NewStatus):
	'''
	描述：判断一个活动状态变更是否合理---用户接口
	参数：旧新状态
	返回：{result：success}/{result：fail，reason：xxx}
	合理：
	状态只有正常之间可以任意变化，其余都8行
	0状态必定不可见
	'''
	Success = True
	Return = {}
	Reason = ""
	if Success:
		if OldStatus == Constants.ACTIVITY_STATUS_GLOBAL_NORMAL and NewStatus == Constants.ACTIVITY_STATUS_GLOBAL_NORMAL:
			Success = True
		else:
			Success = False
			Reason = "状态修改不合法，用户只能在活动正常状态间修改活动状态"
	if Success == True:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
	return Return

def JudgeActivityStatusGlobalValid(TheStatus):
	'''
	描述：判断活动全局状态是否合法
	参数：活动状态id
	返回：非法False，合法True
	'''
	if TheStatus in [Constants.ACTIVITY_STATUS_GLOBAL_EXCEPT, Constants.ACTIVITY_STATUS_GLOBAL_FINISH, \
	Constants.ACTIVITY_STATUS_GLOBAL_NORMAL]:
		return True
	else:
		return False

def JudgeActivityStatusJoinValid(TheStatus):
	'''
	描述：判断活动加入状态是否合法
	参数：活动状态id
	返回：非法False，合法True
	'''
	if TheStatus in [Constants.ACTIVITY_STATUS_JOIN_BEFORE, Constants.ACTIVITY_STATUS_JOIN_CONTINUE, \
	Constants.ACTIVITY_STATUS_JOIN_PAUSED, Constants.ACTIVITY_STATUS_JOIN_STOPPED]:
		return True
	else:
		return False

def JudgeActivityStatusCheckValid(TheStatus):
	'''
	描述：判断活动签到状态是否合法
	参数：活动状态id
	返回：非法False，合法True
	'''
	if TheStatus in [Constants.ACTIVITY_STATUS_CHECK_BEFORE, Constants.ACTIVITY_STATUS_CHECK_CONTINUE, \
	Constants.ACTIVITY_STATUS_CHECK_PAUSED, Constants.ACTIVITY_STATUS_CHECK_STOPPED]:
		return True
	else:
		return False

#用户-活动状态判断
def JudgeUserJoinedActivity(TheUserID, TheActivityID):
	'''
	描述：给定用户openid和活动id，判断用户是否参加了这个活动
	参数：用户openid，活动id
	返回：未参加或被拒绝：返回False，其余True
	'''
	Success = True
	Return = False
	if Success:
		try:
			Info = []
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			Info = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
			if Info.Status != Constants.USER_STATUS_REFUSED:
				return True
		except:
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
			Info = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
			if Info.Role == Constants.USER_ROLE_CREATOR or Info.Role == Constants.USER_ROLE_MANAGER:
				Return = True
		except:
			Success = False
	if Return == True and Success == True:
		return True
	else:
		return False

def JudgeWhetherCreator(TheUserID, TheActivityID):
	'''
	描述：判断一个用户是否是活动创建者
	是True，不是或失败False
	'''
	Success = True
	Return = False
	if Success:
		try:
			Info = []
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
			Info = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
			if Info.Role == Constants.USER_ROLE_CREATOR:
				Return = True
		except:
			Success = False
	if Return == True and Success == True:
		return True
	else:
		return False

def JudgeUserStatusJoined(TheStatus):
	'''
	描述：判断一个用户是否已加入活动（不能是待审核，被拒绝，异常）
	参数：状态
	返回：是True，不是False
	'''
	if TheStatus in [Constants.USER_STATUS_JOINED, Constants.USER_STATUS_CHECKED,\
	 Constants.USER_STATUS_FINISHED, Constants.USER_STATUS_FINISHED_WITHOUT_CHECK]:
		return True
	else:
		return False

def JudgeUserStatusDoingActivity(TheStatus):
	'''
	描述：判断一个用户是否正在参与（只能已加入或者已签到）
	参数：状态
	返回：是True，不是False
	'''
	if TheStatus in [Constants.USER_STATUS_JOINED, Constants.USER_STATUS_CHECKED]:
		return True
	else:
		return False

def JudgeUserStatusCanQuit(TheStatus):
	'''
	描述：判断一个用户是否可以退出活动（不能是被拒绝，异常，结束）
	参数：状态
	返回：是True，不是False
	'''
	if TheStatus in [Constants.USER_STATUS_JOINED, Constants.USER_STATUS_CHECKED, Constants.USER_STATUS_WAITVALIDATE]:
		return True
	else:
		return False

def JudgeSearchStatusValid(TheStatusGlobal, TheStatusJoin, TheStatusCheck, TheSelfStatus, TheRuleForMe):
	'''
	描述：判断一个活动搜索状态字段是否合理
	参数：活动三个状态，用户状态，报名结果
	返回：{result：success}/失败{result：fail，reason：xxx}
	合理：
	活动状态正常或结束
	用户状态正常或未报名
	报名规则如果有，用户状态必须是未报名
	'''
	Success = True
	Reason = ""
	Code = 0
	Return = {}
	if Success:
		if TheStatusGlobal not in [Constants.UNDEFINED_NUMBER, Constants.ACTIVITY_STATUS_GLOBAL_NORMAL, \
		Constants.ACTIVITY_STATUS_GLOBAL_FINISH]:
			Success = False
			Reason = "活动全局状态字段不合理！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
		if TheStatusJoin not in [Constants.ACTIVITY_STATUS_JOIN_BEFORE, Constants.ACTIVITY_STATUS_JOIN_CONTINUE, \
		Constants.ACTIVITY_STATUS_JOIN_PAUSED, Constants.ACTIVITY_STATUS_JOIN_STOPPED, Constants.UNDEFINED_NUMBER]:
			Success = False
			Reason = "活动加入状态字段不合理！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
		if TheStatusCheck not in [Constants.ACTIVITY_STATUS_CHECK_BEFORE, Constants.ACTIVITY_STATUS_CHECK_CONTINUE, \
		Constants.ACTIVITY_STATUS_CHECK_PAUSED, Constants.ACTIVITY_STATUS_CHECK_STOPPED, Constants.UNDEFINED_NUMBER]:
			Success = False
			Reason = "活动签到状态字段不合理！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
		if TheSelfStatus not in [Constants.UNDEFINED_NUMBER - 1, Constants.USER_STATUS_NOT_JOINED, Constants.USER_STATUS_JOINED\
		, Constants.USER_STATUS_WAITVALIDATE, Constants.USER_STATUS_CHECKED, Constants.USER_STATUS_FINISHED, \
		Constants.USER_STATUS_FINISHED_WITHOUT_CHECK]:
			Success = False
			Reason = "个人状态字段不合理！"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER	
		if TheRuleForMe not in [Constants.UNDEFINED_NUMBER - 1, Constants.USER_STATUS_WAITVALIDATE, \
		Constants.USER_STATUS_NOT_JOINED, Constants.USER_STATUS_JOINED]:
			Success = False
			Reason = "报名结果字段不合理"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
		if TheSelfStatus in [Constants.USER_STATUS_JOINED\
		, Constants.USER_STATUS_WAITVALIDATE, Constants.USER_STATUS_CHECKED, Constants.USER_STATUS_FINISHED, \
		Constants.USER_STATUS_FINISHED_WITHOUT_CHECK] and TheRuleForMe != Constants.UNDEFINED_NUMBER - 1:
			Success = False
			Reason = "报名结果字段和个人状态字段冲突，有报名结果字段的话，活动必定是用户未报名的"
			Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

#普通参数合理性判断
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
		if MaxUser < Constants.MIN_MAX_USER:
			Success = False
			Reason = "最大人数应该大于等于" + str(Constants.MIN_MAX_USER)+ "!"
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

def JudgeSearchTimeValid(StartTime, EndTime):
	'''
	描述：判断一个高级搜索的活动时间是否合理
	参数：开始,结束时间
	返回：{result：success}/失败{result：fail，reason：xxx}
	合理：
	'''
	Success = True
	Reason = ""
	Return = {}
	Code = 0
	if StartTime > EndTime:
		Success = False
		Reason = "开始时间应该小于等于结束时间！"	
		Code = Constants.ERROR_CODE_INVALID_PARAMETER
	if Success == True:
		Return["result"] = "success"
	else:
		Return["result"] = "fail"
		Return["reason"] = Reason
		Return["code"] = Code
	return Return

def JudgeTagListValid(TheList):
	'''
	描述：判断一个标签数组是否合法
	参数：标签数组
	返回：合法True，不合法False
	不合法：有英文逗号
	'''
	for item in TheList:
		for one in item:
			if one == ',':
				return False
	return True

def JudgeActivityTypeMatch(FatherType, SonType):
	'''
	描述：判断两个活动类型是否匹配
	参数：父亲类型，子类型
	返回：合法True，不合法False
	如果父亲类型==子类型，或者子类型包含父亲类型可以
	'''
	if len(FatherType) > len(SonType):
		return False
	if FatherType != SonType[0:len(FatherType)]:
		return False
	elif len(FatherType) == len(SonType):
		return True
	elif SonType[len(FatherType)] == '-':
		return True
	return False

#高级报名合理性判断
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
	#print(TheRule, TheEducation)
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

def JudgeWhetherCanJoinAdvanced(TheUserID, TheActivityID):
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

def JudgeWhetherFull(TheActivityID):
	'''
	描述：判断一个活动是否已经满了
	参数：活动ID
	返回：是True，不是或失败False
	'''
	Success = True
	if Success:
		try:
			TheActivity = Activity.objects.get(ID = TheActivityID)
			if TheActivity.MaxUser == Constants.UNDEFINED_NUMBER or TheActivity.CurrentUser < TheActivity.MaxUser:
				Success = False
			else:
				Success = True
		except:
			Success = True
	return Success

def GetSelfStatus(TheUserID, TheActivityID):
	'''
	描述：给定用户openid和活动id，判断用户参加活动状态
	参数：用户openid，活动id
	返回：返回status
	'''
	Success = True
	Return = 0
	if Success:
		try:
			Info = []
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Return = Constants.UNDEFINED_NUMBER - 1
	if Success:
		try:
			Info = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
			Return = Info.Status
			if Return in [Constants.USER_STATUS_ABNORMAL, Constants.USER_STATUS_REFUSED]:
				Return = Constants.UNDEFINED_NUMBER
		except:
			Return = Constants.UNDEFINED_NUMBER
	return Return

def GetSelfJoinStatus(TheUserID, TheActivityID):
	'''
	描述：给定用户openid和活动id，判断用户如果报名活动的状态
	参数：用户openid，活动id
	返回：返回status
	'''
	Success = True
	Return = 0
	Reason = ""
	if Success:
		try:
			Info = []
			TheUser = User.objects.get(OpenID = TheUserID)
			TheActivity = Activity.objects.get(ID = TheActivityID)
		except:
			Success = False
			Return = Constants.UNDEFINED_NUMBER - 1
	if Success:
		try:
			Info = JoinInformation.objects.get(UserId = TheUser, ActivityId = TheActivity)
			if Info.Status not in [Constants.USER_STATUS_ABNORMAL, Constants.USER_STATUS_REFUSED]:
				Success = False
				Return = Constants.UNDEFINED_NUMBER - 1
			else:
				Return = JudgeWhetherCanJoinAdvanced(TheUserID, TheActivityID)
		except:
			Return = JudgeWhetherCanJoinAdvanced(TheUserID, TheActivityID)
	return Return