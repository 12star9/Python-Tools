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

reload(sys)
sys.setdefaultencoding('utf8')

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
        self.gui_main()
        pass

    def chooseXcodePathCallBack(self):
        file_path = tkinter.filedialog.askdirectory()
        self.xcode_display_text.set(file_path)
        self.xcode_path=file_path
        pass

    def chooseTargetFile(self,file_extenstion):
        result= tkinter.filedialog.askopenfilename(title='选择打包需要的 .%s 文件'%(file_extenstion), filetypes=[('%s'%(file_extenstion.upper()),'*.%s'%(file_extenstion)), ('All Files', '*')])
        return result
        pass

    def buildAllTaskCallBack(self):
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
        if self.mobileprovision_path==None or self.exportOptions_path==None:
            tkinter.messagebox.showerror('打包错误提示','.mobileprovision_profile或ipa打包.plist文件没有设置!')
            return
        all_len=self.target_build_list.size()
        list=[]
        for temp in range(0,all_len):
            list.append(self.target_build_list.get(temp))
        if len(list)==0:
            tkinter.messagebox.showwarning('⚠️','没有引入SDK打包!')
        #根据不同的sdk路径,开始打包
        projectPath=self.xcode_path
        if projectPath==None:
            tkinter.messagebox.showerror('打包错误提示','没有设置打包壳工程!')
            return
        index_val=0
        project_name= os.path.split(projectPath)[-1]
        for sdk_path in list:
            index_val=index_val+1
            xcode_build=XCodeBuild(projectPath, projectPath+"/%s/Info.plist"%(project_name),
            True,project_name,build_config,sign_path,self.mobileprovision_path,self.exportOptions_path)
            xcode_build.checkWorkSpace()
            xcode_build.allowFinder()
            xcode_build.allowKeychain()
            xcode_build.clearPbxproj()
            xcode_build.cleanPro()
            # sdk_name= os.path.split(sdk_path)[-1]
            # if sdk_name=='Adview':
            #     xcode_build.embedAssignSDK('Adview')
            # elif sdk_name=='Youmi':
            #     xcode_build.embedAssignSDK('Youmi')
            # elif sdk_name=='Facebook':
            #     xcode_build.embedAssignSDK('Facebook')
            # elif sdk_name=='Adcolony':
            #     xcode_build.embedAssignSDK('Adcolony')
            xcode_build.initProject()
            xcode_build.updateAppDisplayName('project_test_%s'%(index_val))
            xcode_build.updateAppBundleId('com.star.project_test_%s'%(index_val))
            xcode_build.updateMobileProvisionProfile(self.mobileprovision_path)
            xcode_build.updateExportOptionPlistData()
            xcode_build.updateProjectSetsForSDK(sdk_path)
            code,resultMsg=xcode_build.buildApp()
            if code==0:
                lastStr=self.result_display_msg.get()
                currentStr='\n打包路径在:%s'%(resultMsg)
                targetStr=u'%s%s'%(lastStr,currentStr)
                #找到.ipa文件并安装
                ipa_list= self.get_all_ipa_files(resultMsg)
                for ipa_temp in ipa_list:
                    os.system('ideviceinstaller -i %s'%(ipa_temp))
                #删除安装好的ipa目录
                shutil.rmtree(resultMsg)
                self.result_display_msg.set(targetStr)
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

    def layout_main_ui(self):
        self.choose_xcode_path_btn=tk.Button(self.root, text="选择Xcode工程路径",command=self.chooseXcodePathCallBack)
        self.xcode_display_text=tk.StringVar()
        self.xcode_display_text.set('')
        self.xcode_path_text=tk.Label(self.root,height=2,textvariable=self.xcode_display_text)
        self.mobileprosion_display_text=tk.StringVar()
        self.mobileprosion_display_text.set('')
        self.plist_display_text=tk.StringVar()
        self.plist_display_text.set('')
        self.mobileprosion_path_text=tk.Label(self.root,height=2,textvariable=self.mobileprosion_display_text)
        self.plist_path_text=tk.Label(self.root,height=2,textvariable=self.plist_display_text)
        self.add_sdk_path_btn=tk.Button(self.root, text="添加SDK打包任务",command=self.clickCallBack)
        self.target_build_list=tk.Listbox(self.root,width=750,selectmode=MULTIPLE,exportselection=False)
        self.sign_list=tk.Listbox(self.root,width=750,exportselection=False,height=4)
        for temp in self.sign_list_data:
            self.sign_list.insert(0,temp)
        self.build_config_list=tk.Listbox(self.root,width=750,exportselection=False,height=2)
        self.build_list_data=['Debug','Release']
        for temp in self.build_list_data:
            self.build_config_list.insert(0,temp)
        self.test_btn=tk.Button(self.root, text="开始打包",command=self.buildAllTaskCallBack)
        self.choose_mobileprosion_btn=tk.Button(self.root, text="选择打包用的.mobileprosion_profile",command=self.chooseMobileProsionProfileCallBack)
        self.choose_exportOptions_btn=tk.Button(self.root, text="选择打包用的exportOptions.plist",command=self.chooseExportOptionsInfoFileCallBack)
        self.result_display_msg=tk.StringVar()
        self.result_display_msg.set('')
        self.result_display_msg_Label=tk.Label(self.root,textvariable=self.result_display_msg,height=20)
        self.target_build_list.pack()
        self.sign_list.pack()
        self.build_config_list.pack()
        self.xcode_path_text.pack()
        self.mobileprosion_path_text.pack()
        self.plist_path_text.pack()
        self.choose_xcode_path_btn.pack()
        self.add_sdk_path_btn.pack()
        self.choose_mobileprosion_btn.pack()
        self.choose_exportOptions_btn.pack()
        self.test_btn.pack()
        self.result_display_msg_Label.pack()
    
    def update_list_task(self,build_task_name):
        self.target_build_list.insert(0,build_task_name)
        pass

    def gui_main(self):
        root = tk.Tk()
        root.title("iOS包体打包工具!")
        root.geometry('1200x940')
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
