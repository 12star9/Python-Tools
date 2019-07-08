# -*- coding: utf-8 -*-
import os
import subprocess
from biplist import *


#检查Appicon是否满足要求
def check_AppIcon_Requirements(checkfile):
  try:
    list=biplist.readPlist(checkfile)
  except Exception, e:
	  print "Not a plist:", e
  #先判断图片是否包含完整

  #再来判断包体内部是否有对应的图片 

  #判断尺寸是否满足要求
  pass

#检查可执行文件的__TEXT段大小是否满足大小要求
def check_MachO_File(machFilePath,ios_version):

  process=subprocess.Popen('size %s'%(machFilePath),shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  (stdoutdata, stderrdata) = process.communicate()
  print stdoutdata
  result=stdoutdata.split('\n')
  size_result=0
  List_size_result=[]
  for temp_result in range(1,len(result)):
    result2=result[temp_result].split('\t')
    for temp_str in result2:
      if 'arm' in temp_str:
        size_result+=int(result2[0])
        List_size_result.append(int(result2[0]))
        pass
  return_result=True
  if ios_version>=9:
    if (size_result/1024/1024)>500:
      return_result=False
      pass
    pass
  elif ios_version>=7 and ios_version<=8:
    for temp_size in List_size_result:
      if (temp_size/1024/1024)>60:
        return_result=False
        break
      pass
    pass
  
  elif ios_version<7:
    if (size_result/1024/1024)>80:
      return_result=False
      pass
  return return_result
  pass


check_AppIcon_Requirements('./Info2.plist')
# check_MachO_File=check_MachO_File('/Users/star.liao/Downloads/Payload/cn.app/cn',6)
# if check_MachO_File==False:
#   print '检查不通过!'
# else:
#   print '检查通过'