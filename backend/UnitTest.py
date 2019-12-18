'''
单元测试函数
因为所有“获取全部”的接口容易在前端手动测试，搜索推荐等接口不确定性强，不适合自动化测试
因此仅测试增加，修改和删除相关接口
因为条件过于复杂，仅做了部分等价类
'''

import requests
import socket
import time
import json
import unittest


class TestBackend(unittest.TestCase):
    
    def test_SQL(self):
        '''
        测试sql注入
        '''
        Url = "http://127.0.0.1:8082/userData?session=bbb"
        Insert = Url + "-0|"
        Return = requests.get(Insert)
        self.assertTrue(Return.status_code == 400)
        Insert = Url + "and 1=3"
        Return = requests.get(Insert)
        self.assertTrue(Return.status_code == 400)
        Insert = Url + " order by 4"
        Return = requests.get(Insert)
        self.assertTrue(Return.status_code == 400)
        Insert = Url + " order by 5"
        Return = requests.get(Insert)
        self.assertTrue(Return.status_code == 400)
        Insert = Url + " and 1=2 union select 1,2,3,4"
        Return = requests.get(Insert)
        self.assertTrue(Return.status_code == 400)
        Insert = Url + " and 1=2 union select 1,database(),3,4"
        Return = requests.get(Insert)
        self.assertTrue(Return.status_code == 400)
        Insert = Url + "and 1=2 union select 1,table_name,3,4 from information_schema.tables where table_schema='DataBase_user'"
        Return = requests.get(Insert)
        self.assertTrue(Return.status_code == 400)
        Insert = Url + "and 1=2 union select 1,table_name,3,4 from information_schema.tables where table_schema='models'"
        Return = requests.get(Insert)
        self.assertTrue(Return.status_code == 400)
    
    def test_AddActivity(self):
        '''
        描述：对添加活动的主题逻辑进行单元测试
        测试对象：时间合法性判定，人数合法性判定，活动类型合法性判定，活动状态合法性判定，高级报名合法性判定
        '''
        #Url = "http://127.0.0.1:8082/createActivity?session=bbb"
        Url = "http://thalu.starrah.cn/createActivity?session=aaa"
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":2, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 200)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["te,st"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":2, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Info["rules"]["ruleType"] = 3
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 07:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":2, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-08 09:00:00", "signupStopAt":"2020-02-08 10:00:00", "minUser":2, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-08 06:00:00", "signupStopAt":"2020-02-08 13:00:00", "minUser":2, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2019-12-08 08:00:00", "end":"2019-12-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2019-12-08 06:00:00", "signupStopAt":"2019-12-08 08:00:00", "minUser":2, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":1, "maxUser": 2, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":5, "maxUser": 4, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":0, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":2,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":0, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":3,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":0, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":4,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":0, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":4,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士","department":"计算机系"}],
        "reject":[{"department":"电子系","enrollmentType":"博士"}]}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":2, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED"}
        Info["rules"] = Rule
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 200)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},\
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士"}],\
        "reject":[{"department":"电子系","enrollmentType":"博士"}]}
        Info["rules"] = Rule
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},\
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士","department":"计算机系"}],\
        "reject":[{"department":"软件学院"}]}
        Info["rules"] = Rule
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士","department":"计算机系"}],\
        "reject":[{"minEnrollmentYear":2019, "maxEnrollmentYear":2020}]}
        Info["rules"] = Rule
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},\
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士","department":"计算机系"}],\
        "reject":[{"maxEnrollmentYear":2020}]}
        Info["rules"] = Rule
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},\
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],\
        "reject":[{"maxEnrollmentYear":2016}]}
        Info["rules"] = Rule
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 200)
    
    def test_ChangeActivity(self):
        '''
        描述：测试修改活动
        测试对象：时间合法性判定，人数合法性判定，活动类型合法性判定，活动状态合法性判定，高级报名合法性判定
        '''
        Url = "http://127.0.0.1:8082/modifyActivity?session=bbb"
        Rule = {"ruleType":0}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":2, "maxUser": 5, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED", "rules": Rule}
        Return = requests.post("http://127.0.0.1:8082/createActivity?session=bbb", data = json.dumps(Info))
        ID = json.loads(Return.text)["activityId"]
        print(ID)
        Rule = {"ruleType":1}
        Info = {"id":ID, "start":"2020-02-08 13:00:00"}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"id":ID, "end":"2020-02-08 07:00:00"}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"id":ID, "signupBeginAt":"2020-02-08 09:00:00"}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"id":ID, "signupStopAt":"2020-02-08 13:00:00"}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1}
        Info = {"id":ID, "signupBeginAt":"2019-12-18 10:00:00", "signupStopAt":"2019-12-18 12:00:00", "start":"2019-12-18 14:00:00"}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 200)
        Rule = {"ruleType":1}
        Info = {"id":ID, "end":"2019-12-18 14:20:00"}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Info = {"id":ID, "minUser":6}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Info = {"id":ID, "statusGlobal":2}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Info = {"id":ID, "statusJoin":-1}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Info = {"id":ID, "statusCheck":-1}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Info = {"id":ID, "statusGlobal":1, "statusJoin":1,"statusCheck":1}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 200)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士","department":"计算机系"}],
        "reject":[{"department":"电子系","enrollmentType":"博士"}]}
        Info = {"id":ID, "rules":Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 200)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},\
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士"}],\
        "reject":[{"department":"电子系","enrollmentType":"博士"}]}
        Info = {"id":ID, "rules":Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},\
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士","department":"计算机系"}],\
        "reject":[{"department":"软件学院"}]}
        Info = {"id":ID, "rules":Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士","department":"计算机系"}],\
        "reject":[{"minEnrollmentYear":2019, "maxEnrollmentYear":2020}]}
        Info = {"id":ID, "rules":Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},\
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士","department":"计算机系"}],\
        "reject":[{"maxEnrollmentYear":2020}]}
        Info = {"id":ID, "rules":Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},\
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],\
        "reject":[{"maxEnrollmentYear":2016}]}
        Info = {"id":ID, "rules":Rule}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 200)
        Info = {"id":ID, "rules":{"ruleType":0}}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 200)
        requests.post("http://127.0.0.1:8082/joinActivity?session=ccc&activityId=" + str(ID), data = {})
        requests.post("http://127.0.0.1:8082/joinActivity?session=ddd&activityId=" + str(ID), data = {})
        requests.post("http://127.0.0.1:8082/joinActivity?session=eee&activityId=" + str(ID), data = {})
        Info = {"id":ID, "maxUser":3}
        Return = requests.post(Url, data = json.dumps(Info))
        self.assertTrue(Return.status_code == 400)
    
    def test_JoinActivity(self):
        '''
        描述：测试报名活动
        测试对象：重复报名，对不在报名状态的活动报名，对人满的活动报名，高级报名
        '''
        Rule = {"ruleType":1, "accept":[{"enrollmentType":"本科","minEnrollmentYear":2017,"maxEnrollmentYear":2019, "department":"软件学院"},
        {"enrollmentType":"硕士","minEnrollmentYear":2021,"maxEnrollmentYear":2023, "department":"软件学院"}],"needAudit":[{"enrollmentType":"硕士","department":"计算机系"}],
        "reject":[{"department":"电子系","enrollmentType":"博士"}]}
        Info = {"name":"test activity", "place":"test place", "start":"2020-02-08 08:00:00", "end":"2020-02-08 12:00:00","tags":["test"],\
        "signupBeginAt":"2020-02-02 06:00:00", "signupStopAt":"2020-02-07 08:00:00", "minUser":2, "maxUser": 3, "type":"个人活动-聚餐",\
        "statusGlobal":1,"statusJoin":0,"statusCheck":0,"canBeSearched":True,"description":"unit test","imageUrl":"UNDEFINED"}
        Info["rules"] = Rule
        Return = requests.post("http://127.0.0.1:8082/createActivity?session=bbb", data = json.dumps(Info))
        ID = json.loads(Return.text)["activityId"]
        Data = {"reason":"a"}
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=aaa", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 400)
        Data = {"id":ID,"statusJoin":2}
        requests.post("http://127.0.0.1:8082/modifyActivity?session=bbb", data = json.dumps(Data))
        Data = {"reason":"a"}
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=aaa", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 400)
        Data = {"id":ID,"statusJoin":1}
        requests.post("http://127.0.0.1:8082/modifyActivity?session=bbb", data = json.dumps(Data))
        Data = {"reason":"a"}
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=aaa", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 200)
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=bbb", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 400)
        Data = {"reason":""}
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=ddd", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 400)
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=ddd", data = json.dumps({}))
        self.assertTrue(Return.status_code == 400)
        Data = {"reason":"a"}
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=ddd", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 200)
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=eee", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 400)
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=ccc", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 200)
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=qwq", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 200)
        Return = requests.post("http://127.0.0.1:8082/joinActivity?activityId="+str(ID)+"&session=fff", data = json.dumps(Data))
        self.assertTrue(Return.status_code == 400)
    
if __name__ == '__main__':
    unittest.main()
