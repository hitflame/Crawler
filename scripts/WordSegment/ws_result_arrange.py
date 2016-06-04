import sys
import os

#stopwords = {}
#for line in open(sys.argv[1]):
#    stopwords[line.strip()] = ""

res = ""
count = 0
for line in sys.stdin:
	if line.strip().startswith("token"):
		if res == "":
			#print res.strip()
			continue
		print(res.strip())
		res = ""
		continue
	if line.strip() == "":
		continue
	Line = line.strip().split('\t')
	if Line[0] == "SEMANTIC|R_BASIC" and count != 0:
		count -= int(Line[2])
		continue
	elif Line[0] == "SEMANTIC|R_BASIC" and count == 0:
		continue
	#if stopwords.has_key(Line[0]):
	#	continue
	if Line[1] == "SEMANTIC":
		if Line[5] != "NULL" and not Line[5].startswith("NR|NR"):
			res += Line[5]+" "
		else:
			res += Line[0]+" "
		count = int(Line[3])
		continue
	if count != 0 and (Line[1] == "SEMANTIC|R_BASIC" or Line[1] == "R_BASIC"):
		count -= int(Line[3])
		continue
	if count == 0 and Line[1] != "R_BASIC" and Line[1] != "R_EXTEND":
		if Line[5] != "NULL" and not Line[5].startswith("NR|NR"):
			res += Line[5] + " "
		else:
			res += Line[0] + " "
print(res.strip())