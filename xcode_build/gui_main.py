# -*- coding: utf-8 -*-
import subprocess
import re
import os
import Tkinter as tk
from Tkinter import *
from FileDialog import *
from pbxproj import *
import tkinter.filedialog
import tkinter.messagebox
from xcode_build_module import *
import sys
import thread
import time
import logging
import threading

reload(sys)
sys.setdefaultencoding('utf8')

import logging
from logging import handlers

current_build_count=0
mutex=threading.Lock()

class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='info',when='D',backCount=3,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)
if __name__ == '__main__':
    pass
    # log = Logger('all.log',level='debug')
    # log.logger.debug('debug')
    # log.logger.info('info')
    # log.logger.warning('警告')
    # log.logger.error('报错')
    # log.logger.critical('严重')
    # Logger('error.log', level='error').logger.error('error')

def find_signs_file():
    # process=subprocess.Popen('security login-keychain',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # (stdoutdata, stderrdata) = process.communicate()
    # result=process.stdout.readline()
    # signReturnCode = process.returncode
    process=subprocess.Popen('security find-identity -v -p codesigning ~/Library/Keychains/login.keychain-db',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (stdoutdata, stderrdata) = process.communicate()
    iPhoneList=[]
    iPhoneDeveloper_val='iPhone Developer:'
    iPhoneDistribution_val='iPhone Distribution:'
    result= re.findall(r'(?<=%s)(.*?)(?=")'%(iPhoneDeveloper_val),stdoutdata)
    for temp in result:
        iPhoneList.append(iPhoneDeveloper_val+temp)
    result= re.findall(r'(?<=%s)(.*?)(?=")'%(iPhoneDistribution_val),stdoutdata)
    for temp in result:
        iPhoneList.append(iPhoneDistribution_val+temp)
    return iPhoneList
    pass

class LayoutMainUI(object):
    def __init__(self):
        self.sign_list_data =find_signs_file()
        self.log = Logger('all.log',level='debug')
        self.gui_main()
        
        # log.logger.debug('debug')
        # log.logger.info('info')
        # log.logger.warning('警告')
        # log.logger.error('报错')
        # log.logger.critical('严重')
        # Logger('error.log', level='error').logger.error('error')
        pass

    def chooseXcodePathCallBack(self):
        file_path = tkinter.filedialog.askdirectory()
        self.xcode_display_text.set(file_path)
        self.xcode_path=file_path
        #默认输出包路径在母工程父路径，启用可读可写
        print os.path.dirname(self.xcode_path)
        os.system("chmod -R 777 %s"%(os.path.dirname(self.xcode_path)))
        pass

    def chooseTargetFile(self,file_extenstion):
        result= tkinter.filedialog.askopenfilename(title='选择打包需要的 .%s 文件'%(file_extenstion), filetypes=[('%s'%(file_extenstion.upper()),'*.%s'%(file_extenstion)), ('All Files', '*')])
        return result
        pass

    def generateExportInfoPlist(self):
        self.exportOptions_path=None
        base_exportOptions_name='exportOptions'
        if self.v.get()==0:
            base_exportOptions_name+='-dev'
        else:
            base_exportOptions_name+='-dis'
        if self.bitCodeValue==1:
            base_exportOptions_name+=''
        else:
            base_exportOptions_name+='-no-bitcode'
        self.exportOptions_path=os.path.join(os.getcwd(),base_exportOptions_name+'.plist')
        pass

    def buildXcodeProjectWithInfo(self,threadName,projectPath,project_name,build_config,sign_path,display_name,bundle_identifier,sdk_path=None):
        self.log.logger.debug('%s %s 开始打包 %s'%(threadName,projectPath,time.ctime(time.time())))
        xcode_build=XCodeBuild(projectPath, projectPath+"/%s/Info.plist"%(project_name),
        True,project_name,build_config,sign_path,self.mobileprovision_path,self.exportOptions_path)
        xcode_build.checkWorkSpace()
        xcode_build.allowFinder()
        xcode_build.allowKeychain()
        xcode_build.clearPbxproj()
        xcode_build.cleanPro()
        xcode_build.initProject()
        if sdk_path==None or 'origin' in sdk_path:
            xcode_build.updateAppDisplayName('project_test')
            xcode_build.updateAppBundleId('com.star.project_test')
        else:
            xcode_build.updateAppDisplayName(display_name)
            xcode_build.updateAppBundleId(bundle_identifier)
        xcode_build.updateMobileProvisionProfile(self.mobileprovision_path)
        xcode_build.updateExportOptionPlistData()
        if not sdk_path==None and not 'origin' in sdk_path:
            xcode_build.updateProjectSetsForSDK(sdk_path)
        code,resultMsg=xcode_build.buildApp()
        targetStr=''
        if code==0:
            self.log.logger.debug('%s %s 打包成功 %s'%(threadName,projectPath,time.ctime(time.time())))
            lastStr=self.result_display_msg.get()
            currentStr='\n打包路径在:%s'%(resultMsg)
            targetStr=u'%s%s'%(lastStr,currentStr)
             #     # #找到.ipa文件并安装
            #     # ipa_list= self.get_all_ipa_files(resultMsg)
            #     # for ipa_temp in ipa_list:
            #     #     os.system('ideviceinstaller -i %s'%(ipa_temp))
            #     # #删除安装好的ipa目录
            #     # shutil.rmtree(resultMsg)
            pass
        else:
            self.log.logger.debug('%s %s 打包失败 %s'%(threadName,projectPath,time.ctime(time.time())))     
            targetStr='%s %s 打包失败 %s'%(threadName,projectPath,time.ctime(time.time()))
        return targetStr
        # self.result_display_msg.set(targetStr)

    def buildAllTaskCallBack(self):
        projectPath=self.xcode_path
        if projectPath==None:
            tkinter.messagebox.showerror('打包错误提示','没有设置打包Xcode母工程!')
            return

        #TODO: 打包前检查所有的配置？
        #不需要勾选了，自动根据打包目标(AppStore,AdHoc等)生成对应的exportInfo.plist文件
        self.generateExportInfoPlist()
        build_config=None
        if len(self.build_config_list.curselection())>0:
            selections=self.build_config_list.curselection()[0]
            build_config = self.build_config_list.get(selections)
        sign_path=None
        for temp in range(0,self.sign_list.size()):
            if self.sign_list.selection_includes(temp)==1:
                sign_path = self.sign_list.get(temp)
                break
        if sign_path==None or build_config==None:
            tkinter.messagebox.showerror('打包错误提示','打包证书或Config没有设置!')
            return
        if self.mobileprovision_path==None:
            tkinter.messagebox.showerror('打包错误提示','.mobileprovision_profile没有设置!')
            return
        all_len=self.target_build_list.size()
        list=[]
        for temp in range(0,all_len):
            list.append(self.target_build_list.get(temp))
        if len(list)==0:
            tkinter.messagebox.showwarning('⚠️','没有引入SDK打包!')
        project_name= os.path.split(projectPath)[-1]


        #拷贝母包工程配置和Info.plist,防止母包工程被修改
        pbxproj=os.getcwd()+'/project_test'+'/project_test.xcodeproj/project.pbxproj'
        infoPlistPath=os.getcwd()+'/project_test'+'/project_test/Info.plist'
        try:
            src_path=os.path.join(os.getcwd(),'project.pbxproj')
            infPlist_Src_Path=os.path.join(os.getcwd(),'Info.plist')
            shutil.copy(src_path,pbxproj)
            shutil.copy(infPlist_Src_Path,infoPlistPath)
        except Exception,e:
            print e 

        #1.这里目前遍历以此打包
        # list.append('origin')
        # index_val=0
        # self.currentTime=time.time()
        # for sdk_path in list:
        #     targetStr=self.buildXcodeProjectWithInfo(u'current_thread',projectPath,project_name,build_config,sign_path,'project_test_%s'%(index_val),'com.star.project_test_%s'%(index_val),sdk_path)
        #     self.result_display_msg.set(targetStr)
        #     index_val=index_val+1
        # splitTimes= (time.time()-self.currentTime)
        # self.log.logger.debug('耗时:%s'%(splitTimes))
        # return

        #2.开启两个线程，同时打包
        self.currentTime=time.time()
        try:
            #因为是多线程，需要先把数据拷贝到新位置，每条线程只操作各自的数据
            current_work_path=os.getcwd()
            projecttest_path=projectPath
            projectPathList=[projecttest_path]
            for index in range(0,len(list)):
                resultPath=projecttest_path+"/../backup%s"%(index)
                try:
                    shutil.rmtree(resultPath)
                except BaseException:
                    pass
                    # print 'error!'
                pass
            for index in range(0,len(list)):
                resultPath=projecttest_path+"/../backup%s"%(index)
                try:
                    shutil.copytree(projecttest_path, resultPath)
                except BaseException:
                    pass
                    # print 'error.'
                finally:
                    projectPathList.append(resultPath)
                pass
            index_val=0
            all_list_len=len(list)
            build2_len=None
            build3_len=None
            min_len=2
            #如果sdk打包任务大于min_len个，以min_len个sdk打包任务切分为一个线程任务，剩下的sdk任务为另一个线程任务
            if all_list_len>min_len or all_list_len==min_len:
                build2_len=min_len
                build3_len=all_list_len-min_len
            else:
                build2_len=min_len-(min_len-1)
                min_len=(min_len-1)
                build3_len=all_list_len-build2_len

            # projectPathList包含母包在内，总共len(list）+1次打包任务
            #线程sdk打包任务
            def commonBuildTask(min_len,build_length,threadName):
                if build_length==0:
                    self.log.logger.debug('%s,该线程没有打包任务，退出,%s'%(threadName,time.ctime(time.time())))
                    return
                global current_build_count
                index_val=min_len+1
                self.log.logger.debug('%s,%s'%(threadName,time.ctime(time.time())))
                for sdk_index in range(min_len,min_len+build_length):
                    projectPath=projectPathList[index_val]
                    targetStr=self.buildXcodeProjectWithInfo(threadName,projectPath,project_name,build_config,sign_path,'project_test_%s'%(index_val),'com.star.project_test_%s'%(index_val),list[sdk_index])
                    self.result_display_msg.set(targetStr)
                    if mutex.acquire():
                        current_build_count+=1
                        if current_build_count>=(len(list)+1):
                            splitTimes= (time.time()-self.currentTime)
                            self.log.logger.debug('耗时:%s'%(splitTimes))
                            mutex.release()
                            break
                        mutex.release()
                    index_val+=1

            #这里打包母包
            def buildTask1(threadName,testPara):
                global current_build_count
                self.log.logger.debug('%s,%s'%(threadName,time.ctime(time.time())))
                projectPath=projectPathList[0]
                targetStr=self.buildXcodeProjectWithInfo(threadName,projectPath,project_name,build_config,sign_path,'project_test','com.star.project_test',None)
                self.result_display_msg.set(targetStr)
                if mutex.acquire():
                    current_build_count+=1
                    if current_build_count>=(len(list)+1):
                        splitTimes= (time.time()-self.currentTime)
                        self.log.logger.debug('耗时:%s'%(splitTimes))
                    mutex.release()
                
            #min_len个sdk打包任务
            def buildTask2(threadName,testPara):
                commonBuildTask(0,build2_len,threadName)
            #剩下的sdk任务
            def buildTask3(threadName,testPara):
                commonBuildTask(min_len,build3_len,threadName)
            thread.start_new_thread(buildTask1,('Thread-1-Parent-build',1,))
            thread.start_new_thread(buildTask2,('Thread-2-build',2,))
            thread.start_new_thread(buildTask3,('Thread-3-build',3,))
        except:
            print 'thread error.'
        pass

    def get_all_ipa_files(self,dir):
        files_ = []
        list = os.listdir(dir)
        for i in range(0, len(list)):
            path = os.path.join(dir, list[i])
            if os.path.isdir(path):               
                if path.endswith('ipa'):
                    files_.append(path)
                    continue
                else:
                    files_.extend(self.get_all_ipa_files(path))
            if os.path.isfile(path) and path.endswith('ipa'):
                files_.append(path)
        return files_  
                                            
    def clickCallBack(self):
        #选择SDK
        sdk_path = tkinter.filedialog.askdirectory()
        temppath=sdk_path
        self.update_list_task(temppath)
        pass

    def chooseMobileProsionProfileCallBack(self):
        self.mobileprovision_path= self.chooseTargetFile('mobileprovision')
        #先用Xcode打开一次或拷贝到文件夹，让XCode命令行工具可以查找到，不然打包会失败
        self.mobileprosion_display_text.set(self.mobileprovision_path)
        pass

    def chooseExportOptionsInfoFileCallBack(self):
        self.exportOptions_path= self.chooseTargetFile('plist')
        self.plist_display_text.set(self.exportOptions_path)
        pass

    def exportIpaConfigFrame(self):
        myWindow=self.root
        frame_l= Frame(myWindow)
        frame_r=Frame(myWindow)
        frameRoot=Frame(myWindow,width=200,height=2)

        self.bitCodeValue=tk.IntVar()
        bitCodeText=tk.StringVar()
        bitCodeText.set('是否设置Bitcode')
        self.c1=tk.Checkbutton(frameRoot,textvariable=bitCodeText,variable=self.bitCodeValue,onvalue=1,offvalue=0,width=20,command=self.callCheckBtn1)
        self.c1.deselect()
        self.symbolValue=tk.IntVar()
        symbolText=tk.StringVar()
        symbolText.set('是否启用Symbol')
        self.c2=tk.Checkbutton(frameRoot,textvariable=symbolText,variable=self.symbolValue,onvalue=1,offvalue=0,width=20,command=self.callCheckBtn2)
        self.c2.select()
        self.c1.pack(side=TOP)
        self.c2.pack(side=TOP)
        frameRoot.pack(side=TOP)

    def callCheckBtn1(self):
        val=self.bitCodeValue.get()
        print val
        pass
    def callCheckBtn2(self):
        val=self.symbolValue.get()
        print val
        pass
    
    def exportIpaTarget(self):
        frameRoot=Frame(self.root,width=200,height=2)
        self.v=tk.IntVar()
        self.v.set(0)
        
        targetList=[('开发',0),('AppStore',1)]
        for text,value in targetList:
            # v=tk.IntVar()
            tk.Radiobutton(frameRoot,text=text,value=value,command=self.callBB(self.v),variable=self.v).pack(side=LEFT)
        pass
        frameRoot.pack(side=TOP)


    def callBB(self,v):
        print '勾选: %s'%(self.v.get())
        pass
    def layout_main_ui(self):
        width_value=800
        height_value=2
        self.choose_xcode_path_btn=tk.Button(self.root, text="选择Xcode母工程路径",command=self.chooseXcodePathCallBack,height=height_value,width=width_value)
        self.choose_xcode_path_btn.pack()

        self.xcode_display_text=tk.StringVar()
        self.xcode_display_text.set('')
        self.xcode_path_text=tk.Label(self.root,height=2,textvariable=self.xcode_display_text,width=width_value)
        self.xcode_path_text.pack()

        self.mobileprosion_display_text=tk.StringVar()
        self.mobileprosion_display_text.set('')
        self.plist_display_text=tk.StringVar()
        self.plist_display_text.set('')
        self.mobileprosion_path_text=tk.Label(self.root,height=2,textvariable=self.mobileprosion_display_text)
        self.plist_path_text=tk.Label(self.root,height=2,textvariable=self.plist_display_text)
        self.add_sdk_path_btn=tk.Button(self.root, text="添加SDK打包任务",command=self.clickCallBack,width=width_value)
        self.add_sdk_path_btn.pack()
        

        self.target_build_list=tk.Listbox(self.root,selectmode=MULTIPLE,exportselection=False,width=width_value)
        self.sign_list=tk.Listbox(self.root,width=750,exportselection=False,height=4)
        for temp in self.sign_list_data:
            self.sign_list.insert(0,temp)
        self.build_config_list=tk.Listbox(self.root,exportselection=False,height=2,width=width_value)
        self.build_list_data=['Debug','Release']
        for temp in self.build_list_data:
            self.build_config_list.insert(0,temp)
        self.test_btn=tk.Button(self.root, text="开始打包",command=self.buildAllTaskCallBack,width=width_value)
        self.choose_mobileprosion_btn=tk.Button(self.root, text="选择打包用的.mobileprosion_profile",command=self.chooseMobileProsionProfileCallBack,width=width_value)
        self.choose_exportOptions_btn=tk.Button(self.root, text="选择打包用的exportOptions.plist",command=self.chooseExportOptionsInfoFileCallBack,width=width_value)
        self.result_display_msg=tk.StringVar()
        self.result_display_msg.set('')
        self.result_display_msg_Label=tk.Label(self.root,textvariable=self.result_display_msg,height=5,bg='white')
        self.target_build_list.pack()
        self.sign_list.pack()
        self.build_config_list.pack()
        
        self.mobileprosion_path_text.pack()
        self.plist_path_text.pack()
        
        self.result_display_msg_Label.pack()
        self.choose_mobileprosion_btn.pack()
        # self.choose_exportOptions_btn.pack()
        self.exportIpaTarget()
        self.exportIpaConfigFrame()

        self.test_btn.pack()
        

        
    
    def update_list_task(self,build_task_name):
        self.target_build_list.insert(0,build_task_name)
        pass

    def gui_main(self):
        root = tk.Tk()
        root.title("iOS包体打包工具!")
        root.geometry('840x800')
        root.resizable(width=True,height=True)
        self.root =root
        self.xcode_path=None
        self.mobileprovision_path=None
        self.exportOptions_path=None
        self.layout_main_ui()
        tk.mainloop()

#清理删除设备上安装好的应用程序
def uninstall_device_apps():
    for index_val in range(1,4):
        appid='com.star.project_test_%s'%(index_val)
        os.system('ideviceinstaller -U %s'%(appid))

# uninstall_device_apps()
LayoutMainUI()
# find_signs_file()
