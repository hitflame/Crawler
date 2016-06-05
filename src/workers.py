#coding=utf-8
import time,threading
from Model import ZhihuTask,ZhihuQA,Seeds
from zhihu_crawler import get_questions_list,get_question
import concurrent.futures
from logger import Flogger,Slogger 
import random




class Worker(object):
    
    def __init__(self,worker_method,work_source):
        self._worker_method = worker_method
        self._work_source = work_source
        
    def work(self):
        while True:
            #随机取一个任务
            task = self._work_source().getConnection().find({'isExec': False}).limit(1000).skip(random.randint(1,998)).limit(1).next() 
#             print(task)
            if task:
                self._worker_method(task)
                time.sleep(3)
            else:
                Slogger.info("NO WORK TO DO,SLEEP...")
                time.sleep(10)
        


class ListExecWorker(Worker):
    pass

class TaskExecWorker(Worker):
    pass

taskWorker = TaskExecWorker(get_question,ZhihuTask)
listWorker = ListExecWorker(get_questions_list,Seeds)



"https://www.zhihu.com/topic/19776749/questions?page=2"

def CreateWorker():
    for page in range(1,193823):#193823
        Seeds({
               'url':"https://www.zhihu.com/topic/19776749/questions?page="+str(page),
               'isExec':False
               }).save()
        print(page)
 
        
        
if __name__=="__main__":  
#     CreateWorker()
#     listWorker.work()
    taskWorker.work()
