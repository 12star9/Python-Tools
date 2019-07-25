# -*- coding: utf-8 -*-
import os
import subprocess
from biplist import *





class AppCheckSystem(object):
    
    def __init__(self,app_path):
        self.app_path = app_path
        self.machFilePath=os.path.join(self.app_path,'project_test')

    #找到所有的app-icon图片列表
    def get_all_img_files(self):
      dir=self.app_path
      files_ = []
      list = os.listdir(dir)
      for i in range(0, len(list)):
        path = os.path.join(dir, list[i])
        if os.path.isdir(path):
          print '只做一层文件夹层次判断'
          continue
        if os.path.isfile(path):
          if path.endswith('png') or path.endswith('jpg') or path.endswith('jpeg'):
            files_.append(path)
      return files_

    #检查Appicon是否满足要求
    def check_AppIcon_Requirements(self):
      self.checkfile=os.path.join(self.app_path,'Info.plist')
      try:
        list=readPlist(self.checkfile)
      except Exception, e:
        print "Not a plist:", e

      supportedPlatform= list['CFBundleSupportedPlatforms'][0]
      warning_str_result=''
      #先判断图片是否包含完整
      check_iphone_completed=False
      check_iphone_appicon_list=[]
      check_ipad_completed=False
      check_ipad_appicon_list=[]
      if supportedPlatform=='iPhoneOS':
        if 1 in list['UIDeviceFamily']:
          print 'iphone'
          if list.has_key('CFBundleIcons'):
            CFBundleIcons=list['CFBundleIcons']
            if CFBundleIcons.has_key('CFBundlePrimaryIcon'):
              CFBundlePrimaryIcon=CFBundleIcons['CFBundlePrimaryIcon']
              if CFBundlePrimaryIcon.has_key('CFBundleIconName'):
                CFBundleIconFilesList=CFBundlePrimaryIcon['CFBundleIconFiles']
                check_iphone_appicon_list=CFBundleIconFilesList
                if len(CFBundleIconFilesList)>=4:
                  
                  check_iphone_completed=True
        if 2 in list['UIDeviceFamily']:
          print 'ipad'
          if list.has_key('CFBundleIcons~ipad'):
            CFBundleIcons=list['CFBundleIcons~ipad']
            if CFBundleIcons.has_key('CFBundlePrimaryIcon'):
              CFBundlePrimaryIcon=CFBundleIcons['CFBundlePrimaryIcon']
              if CFBundlePrimaryIcon.has_key('CFBundleIconName'):
                CFBundleIconFilesList=CFBundlePrimaryIcon['CFBundleIconFiles']
                check_ipad_appicon_list=CFBundleIconFilesList
                if len(CFBundleIconFilesList)>=4:
                  
                  check_ipad_completed=True
      #再来判断包体内部是否有对应的图片,列出所有图片看有没有包含
      img_list=self.get_all_img_files()
      #iphone
      iphone_img_result={}
      for iphone_icon in check_iphone_appicon_list:
        for img_temp in img_list:
          #匹配图片名?
          if iphone_icon in img_temp:
            iphone_img_result['%s'%(iphone_icon)]=True
            break
          else:
            iphone_img_result['%s'%(iphone_icon)]=False
            continue
      #ipad
      ipad_img_result={}
      for ipad_icon in check_ipad_appicon_list:
        for img_temp in img_list:
          #匹配图片名?
          if ipad_icon in img_temp:
            ipad_img_result['%s'%(ipad_icon)]=True
            break
          else:
            ipad_img_result['%s'%(ipad_icon)]=False
            continue


      #判断尺寸是否满足要求
      
      pass

    #检查可执行文件的__TEXT段大小是否满足大小要求
    def check_MachO_File(self,ios_version):
      process=subprocess.Popen('size %s'%(self.machFilePath),shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
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

appCheckSystem=AppCheckSystem('./project_test.app')
appCheckSystem.check_AppIcon_Requirements()
# appCheckSystem.check_MachO_File=check_MachO_File(6)
# if check_MachO_File==False:
#   print '检查不通过!'
# else:
#   print '检查通过'