#coding=utf-8
import time,threading
from Model import ZhihuTask,ZhihuQA
from zhihu_crawler import get_question,get_questions_list
import concurrent.futures
from logger import Flogger,Slogger 


def taskExecWorker():
    while True:
        task = ZhihuTask().getConnection().find_one({'isExec': False}) #根据条件查询posts中数据
        if task:
            get_question(task)
            time.sleep(5)
        else:
            Slogger.info("NO WORK TO DO,SLEEP...")
            time.sleep(60)

    
def taskCreateWorker():
    jobs = [(page,page+10000) for page in range(1,193820,10000)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        [executor.submit(get_questions_list,*job) for job in jobs]
        
        
if __name__=="__main__":  
    taskCreateWorker()   
#     taskExecWorker()  
