'''
用于推荐与搜索的函数

'''
from __future__ import unicode_literals
from whoosh.fields import Schema, TEXT, ID
import os.path
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh.qparser import syntax
from whoosh.index import open_dir
from jieba.analyse import ChineseAnalyzer
from DataBase.models import Activity
from . import DataBaseGlobalFunctions
from Alumni.constants import Constants




class WhooshSearcher:
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
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
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
        Info = Activity.objects.all()
        Writer = self.Index.writer()
        for item in Info:
            if item.CanBeSearched == True:
            #print(item.Name)
                Writer.add_document(
                    path = "/" + str(item.ID),
                    content = item.Name
                )
        Writer.commit()

    def AddOneInfo(self, TheID, TheTitle):
        #print(1)
        Writer = self.Index.writer()
        Writer.add_document(
            path = "/" + str(TheID),
            content = TheTitle
            )
        Writer.commit()   

    def DeleteOneInfo(self, TheID):
        Writer = self.Index.writer()
        Writer.delete_by_term("path","/" + str(TheID))
        Writer.commit()  

    def UpdateOneInfo(self, TheID, NewContent):
        Writer = self.Index.writer()
        Writer.update_document(
            path = "/" + str(TheID),
            content = NewContent
            )
        Writer.commit()  

    def SearchInfo(self, TheKeyWord):
        Return = {}
        TheInfoList = []
        Searcher = self.Index.searcher()
        ParsedKeyword = self.AndParser.parse(TheKeyWord)
        print(str(ParsedKeyword)[1:-1].split()[::2])

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
            for i in range(len(TheOrResult)):
                hit = TheOrResult[i]
                TheInfo = {}
                TheNumberID = int(hit["path"][1:])
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
        print(TheUseString)
        ParsedKeyword = self.OrParser.parse(TheUseString)
        print(ParsedKeyword)
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
        print(Return)
        return Return

    def GetMostImportantWords(self, TheSentenceList):
        TheWordList = []
        
        for item in TheSentenceList:
            ParsedKeyword = self.AndParser.parse(item)
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
            TheResult["createTime"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(TheActivity.CreateTime))
            TheResult["start"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(TheActivity.StartTime))
            TheResult["end"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(TheActivity.EndTime))
            TheResult["signupBeginAt"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(TheActivity.SignUpStartTime))
            TheResult["signupStopAt"] = DataBaseGlobalFunctions.TimeStampToTimeString(int(TheActivity.SignUpEndTime))
            TheResult["minUser"] = int(TheActivity.MinUser)
            TheResult["maxUser"] = int(TheActivity.MaxUser)
            TheResult["curUser"] = int(TheActivity.CurrentUser)
            TheResult["type"] = TheActivity.Type
            TheResult["status"] = int(TheActivity.Status)
            if TheActivity.CanBeSearched != True:
                Success = False
        except:
            Success = False
        if Success:
            return TheResult
        else:
            return {}


