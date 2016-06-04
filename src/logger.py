#coding=utf8
import logging

#logger set
Slogger = logging.getLogger("success")
Flogger = logging.getLogger("failed")
#set loghandler  
StatusLog = logging.FileHandler("../log/StatusLog.txt")  
failedRecord = logging.FileHandler("../log/failedRecord.txt") 
Slogger.addHandler(StatusLog) 
Flogger.addHandler(failedRecord) 
#set formater   
formatter = logging.Formatter("%(asctime)s %(filename)s: %(message)s")
StatusLog.setFormatter(formatter) 
failedRecord.setFormatter(formatter) 
#set log level  
Slogger.setLevel(logging.INFO)
Flogger.setLevel(logging.INFO)