# -*- coding: utf-8 -*-
"""
echo "花呗无法还款" | ./bin/AliTokenizer -conf ./conf/AliTokenizer.conf -ws TAOBAO_CHN -outtype 2 | python ws_result_arrange.py 

"""

import os
import sys


CMD = "echo {} | ./bin/AliTokenizer -conf ./conf/AliTokenizer.conf -ws TAOBAO_CHN -outtype 2 | python ws_result_arrange.py "

def handle(inputFile,outputFile):
	write_str = []
	with open(inputFile,'r',encoding='utf-8') as f: 
		for line in f:
			try:
				q,a = line.strip().split('\t')
				if q=="" or a=="":
					continue
				cut_q,cut_a = os.popen(CMD.format(q)).read(),os.popen(CMD.format(a)).read()
				write_str.append(cut_q.strip()+"\t"+cut_a.strip()+"\n")
			except:
				continue
	open(outputFile,"w+",encoding='utf-8').writelines(write_str)


if __name__ == "__main__":
	handle(*sys.argv[1:3])
    
