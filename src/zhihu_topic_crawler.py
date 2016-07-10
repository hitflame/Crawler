# -*- coding: utf-8 -*-
"""
Created on Thu Jul 07 20:03:13 2016

@author: wenqiang.zwq
"""
import requests
from bs4 import BeautifulSoup
from Model import ZhihuInsuranceQuestion,ZhihuInsuranceSeeds,ZhihuInsuranceQuestionPage
from logger import Flogger,Slogger
from bson.objectid import ObjectId
import random
import time,math
import codecs

defalut_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    "Host": "www.zhihu.com",
    "X-Requested-With": "XMLHttpRequest"
}

AGENT_LIST =[line.strip() for line in  codecs.open(r"../agentlist",encoding='utf-8')]

class zhihu_topic_crawler(object):
    def __init__(self, topic_id = 19562045):
        self.topic_id = topic_id
            
    def get_question_list(self, task, sleep_sec=5, max_try=3):
        def _get_each_question(task):
            try:
                url = task['url']
                defalut_headers["User-Agent"] = random.choice(AGENT_LIST)
                html = requests.get(url, headers=defalut_headers, timeout=60).text
                soup = BeautifulSoup(html, 'lxml')
                for div in soup.find_all('div', attrs={'itemprop': 'question'}):
                    question = {}
                    a = div.find('a', class_='question_link')
                    question['url'] = 'http://www.zhihu.com' + a['href']
                    question['question'] = a.text.strip()
                    if int(div.find('meta', attrs={'itemprop': 'answerCount'})['content']) > 0:
                        question['isExec'] = False
                    else:
                        question['isExec'] = True
           
                    question['extra_data'] = {}
                    '''
                    需要添加功能：将question存入任务队列，并输出success到任务队列success log
                    '''
#                 print(question)#debug
                    ZhihuInsuranceQuestion(question).save()
                    ZhihuInsuranceSeeds().getConnection().update({'_id':ObjectId(task['_id'])},{'$set':{'isExec':True}},False)
                    Slogger.info("GET TASK SUCCESS:{}".format(question['question']))
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
            '''
            修改: 将url 打印到任务fail log
            '''
            Flogger.info("GET TASK-LIST FAILED:{}".format(url))
#             print('error occurs in get_questions_list!')
        time.sleep(sleep_sec)
    
    def get_question_page(self,task_dict):
        try:
            url = task_dict['url']
            question_id = int(url.split('/')[-1])
    #         print("question_id:",question_id)
            
            defalut_headers["User-Agent"] = random.choice(AGENT_LIST)
            response = requests.get(url, headers=defalut_headers, timeout=60)
            if response.status_code == 404:
                return None
            soup = BeautifulSoup(response.text, 'lxml')
            question = {}
            question['question'] = task_dict['question']
            question["question_id"] = question_id
#            block = soup.find('div', id='zh-question-detail')
#            def _extract_answer(block):
#                answer = block.find('div', class_='zm-editable-content').text.strip()
#                return answer
        
            # 回答数目
            block = soup.find('h3', id='zh-question-answer-num')
            if block is None:
                if soup.find('span', class_='count') is not None:
                    answers_count = 1
                else:
                    answers_count = 0
            else:
                answers_count = int(block['data-num'])
#            # 答案
#            answers = []
#            for block in soup.find_all('div', class_='zm-item-answer'):
#                if block.find('div', class_='answer-status') is not None:
#                    continue  # 忽略建议修改的答案
#                answer = _extract_answer(block)
#                if len(answer) <= ANSWER_MAX_LEN:
#                    answers.append(answer)
            target_page = response.text
                
            if answers_count > 50:
                xsrf_tag = soup.find('input', attrs={'name': '_xsrf'})
                if xsrf_tag is not None:
                    _xsrf = xsrf_tag['value']
                    headers = dict(defalut_headers)
                    headers['Referer'] = url
                    headers["User-Agent"] = random.choice(AGENT_LIST)
                    for i in range(1, int(math.ceil(answers_count/50))):  # more answers
                        data = {"_xsrf": _xsrf, "method": 'next', 'params':
                            '{"url_token": %d, "pagesize": 50, "offset": %d}' % (question_id, i*50)}
                        r = requests.post('http://www.zhihu.com/node/QuestionAnswerListV2',
                            headers=headers, data=data, timeout=60)
    #                     print(r.url)
                        for block in r.json()['msg']:
                            target_page += block
            question['html_page'] = target_page
            question['extra_data'] = {}
    #         print(question)
            
            '''
            需要添加功能：将question存入结果数据库，并更新task的IsExeted字段为True;在结果log中打印success
            '''
            ZhihuInsuranceQuestionPage(question).save()
            ZhihuInsuranceQuestion().getConnection().update({'_id':ObjectId(task_dict['_id'])},{'$set':{'isExec':True}},False)
            Slogger.info("EXECUTE TASK SUCCESS:{}".format(url))
        except Exception:
            '''
            将fail的url打印到fail的结果log里面
            '''
            Flogger.info("EXECUTE TASK FAILED:{}".format(task_dict['url']))
            return None
            
            
if __name__=="__main__":
    zhihu_crawler = zhihu_topic_crawler()
#    task = {'url': "https://www.zhihu.com/topic/19562045/questions?page=1",'isExec': False}
#    zhihu_crawler.get_question_list(task)
    task_dict = {"question":"为什么大家对推迟退休年龄这么大意见？","url":"https://www.zhihu.com/question/21682734","isExec": False, "extra_data":{}}
    zhihu_crawler.get_question_page(task_dict)
        