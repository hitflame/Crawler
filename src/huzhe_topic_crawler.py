# -*- coding: utf-8 -*-
"""
Created on Thu Jul 07 20:03:13 2016

@author: wenqiang.zwq
"""
import requests
from bs4 import BeautifulSoup
from Model import HuizheFAQ,HuizheFAQSeeds,HuizheFAQQuestionPage
from logger import Flogger,Slogger
from bson.objectid import ObjectId
import random
import time
import codecs

defalut_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    "Host": "xuexi.huize.com",
    "X-Requested-With": "XMLHttpRequest"
}

AGENT_LIST =[line.strip() for line in  codecs.open(r"../agentlist",encoding='utf-8')]

def get_question_list(task, sleep_sec=5, max_try=3):
    def _get_each_question(task):
        try:
            url = task['url']
            defalut_headers["User-Agent"] = random.choice(AGENT_LIST)
            html = requests.get(url, headers=defalut_headers, timeout=60).text
            soup = BeautifulSoup(html, 'lxml')
            
            question_tag_list = soup.find_all("a", class_ = "qas-r1 f14 lk-mt cur-pt")
            answer_tag_list = soup.find_all("a", class_ = "lk-f9")
            glance_tag_list = soup.find_all("i", class_ = "pl20 fc9")[::2]
            for cur_question_tag, cur_answer_tag, cur_glance_tag in zip(question_tag_list, answer_tag_list, glance_tag_list):
                question = {}
                question["extra_data"] = {}
                question["question"] = cur_question_tag.text
                question["url"] = "http://xuexi.huize.com" + cur_question_tag['href']
                question["extra_data"]["answer_count"] = int(cur_answer_tag.text[:-2]) #回答数目
                if question["extra_data"]["answer_count"]>0:
                    question['isExec'] = False
                else:
                    question['isExec'] = True
                question["extra_data"]["glance_count"] = int(cur_glance_tag.text[:-2]) #浏览数目
                HuizheFAQ(question).save()
                Slogger.info("GET TASK SUCCESS:{}".format(question['question']))
            HuizheFAQSeeds().getConnection().update({'_id':ObjectId(task['_id'])},{'$set':{'isExec':True}},False)
            return True
        except Exception:
            return False
        
    try_count = 0
    while not _get_each_question(task):
        if try_count > max_try:
            break
        else:
            try_count += 1
            time.sleep(sleep_sec)
            
    if try_count > max_try:
        url = task['url']
        Flogger.info("GET TASK-LIST FAILED:{}".format(url))
    time.sleep(sleep_sec)
    
def get_question_page(task_dict):
    try:
        url = task_dict['url']
        defalut_headers["User-Agent"] = random.choice(AGENT_LIST)
        response = requests.get(url, headers=defalut_headers, timeout=60)
        if response.status_code == 404:
            return None
        question = {}
        question['question'] = task_dict['question']
        question['html_page'] = response.text
        question['extra_data'] = {}
        HuizheFAQQuestionPage(question).save()
        HuizheFAQ().getConnection().update({'_id':ObjectId(task_dict['_id'])},{'$set':{'isExec':True}},False)
        Slogger.info("EXECUTE TASK SUCCESS:{}".format(url))
    except Exception:
        Flogger.info("EXECUTE TASK FAILED:{}".format(task_dict['url']))
        return None
        
if __name__=="__main__":
#    task = {'url': "http://xuexi.huize.com/insurancefaq/default-2-2-2.html",'isExec': False}
#    get_question_list(task)
    task_dict = {"question":"车险马上到期了，现在一直纠结买那家保险，平安和太平洋","url":"http://xuexi.huize.com/insurancefaq/detal-123765.html","isExec": False, "extra_data":{}}
    get_question_page(task_dict)
        