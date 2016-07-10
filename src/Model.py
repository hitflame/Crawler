#coding=utf-8
__author__="mj"
from pymongo import MongoClient

MONGO_HOST = '100.81.181.119'
MONGO_PORT = 27017

DB_CONNECTION = {}

class DataBase(dict):
    
    field = []
    
    def __init__(self,dic={}):
        for k,v in dic.items():
            self[k] = v
    
    def getConnection(self):
        conection = DB_CONNECTION.get(self.__class__.__name__)
        if not conection:
            DB_CONNECTION[self.__class__.__name__] = MongoClient(host=MONGO_HOST, port=MONGO_PORT)[self.__class__.__base__.__name__][self.__class__.__name__]
            conection = DB_CONNECTION[self.__class__.__name__]
        return conection

    def __setitem__(self,key,val):
        if key not in self.__class__.field:
            return
        super(DataBase,self).__setitem__(key,val)
        
    def save(self):
        self.getConnection().insert_one(self)
        
    
"""
知乎全站QA存储
"""
class Seeds(DataBase):
    field = ["url","isExec"]
        
        
class ZhihuTask(DataBase):
    field = ["question",    #question of the post
             "topic",       #add topic field to indicate the question area
             "url",         #detail url for question
             "isExec",      #indicate weather this question has been crawled
             "extra_data"]  #some extra data may be used in crawler
    
    
class ZhihuQA(DataBase):
    field = ["question", #question of the post
             "question_id",   
             'topic',       #question area
             'answer_list', #replies for the question
             "extra_data"]  #some extra data may be used in crawler
"""
互动百科存储
"""
class BaikeFenLei(DataBase):
    field = ["name", "url", "isExec", "extra_data"]
    
class BaikeSecondClass(DataBase):
    field = ['name', 'url', 'isExec', 'extra_data']
    
    def getConnection(self, unique_index = "url"):
        conection = DB_CONNECTION.get(self.__class__.__name__)
        if not conection:
            DB_CONNECTION[self.__class__.__name__] = MongoClient(host=MONGO_HOST, port=MONGO_PORT)[self.__class__.__base__.__name__][self.__class__.__name__]
            conection = DB_CONNECTION[self.__class__.__name__]
            conection.ensureIndex({unique_index:1},{"unique":True})
        return conection

"""
知乎保险版块存储
"""        
class ZhihuInsuranceSeeds(DataBase):
    field = ["url","isExec"]
    
class ZhihuInsuranceQuestion(DataBase):
    field = ["question",    #question of the post
             "url",         #detail url for question
             "isExec",      #indicate weather this question has been crawled
             "extra_data"]  #some extra data may be used in crawler
    
class ZhihuInsuranceQuestionPage(DataBase):
    field = ["question", #question of the post
             "question_id",   
             "html_page", #replies for the question
             "extra_data"]  #some extra data may be used in crawler
             
"""
慧择问答版块版块存储
"""
class HuizheFAQSeeds(DataBase):
    field = ["url","isExec"]
    
class HuizheFAQ(DataBase):
    field = ["question",    #question of the post
             "url",         #detail url for question
             "isExec",      #indicate weather this question has been crawled
             "extra_data"]  #some extra data may be used in crawler

class HuizheFAQQuestionPage(DataBase):
    field = ["question", #question of the post
             "html_page", #replies for the question
             "extra_data"]  #some extra data may be used in crawler
    
"""
向日葵问答数据存储
"""
class XiangrikuiSeeds(DataBase):
    field = ["url","isExec"]
    
class XiangrikuiQuestionList(DataBase):
    field = ["question",    #question of the post
             "url",         #detail url for question
             "isExec",      #indicate weather this question has been crawled
             "extra_data"]  #some extra data may be used in crawler
             
class XiangrikuiQuestionPage(DataBase):
    field = ["question", #question of the post
             "html_page", #replies for the question
             "extra_data"]  #some extra data may be used in crawler
    
    
if __name__=="__main__":
#    ZhihuQA({'question':1,'topic':2,'answer_list':3}).save()
#     ZhihuTask({'question':1,'topic':2,'url':3,'isExec':4}).save()
    ZhihuInsuranceSeeds({'url':3,'isExec':4}).save()
    ZhihuInsuranceQuestion({'question':1,'extra_data':{},'url':3,'isExec':4}).save()
    ZhihuInsuranceQuestionPage({'question':1,'extra_data':{},'question_id':3,'html_page':4}).save()
    
    