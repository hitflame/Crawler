#coding=utf-8
import time,threading
from Model import XiangrikuiQuestionList,XiangrikuiQuestionPage,XiangrikuiSeeds
from xiangrikui_crawler import get_question_list,get_question_page
import concurrent.futures
from logger import Slogger 
import random


class Worker(object):
    
    def __init__(self,worker_method,work_source):
        self._worker_method = worker_method
        self._work_source = work_source
        
    def work(self):
        while True:
            #随机取一个任务
            find_interator = self._work_source().getConnection().find({'isExec': False})
            task = find_interator.limit(-1).skip(random.randint(0,find_interator.count()-1)).next() 
#             print(task)
            if task:
                self._worker_method(task)
                time.sleep(random.randint(1,10))
            else:
                Slogger.info("NO WORK TO DO,SLEEP...")
                time.sleep(10)
        


class ListExecWorker(Worker):
    pass

class TaskExecWorker(Worker):
    pass

taskWorker = TaskExecWorker(get_question_page,XiangrikuiQuestionList)
listWorker = ListExecWorker(get_question_list,XiangrikuiSeeds)

"https://www.zhihu.com/topic/19776749/questions?page=2"

def CreateWorker():
    for page in range(1,20502):#20502
        XiangrikuiSeeds({
               'url':"http://wenba.xiangrikui.com/wenda/"+str(page)+".html",
               'isExec':False
               }).save()
#        print(page)
 
        
        
if __name__=="__main__":  
#     CreateWorker()
#     listWorker.work()
    taskWorker.work()
