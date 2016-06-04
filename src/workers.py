#coding=utf-8
import time,threading
from Model import ZhihuTask,ZhihuQA,Seeds
from zhihu_crawler import get_questions_list,get_question
import concurrent.futures
from logger import Flogger,Slogger 




class Worker(object):
    
    def __init__(self,worker_method,work_source):
        self._worker_method = worker_method
        self._work_source = work_source
        
    def work(self):
        while True:
            task = self._work_source().getConnection().find_one({'isExec': False}) #根据条件查询posts中数据
#             print(task)
            if task:
                self._worker_method(task)
                time.sleep(5)
            else:
                Slogger.info("NO WORK TO DO,SLEEP...")
                time.sleep(60)
        


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
    listWorker.work()
#     taskWorker.work()
#     taskCreateWorker()   
#     taskExecWorker()  
