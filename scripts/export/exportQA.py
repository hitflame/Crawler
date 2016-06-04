#coding=utf-8
from pymongo import MongoClient
from src.Model import ZhihuTask,ZhihuQA
import random


def exportQA():
    write_list= []
    for x in ZhihuQA().getConnection().find({}):
        question = x['question']
        answers = x['answer_list']
        if len(question)>20:
            continue
        for  answer in answers:
            if len(answer)>20:
                continue
            c = question+u'\t'+answer+u"\n"
            write_list.append(c)
    with open(r'Zhihu_all.txt','a+',encoding='utf-8') as f:
        f.writelines(write_list)

    

def exportQ():
    write_list= []
    for x in ZhihuTask().getConnection().distinct('question'):
        if len(x)<=20:
            write_list.append(x+'\n')
    open('Zhihu_question.txt','a+',encoding='utf-8').writelines(write_list)          
              
                
def shuffleQA():
    with open(r'C:\Users\guoqingpei\douban_abc_ALL_.txt','w+',encoding='utf-8') as f:
        lines = open(r'C:\Users\guoqingpei\douban_all.txt','r',encoding='utf-8').readlines()
        random.shuffle(lines)
        f.writelines(lines)


if __name__=="__main__":
#     exportA()
#     exportQA()
    exportQ()