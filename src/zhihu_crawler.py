# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
import re
import math,time
from bson.objectid import ObjectId
from logger import Flogger,Slogger
from Model import ZhihuTask,ZhihuQA,Seeds



defalut_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    "Host": "www.zhihu.com",
    "X-Requested-With": "XMLHttpRequest"
}
ANSWER_MAX_LEN = 200  #回答长度限制
TOPIC_ID = 19776749   #根话题topic id

'''
知乎登录：可以修改config.json的账号信息，爬虫测试过可以不用登录
'''

SESSION = {}

def get_login_session():
    with open('../config.json') as f:
        config = json.load(f)
    session = requests.Session()
    login_result = session.post('http://www.zhihu.com/login/email', data=config, headers=defalut_headers).json()
    if login_result['r'] == 1:
        print('登录失败:', login_result['msg'])
        if login_result['errcode'] == 1991829:  # 输入验证码
            r = session.get('http://www.zhihu.com/captcha.gif')
            with open('captcha.gif', 'wb') as f:
                f.write(r.content)
            captcha = input('请输入验证码（当前目录下captcha.gif）：')
            config['captcha'] = captcha
            r = session.post('http://www.zhihu.com/login/email', data=config, headers=defalut_headers)
            login_result = r.json()
            if login_result['r'] == 1:
                print('登录失败:', login_result['msg'])
                exit(1)
            else:
                print('登录成功！')
    else:
        print('登录成功！')
    return session

# session = SESSION.get("session")
# if not session:
#     SESSION['session'] = get_login_session()
# session = SESSION['session']


def get_questions_list(task, sleep_sec=5, max_try=3):
    '''
        按照时间倒序获取某话题下的问题列表
        爬取的属性：ID，标题，来自的子话题，答案
        2016年2月后知乎不再提供“全部问题”页面
        2016年2月26日恢复了23日上线时去掉的「全部问题」列表
        参见 https://www.zhihu.com/question/40470324
    '''
    def _get_each_question(task):
        try:
            url = task['url']
            html = requests.get(url, headers=defalut_headers, timeout=60).text
            soup = BeautifulSoup(html, 'lxml')
            for div in soup.find_all('div', attrs={'itemprop': 'question'}):
                question = {}
                a = div.find('a', class_='question_link')
                question['url'] = 'http://www.zhihu.com' + a['href']
                question['question'] = a.text.strip()
                question['isExec'] = False
                subtopic = div.find('div', class_='subtopic')
                if subtopic:
                    question['topic'] = subtopic.a.text
                else:
                    question['topic'] = "unknown"
                question['extra_data'] = {}
                '''
                需要添加功能：将question存入任务队列，并输出success到任务队列success log
                '''
#                 print(question)#debug
                ZhihuTask(question).save()
                Seeds().getConnection().update({'_id':ObjectId(task['_id'])},{'$set':{'isExec':True}},False)
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


def get_question(task_dict):
    try:
        url = task_dict['url']
        question_id = int(url.split('/')[-1])
#         print("question_id:",question_id)
        response = requests.get(url, headers=defalut_headers, timeout=60)
        if response.status_code == 404:
            return None
        soup = BeautifulSoup(response.text, 'lxml')
        
        question = {}
        question['question'] = task_dict['question']
        question['topic'] = task_dict['topic']
        question["question_id"] = question_id
        block = soup.find('div', id='zh-question-detail')
        def _extract_answer(block):
            answer = block.find('div', class_='zm-editable-content').text.strip()
            return answer
    
        # 回答数目
        block = soup.find('h3', id='zh-question-answer-num')
        if block is None:
            if soup.find('span', class_='count') is not None:
                answers_count = 1
            else:
                answers_count = 0
        else:
            answers_count = int(block['data-num'])
        # 答案
        answers = []
        for block in soup.find_all('div', class_='zm-item-answer'):
            if block.find('div', class_='answer-status') is not None:
                continue  # 忽略建议修改的答案
            answer = _extract_answer(block)
            if len(answer) <= ANSWER_MAX_LEN:
                answers.append(answer)
            
        if answers_count > 50:
            xsrf_tag = soup.find('input', attrs={'name': '_xsrf'})
            if xsrf_tag is not None:
                _xsrf = xsrf_tag['value']
                headers = dict(defalut_headers)
                headers['Referer'] = url
                for i in range(1, int(math.ceil(answers_count/50))):  # more answers
                    data = {"_xsrf": _xsrf, "method": 'next', 'params':
                        '{"url_token": %d, "pagesize": 50, "offset": %d}' % (question_id, i*50)}
                    r = requests.post('http://www.zhihu.com/node/QuestionAnswerListV2',
                        headers=headers, data=data, timeout=60)
#                     print(r.url)
                    for block in r.json()['msg']:
                        div = BeautifulSoup(block, 'lxml').div
                        if div.find('div', class_='answer-status') is not None:
                            continue  # 忽略建议修改的答案
                        answer = _extract_answer(div)
                        if len(answer) <= ANSWER_MAX_LEN:
                            answers.append(answer)
        question['answer_list'] = answers
#         print(question)
        
        '''
        需要添加功能：将question存入结果数据库，并更新task的IsExeted字段为True;在结果log中打印success
        '''
        ZhihuQA(question).save()
        ZhihuTask().getConnection().update({'_id':ObjectId(task_dict['_id'])},{'$set':{'isExec':True}},False)
        Slogger.info("EXECUTE TASK SUCCESS:{}".format(url))
    except Exception:
        '''
        将fail的url打印到fail的结果log里面
        '''
        Flogger.info("EXECUTE TASK FAILED:{}".format(task_dict['url']))


if __name__=="__main__":
#     get_login_session()
#     get_question({'url': 'http://www.zhihu.com/question/47086984', 'question': '如何提高普通人的艺术修养，尤其是美术、音乐、时装之类的？电视里播的欣赏不了啊！', 'topic': '生活、艺术、文化与活动', 'extra_data': {}, 'isExec': False})
    pass

            
