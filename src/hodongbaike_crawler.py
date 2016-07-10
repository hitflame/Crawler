# -*- coding: utf-8 -*-
"""
Created on Mon Jul 04 19:11:36 2016

@author: wenqiang.zwq
"""

import requests
from bs4 import BeautifulSoup
from Model import BaikeFenLei, BaikeSecondClass
from logger import Flogger,Slogger

class hudongbaike(object):
    def __init__(self, root_url = r'http://www.baike.com/fenlei/?prd=shouye_fenleidaohang'):
        self.root_url = root_url
    
    def get_all_first_class_url(self):
        response = requests.get(self.root_url)
        soup = BeautifulSoup(response.content, 'lxml')
        for div in soup.find_all('div', class_ = 'td w-578'):
            for a in div.find_all('a'):
                fenLei = {}
                if a.has_attr('href'):
                    if a.text == "老北京百科":
                        fenLei["name"] = "老北京"
                    else:
                        fenLei["name"] = a.text
                    
                    fenLei["url"] = "http://fenlei.baike.com/"+fenLei["name"]+"/list/"
                    fenLei['isExec'] = False
                    fenLei['extra_data'] = {}
                    BaikeFenLei(fenLei).save()
                    
    def get_second_class_url(self, class_url = 'http://fenlei.baike.com/%E5%9C%B0%E8%B4%A8%E5%AD%A6%E5%AE%B6/list/'):
        
        response = requests.get(class_url)
        soup = BeautifulSoup(response.content, 'lxml')
        for a in soup.find_all("a", target = "_blank"):
            fenLei = {}
            if a.has_attr('href'):
                fenLei['name'] = a.text
                fenLei['url'] = a['href']
                fenLei['isExec'] = False
                fenLei['extra_data'] = {}
                try:
                    BaikeSecondClass(fenLei).save()
                except:
                    continue
                
    def get_all_second_class_url(self):
        connection = BaikeFenLei({}).getConnection()
        for cur_first_class in connection.find():
            self.get_second_class_url(class_url = cur_first_class[u'url'])
            
            
if __name__ == "__main__":
    hudongbaike = hudongbaike()
    hudongbaike.get_all_second_class_url()
#    hudongbaike.get_all_first_class()