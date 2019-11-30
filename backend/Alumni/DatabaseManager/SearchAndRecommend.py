'''
用于推荐与搜索的类和函数

'''
from __future__ import unicode_literals
from whoosh.fields import Schema, TEXT, ID
import os.path
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh.qparser import syntax
from whoosh.index import open_dir
from jieba.analyse import ChineseAnalyzer
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




class WhooshSearcher:
    '''
	用于搜索的类，采用单体模式
	'''
    #单体模式
    _instance = None
    Analyzer = None
    Schema = None
    Index = None
    #Searcher = None
    AndParser = None
    OrParser = None
    #Writer = None

    @classmethod
    def Create(cls):
        '''
	    单体模式
	    '''
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        '''
	    初始化
	    '''
        self.Analyzer = ChineseAnalyzer()
        self.Schema = Schema(path = ID(stored = True, unique = True),\
         content = TEXT(stored =True, analyzer= self.Analyzer))
        if not os.path.exists("IndexPath"):
            os.mkdir("IndexPath")
        self.Index = create_in("IndexPath", self.Schema)
        #self.Writer = self.Index.writer()
        #self.Searcher = self.Index.searcher()
        SelfGroup = syntax.OrGroup.factory(0.9)
        self.AndParser = QueryParser("content", schema = self.Index.schema)
        self.OrParser = QueryParser("content", schema = self.Index.schema, group = SelfGroup)
        self.LoadDatabaseInfo()

    def LoadDatabaseInfo(self):
        '''
	    描述：从数据库里读取现有的信息用于搜索推荐
        参数：无
        返回：无
	    '''
        Info = Activity.objects.all()
        Writer = self.Index.writer()
        for item in Info:
            if JudgeValid.JudgeActivityNormal(item.ID):
                Writer.add_document(
                    path = "/" + str(item.ID),
                    content = item.Name + item.Tags
                )
        Writer.commit()

    def AddOneInfo(self, TheID, TheTitle):
        '''
	    描述：添加活动时，增加对应的信息用于搜索推荐
        参数：活动id，内容
        返回：无
	    '''
        #print(1)
        Writer = self.Index.writer()
        Writer.add_document(
            path = "/" + str(TheID),
            content = TheTitle
            )
        Writer.commit()   

    def DeleteOneInfo(self, TheID):
        '''
	    描述：删除活动时，删除对应的信息用于搜索推荐
        参数：活动id
        返回：无
	    '''
        Writer = self.Index.writer()
        Writer.delete_by_term("path","/" + str(TheID))
        Writer.commit()  

    def UpdateOneInfo(self, TheID, NewContent):
        '''
	    描述：修改活动时，更新对应的信息用于搜索推荐
        参数：活动id，新内容
        返回：无
	    '''
        Writer = self.Index.writer()
        Writer.update_document(
            path = "/" + str(TheID),
            content = NewContent
            )
        Writer.commit()  

    def SearchInfo(self, TheKeyWord):
        '''
	    描述：根据关键词搜索活动
        参数：关键词
        返回：无
	    '''
        Return = {}
        TheInfoList = []
        Searcher = self.Index.searcher()
        ParsedKeyword = self.AndParser.parse(TheKeyWord)
        print(str(ParsedKeyword))

        TheAndResult = Searcher.search(ParsedKeyword)
        IDList = []
        InfoNum = 0
        for i in range(len(TheAndResult)):
            hit = TheAndResult[i]
            TheInfo = {}
            TheNumberID = int(hit["path"][1:])
            TheInfo = self.GetOneActivityInfo(TheNumberID)
            if TheInfo != {}:
                TheInfoList.append(TheInfo)
                IDList.append(TheNumberID)
                InfoNum  = InfoNum + 1
                if InfoNum >= Constants.MAX_SEARCH_RESULT:
                    break
        
        if InfoNum < Constants.MAX_SEARCH_RESULT:
            ParsedKeyword = self.OrParser.parse(TheKeyWord)
            #print(ParsedKeyword)
            TheOrResult = Searcher.search(ParsedKeyword)
            #print(TheOrResult)
            for i in range(len(TheOrResult)):
                hit = TheOrResult[i]
                TheInfo = {}
                TheNumberID = int(hit["path"][1:])
                #print(TheNumberID)
                if TheNumberID in IDList:
                    continue
                TheInfo = self.GetOneActivityInfo(TheNumberID)
                if TheInfo != {}:
                    TheInfoList.append(TheInfo)
                    IDList.append(TheNumberID)
                    InfoNum = InfoNum + 1
                    if InfoNum >= Constants.MAX_SEARCH_RESULT:
                        break
        Return["activityList"] = TheInfoList
        #print(IDList)
        #print(Return)
        return Return

    def Recommend(self, TheSentenceList):
        Return = {}
        TheInfoList = []
        Searcher = self.Index.searcher()
        TheUseString = self.GetMostImportantWords(TheSentenceList)
        #print(TheUseString)
        ParsedKeyword = self.OrParser.parse(TheUseString)
        #print(ParsedKeyword)
        TheOrResult = Searcher.search(ParsedKeyword)
        InfoNum = 0
        for i in range(len(TheOrResult)):
            hit = TheOrResult[i]
            TheInfo = {}
            TheNumberID = int(hit["path"][1:])
            TheInfo = self.GetOneActivityInfo(TheNumberID)
            if TheInfo != {}:
                TheInfoList.append(TheInfo)
                InfoNum = InfoNum + 1
                if InfoNum >= Constants.MAX_SEARCH_RESULT:
                    break
        Return["activityList"] = TheInfoList
        #print(Return)
        return Return

    def GetMostImportantWords(self, TheSentenceList):
        TheWordList = []
        
        for item in TheSentenceList:
            ParsedKeyword = self.AndParser.parse(item)
            if str(ParsedKeyword)[0] != '(':
                TheParsedWordList = []
                TheParsedWordList.append(str(ParsedKeyword))
            else:
                TheParsedWordList = str(ParsedKeyword)[1:-1].split()[::2]
            for OneWord in TheParsedWordList:
                ProcessedWord = OneWord[8:]
                #print(ProcessedWord)
                WhetherExist = False
                for ExistWord in TheWordList:
                    if ProcessedWord == ExistWord["word"]:
                        WhetherExist = True
                        ExistWord["frequency"] = ExistWord["frequency"] + 1
                        break
                if WhetherExist == False:
                    NewWord = {}
                    NewWord["word"] = ProcessedWord
                    NewWord["frequency"] = 1
                    TheWordList.append(NewWord)
        SortedWordList = sorted(TheWordList, key = lambda x:x["frequency"], reverse = True)
        print(SortedWordList)
        UsedLength = min(len(SortedWordList), Constants.MAX_RECOMMEND_WORD)
        TheReturnString = ""
        for i in range(UsedLength):
            TheReturnString = TheReturnString + SortedWordList[i]["word"] + ' '
        return TheReturnString

    def GetOneActivityInfo(self, TheID):
        TheResult = {}
        Success = True
        try:
            TheActivity = Activity.objects.get(ID = TheID)
            TheResult["id"] = TheID
            TheResult["name"] = TheActivity.Name
            TheResult["place"] = TheActivity.Place
            TheResult["createTime"] = GlobalFunctions.TimeStampToTimeString(int(TheActivity.CreateTime))
            TheResult["start"] = GlobalFunctions.TimeStampToTimeString(int(TheActivity.StartTime))
            TheResult["end"] = GlobalFunctions.TimeStampToTimeString(int(TheActivity.EndTime))
            TheResult["signupBeginAt"] = GlobalFunctions.TimeStampToTimeString(int(TheActivity.SignUpStartTime))
            TheResult["signupStopAt"] = GlobalFunctions.TimeStampToTimeString(int(TheActivity.SignUpEndTime))
            TheResult["minUser"] = int(TheActivity.MinUser)
            TheResult["maxUser"] = int(TheActivity.MaxUser)
            TheResult["curUser"] = int(TheActivity.CurrentUser)
            TheResult["type"] = TheActivity.Type
            TheResult["statusGlobal"] = int(TheActivity.StatusGlobal)
            TheResult["statusJoin"] = int(TheActivity.StatusJoin)
            TheResult["statusCheck"] = int(TheActivity.StatusCheck)
            TheResult["tags"] = GlobalFunctions.SplitTags(TheActivity.Tags)
            #print(TheResult)
            if JudgeValid.JudgeActivityCanBeSearched(TheID) != True:
                Success = False
        except:
            Success = False
        if Success:
            return TheResult
        else:
            return {}


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
			TheSearcher = WhooshSearcher.Create()
			RawReturnInfo = TheSearcher.Recommend(TheWordList)
			#print(RawReturnInfo)
			Buf1ReturnInfo = RemoveJoinedActivity(TheUserID, RawReturnInfo)
			Buf2ReturnInfo = RemoveSelfFromList(TheActivityID, Buf1ReturnInfo)
			ReturnInfo = RemoveRefuseActivity(TheUserID, Buf2ReturnInfo)
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
			TheSearcher = WhooshSearcher.Create()
			RawReturnInfo = TheSearcher.Recommend(TheWordList)
			BufReturnInfo = RemoveJoinedActivity(TheUserID, RawReturnInfo)
			ReturnInfo = RemoveRefuseActivity(TheUserID, BufReturnInfo)
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
				if item.Status != Constants.USER_STATUS_ABNORMAL:
					TheWordList.append(item.ActivityId.Name)
					TheWordList.append(item.ActivityId.Tags)
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
				if JudgeValid.JudgeUserJoinedActivity(TheUserID, TheActivityID) != True:
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

def RemoveRefuseActivity(TheUserID, TheActivityList):
	'''
	描述：移除用户参与必定被拒绝的活动
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
				WhetherCanJoin = JudgeValid.JudgeWhetherCanJoinAdvanced(TheUserID, TheActivityID)
				if WhetherCanJoin != Constants.UNDEFINED_NUMBER:
					NewActivityList.append(item)
		except:
			Success = False
	if Success:
		Return["activityList"] = NewActivityList
	else:
		Return = {}
	return Return