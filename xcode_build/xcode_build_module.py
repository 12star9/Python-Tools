# -*- coding: utf-8 -*-
import optparse
import os
import sys
import getpass
import json
import hashlib
import smtplib
import commands
import subprocess
import shutil
import re
from pbxproj import XcodeProject
from pbxproj.pbxextensions.ProjectFiles import FileOptions

#钥匙链相关
keychainPath="~/Library/Keychains/login.keychain-db"
keychainPassword="123456789"
mobileprovision_path="/Users/"+getpass.getuser()+"/Library/MobileDevice/Provisioning Profiles"

class XCodeBuild(object):
    
    def __init__(self,xcodeProjectRootPath,infoPlistFilePath,isWorkSpace,targetName,configurationSet,certificateName,provisioning_profile_file,base_exportOptionPlist):
        self.xcodeProjectRootPath = xcodeProjectRootPath
        self.infoPlistFilePath=infoPlistFilePath
        self.isWorkSpace=isWorkSpace
        self.targetName=targetName
        self.exportOptionPlist=base_exportOptionPlist
        #编译配置
        self.configuration_set=configurationSet
        #证书名
        self.certificateName =certificateName
        #开始获取.mobileprovision文件的uuid值
        (status, provisioning_profile_temp) = commands.getstatusoutput("/usr/libexec/PlistBuddy -c 'Print UUID' /dev/stdin <<< $(/usr/bin/security cms -D -i %s)" %(provisioning_profile_file))
        self.provisioning_profile=provisioning_profile_temp
        print 'self.provisioning_profile :'
        print self.provisioning_profile
        print "开始打开.mobileprovision文件位置"
        # os.system("open %s"%(provisioning_profile_file))
    
    def updateExportOptionPlistData(self):
        #根据包名更新exportOptions.plist文件信息
        #先复制一份，修改好用这份新的
        new_exportOption_plist= '%s_%s'%(self.app_display_name,self.app_bundle_id)+'_'+self.exportOptionPlist.split('/')[-1]
        shutil.copyfile(self.exportOptionPlist,new_exportOption_plist)
        self.current_exportOption_plist=new_exportOption_plist
        cmd='/usr/libexec/PlistBuddy -c "Add :provisioningProfiles:%s string %s" %s'%(self.app_bundle_id,self.provisioning_profile,new_exportOption_plist)
        os.system(cmd)
        os.system('/usr/libexec/PlistBuddy -c "Set :provisioningProfiles:%s %s" %s'%(self.app_bundle_id,self.provisioning_profile,new_exportOption_plist))
        pass
        
    def cleanPro(self):
        if self.isWorkSpace:
            os.system('cd %s;xcodebuild -workspace %s.xcworkspace -scheme %s clean'%(self.xcodeProjectRootPath,self.targetName,self.targetName))
        else:
            os.system('cd %s;xcodebuild -target %s clean'%(self.xcodeProjectRootPath,self.targetName))
        build_path=self.xcodeProjectRootPath+"/build"
        cleanCmd = "rm -r %s" %(build_path)
        process = subprocess.Popen(cleanCmd, shell = True)
        process.wait()
        return

    def clearPbxproj(self):
        path = "%s/%s.xcodeproj/project.pbxproj"%(self.xcodeProjectRootPath,self.targetName)
        print path;
        file_object = open(path)
        try:
            all_the_text=file_object.readlines()
            for text in all_the_text:
                if 'PROVISIONING_PROFILE' in text:
                    all_the_text.remove(text)
        finally:
            file_object.close()
        file_object = open(path,'w')
        try:
            for text in all_the_text:
                file_object.write(text)
        finally:
            file_object.close()
        return

    def cerateIPA(self):
        # return;
        # os.system ("cd %s;rm -r -f %s-%s.ipa"%(mainPath,targetName,configuration_set))
        # build_path="build"
        # if isWorkSpace:
        #     build_path="build/Build/Products"
        # else:
        #     build_path="build"
        # os.system ("cd %s;xcrun -sdk iphoneos PackageApplication -v %s/%s/%s-iphoneos/%s.app -o %s/%s-%s.ipa CODE_SIGN_IDENTITY='%s'"%(mainPath,mainPath,build_path,configuration_set,targetName,mainPath,targetName,configuration_set,certificateName))
        # app_path="%s/%s/%s-iphoneos/%s.app" %(mainPath,build_path,configuration_set,targetName);
        # device_udid="booted";
        # unInstallApp(device_udid,app_path)
        # installApp(device_udid,app_path)
        return
    
    def exportArchive(self,archivePath):
        result_exportDirectory=None
        exportDirectory=self.buildExportDirectory()
        exportCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s' -exportOptionsPlist %s" %(archivePath, exportDirectory,self.provisioning_profile,self.certificateName,self.current_exportOption_plist)
        process = subprocess.Popen(exportCmd, shell=True)
        (stdoutdata, stderrdata) = process.communicate()
        signReturnCode = process.returncode
        code=None
        #打包后把使用的临时exportOptionPlist和.xcarchive进行删除
        try:
            os.remove(self.current_exportOption_plist)
            cleanCmd = "rm -r %s" %(archivePath)
            os.system(cleanCmd)
            build_path=self.xcodeProjectRootPath+"/build"
            cleanCmd = "rm -r %s" %(build_path)
            process = subprocess.Popen(cleanCmd, shell = True)
            process.wait()
        except Exception,e:
            print e
        if signReturnCode != 0:
            code=-1
            print 'ipa打包失败!'
        else:
            result_exportDirectory=exportDirectory
            code=0
            print 'ipa打包成功，路径在:%s'%(exportDirectory)
            # os.system('open %s'%(exportDirectory))
        return code,result_exportDirectory

    def buildArchivePath(self,tempName):
        archiveName = "%s.xcarchive" %(tempName)
        archivePath = self.xcodeProjectRootPath + '/' + archiveName
        cleanCmd = "rm -r %s" %(archivePath)
        process = subprocess.Popen(cleanCmd, shell = True)
        process.wait()
        return archivePath

    def updateMobileProvisionProfile(self,file_path):
        #重命名
        (status, provisioning_profile_temp) = commands.getstatusoutput("/usr/libexec/PlistBuddy -c 'Print UUID' /dev/stdin <<< $(/usr/bin/security cms -D -i %s)" %(file_path))
        newname=provisioning_profile_temp+'.mobileprovision'
        # oldname=file_path.split('/')[-1]
        newfile=os.path.join(mobileprovision_path,newname)
        if not os.path.exists(newfile):
            shutil.copyfile(file_path,newfile)
    
    def buildExportDirectory(self):
        dateCmd = 'date "+%Y-%m-%d_%H-%M-%S"'
        process = subprocess.Popen(dateCmd, stdout=subprocess.PIPE, shell=True)
        (stdoutdata, stderrdata) = process.communicate()
        exportDirectory = "%s/%s" %(self.xcodeProjectRootPath, stdoutdata.strip())
        return exportDirectory

    def checkWorkSpace(self):
        if os.path.exists("%s/%s.xcworkspace"%(self.xcodeProjectRootPath,self.targetName)):
            self.isWorkSpace = True
        else:
            self.isWorkSpace = False
        return

    def unInstallApp(self,device_udid,app_bundle_id):
        (status,results)=commands.getstatusoutput("xcrun simctl uninstall %s '%s'" %(device_udid,app_bundle_id));
        print status, results

    def installApp(self,device_udid,app_path):
        (status,results)=commands.getstatusoutput("xcrun simctl install %s %s" %(device_udid,app_path));
        print 'status:%s,results:%s' %(status,results)
        return
        # process=subprocess.Popen("xcrun simctl install %s %s" %(device_udid,app_path),shell=True)
        # process.wait()
        # (stdoutdata, stderrdata) = process.communicate()
        # signReturnCode = process.returncode
        # if signReturnCode!=0:
        #     print 'error result:%s,stdoutdata:%s'%(stderrdata,stdoutdata)  
        # else:
        #     print 'install app success!'
        
    # def startApp(device_udid,app_bundle_id):
    #     (status,results)=commands.getstatusoutput("sudo xcrun simctl launch %s '%s'" %(device_udid,app_bundle_id));
    #     print status, results

    def isNone(self,para):
        if para == None or len(para) == 0:
            return True
        else:
            return False
        
    def allowFinder(self):
        os.system("chmod -R 777 %s"%(self.xcodeProjectRootPath))
        return

    def eachFile(self,filepath,postfix):
        datas = []
        fileNames = os.listdir(filepath)
        for file in fileNames:
            newDir = filepath + '/' + file
            if os.path.isfile(newDir):  
                if os.path.splitext(newDir)[1] == postfix: 
                    datas.append(newDir)
            else:
                eachFile(newDir)          
        return datas
        
    def scan_files(self,directory,postfix):
        files_list=[]
        for root, sub_dirs, files in os.walk(directory):
            for special_file in sub_dirs:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root,special_file))    
        return files_list
    
    def isFinderExists(self):
        return os.path.exists(self.xcodeProjectRootPath)

    def allowKeychain(self):
        # print "security unlock-keychain -p '%s' %s"%(keychainPassword,keychainPath)
        os.system("security unlock-keychain -p '%s' %s"%(keychainPassword,keychainPath))
        return

    def buildApp(self):
        files_list=self.scan_files(self.xcodeProjectRootPath,".xcodeproj")
        temp = -1
        for k in range(len(files_list)):
            if files_list[k] == self.xcodeProjectRootPath + "/" + self.targetName + ".xcodeproj":
                temp = k
        if temp >= 0:
            files_list.pop(temp)
        archivePath=self.buildArchivePath(self.targetName)
        # for target in files_list:
        #     target=target.replace(".xcodeproj","")
        #     tmpList=target.split('/')
        #     name=tmpList[len(tmpList)-1]
        #     path=target.replace(name,"")
        #     path=path[0:len(path)-1]
        #     os.system("cd %s;xcodebuild -target %s -configuration '%s' PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s' archive -archivePath %s -destination generic/platform=iOS"%(path,name,self.configuration_set,self.provisioning_profile,self.certificateName,archivePath))
        # -arch arm64 -arch armv7s -arch armv7
        if self.isWorkSpace:
            buildCmd="cd %s;xcodebuild -workspace %s.xcworkspace -configuration '%s' -scheme %s PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s' -derivedDataPath build/ archive -archivePath %s -destination generic/platform=iOS"%(self.xcodeProjectRootPath,self.targetName,self.configuration_set,self.targetName,self.provisioning_profile,self.certificateName,archivePath)
        else:
            buildCmd="cd %s;xcodebuild -target %s -configuration '%s' PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s' archive -archivePath %s -destination generic/platform=iOS"%(self.xcodeProjectRootPath,self.targetName,self.configuration_set,self.provisioning_profile,self.certificateName,archivePath)
        process = subprocess.Popen(buildCmd, shell=True)
        (stdoutdata, stderrdata) = process.communicate()
        signReturnCode = process.returncode
        resultMsg=None
        code=None
        if signReturnCode != 0:
            print 'ipabuild失败!'
            code=-1
        else:
            code,resultMsg=self.exportArchive(archivePath)
        return code,resultMsg

    # 启用沙盒文件访问
    def setUIFileSharingEnabled(self):
        os.system('/usr/libexec/PlistBuddy -c "Add :UIFileSharingEnabled bool True" %s'%(self.infoPlistFilePath))
        os.system('/usr/libexec/PlistBuddy -c "Set :UIFileSharingEnabled True" %s'%(self.infoPlistFilePath))

    # 禁用沙盒文件访问
    def setUIFileSharingDisabled(self):
        os.system('/usr/libexec/PlistBuddy -c "Add :UIFileSharingEnabled bool False" %s'%(self.infoPlistFilePath))
        os.system('/usr/libexec/PlistBuddy -c "Set :UIFileSharingEnabled False" %s'%(self.infoPlistFilePath))

    # 设置参与编译的.m文件的compiler-flag为'-fno-objc-arc'
    def modifyXCodeFileCompilerFlag(self,filePath):
        strongFileOptions=FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
        addFileReference= self.project.add_file(filePath,  force=False,  file_options=strongFileOptions, parent=self.frameworksGroupID, tree='SDKROOT')
        files=self.project.get_build_files_for_file(addFileReference[0].fileRef)
        for f in files:
            f.add_compiler_flags('-fno-objc-arc')

    # 设置域名添加到白名单里，以通过https审核
    def setAdapteHttps(self,domainAddress):
        os.system('/usr/libexec/PlistBuddy -c "Add :NSAppTransportSecurity:NSExceptionDomains:%s:NSIncludesSubdomains bool True" %s'%(domainAddress,self.infoPlistFilePath))
        os.system('/usr/libexec/PlistBuddy -c "Set :NSAppTransportSecurity:NSExceptionDomains:%s:NSIncludesSubdomains True" %s'%(domainAddress,self.infoPlistFilePath))
        os.system(
            '/usr/libexec/PlistBuddy -c "Add :NSAppTransportSecurity:NSExceptionDomains:%s:NSTemporaryExceptionAllowsInsecureHTTPLoads bool True" %s' % (domainAddress,
            self.infoPlistFilePath))
        os.system(
            '/usr/libexec/PlistBuddy -c "Set :NSAppTransportSecurity:NSExceptionDomains:%s:NSTemporaryExceptionAllowsInsecureHTTPLoads True" %s' % (domainAddress,
            self.infoPlistFilePath))

    def addNSAppTransportSecurity(self):
        os.system('/usr/libexec/PlistBuddy -c "Add :NSAppTransportSecurity:NSAllowsArbitraryLoads bool True" %s'%(infoPlistFilePath))
        os.system('/usr/libexec/PlistBuddy -c "Set :NSAppTransportSecurity:NSAllowsArbitraryLoads True" %s'%(infoPlistFilePath))

    def updateAppBundleId(self,app_bundle_id):
        self.app_bundle_id=app_bundle_id
        os.system('/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier %s" %s'%(app_bundle_id,self.infoPlistFilePath))
        pass
    def updateAppDisplayName(self,displayName):
        self.app_display_name=displayName
        os.system('/usr/libexec/PlistBuddy -c "Set :CFBundleName %s" %s'%(displayName,self.infoPlistFilePath))
        os.system('/usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string %s" %s'%(displayName,self.infoPlistFilePath))
        os.system('/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName %s" %s'%(displayName,self.infoPlistFilePath))

    def setProjectAppDisplayName(self,displayName):
        updateAppDisplayName(displayName)
    
    def automaticIntegrationCodeInDidFinishLaunchingWithOptions(filePath,insert_header_file_code='#import "SDK.h"',insert_code=u'[[SDK sharedInstance] show:@\"%s\" withWindow:self.window];\n' %("123")):
        try:
            default_encoding = 'utf-8'
            if sys.getdefaultencoding() != default_encoding:
                reload(sys)
                sys.setdefaultencoding(default_encoding)
            lines = []
            f = open(filePath, 'r')
            index = 0
            findindex = -1
            spacecount = 0
            isfinddidFinishLaunchingWithOptions = -1
            returnYESIndex = -1
            for line in f:
                index += 1
                # 查找指定字符串，找到索引
                if 'didFinishLaunchingWithOptions' in line:
                    # 寻找didFinishLaunchingWithOptions方法体第一行代码行数索引，记录下来
                    findindex = index
                    isfinddidFinishLaunchingWithOptions = 1
                # 寻找方法体返回值的行数索引
                if isfinddidFinishLaunchingWithOptions == 1 and 'return YES;' in line:
                    returnYESIndex = index
                # 找到方法体内第一行代码，前置空格个数
                if index == findindex + 2:
                    for c in line:
                        if c.isspace():
                            spacecount += 1
                        else:
                            break
                lines.append(line)
            f.close()
            # 找到索引位置，写入指定字符串，数组元素发生变化
            spacecount = 4
            splitstr = spacecount * ' '
            insertstr = splitstr+insert_code
            # 之前没写入开屏接入代码，这时候才插入代码
            if insertstr not in lines:
                lines.insert(returnYESIndex - 1, insertstr)
            headerIncludeStr = u'%s \n'%(insert_header_file_code)
            if headerIncludeStr not in lines:
                lines.insert(0, headerIncludeStr)
            # 重新写入字符串
            s = ''.join(lines)
            f = open(filePath, 'w++')
            f.write(s)
            f.close()
            del lines[:]
            print 'Automatic integration Success!'
            return 0
        except Exception as e:
            print "please check the error", e
            return 1

    def addSystemFrameworkOrDylib(self,project):
        strongFileOptions=FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
        frameworksGroupID=self.frameworksGroupID
        project.add_file('usr/lib/libxml2.dylib',         force=False,  file_options=strongFileOptions,             parent=frameworksGroupID, tree='SDKROOT')
        project.add_file('usr/lib/libsqlite3.dylib',        force=False,      file_options=strongFileOptions,         parent=frameworksGroupID, tree='SDKROOT')
        project.add_file('usr/lib/libz.dylib',           force=False,         file_options=strongFileOptions,         parent=frameworksGroupID, tree='SDKROOT')
        project.add_file('usr/lib/libc++.dylib',      force=False,        file_options=strongFileOptions,               parent=frameworksGroupID, tree='SDKROOT')
        project.add_file('usr/lib/libsqlite3.0.dylib',    force=False,     file_options=strongFileOptions,                    parent=frameworksGroupID, tree='SDKROOT')
        # project.add_file('usr/lib/libstdc++.6.dylib',                          parent=frameworksGroupID, tree='SDKROOT')
        # project.add_file('usr/lib/libstdc++.dylib',                          parent=frameworksGroupID, tree='SDKROOT')
        # project.add_file('usr/lib/libstdc++.6.0.9.dylib',                          parent=frameworksGroupID, tree='SDKROOT')
        project.add_file('usr/lib/libxml2.2.dylib',          force=False,   file_options=strongFileOptions,                parent=frameworksGroupID, tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CoreBluetooth.framework', file_options=strongFileOptions,   force=False, parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/GLKit.framework',file_options=strongFileOptions,   force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/AudioToolbox.framework',file_options=strongFileOptions,   force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CoreFoundation.framework',file_options=strongFileOptions,  force=False,   parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/ImageIO.framework', file_options=strongFileOptions,   force=False, parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/AdSupport.framework',file_options=strongFileOptions,    force=False, parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/AVFoundation.framework', file_options=strongFileOptions,  force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CoreMedia.framework', file_options=strongFileOptions,  force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/Foundation.framework',file_options=strongFileOptions,  force=False,   parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/Security.framework', file_options=strongFileOptions,  force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/UIKit.framework',  file_options=strongFileOptions,  force=False, parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CoreVideo.framework',file_options=strongFileOptions,   force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CFNetwork.framework',file_options=strongFileOptions,   force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/MobileCoreServices.framework',file_options=strongFileOptions,   force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CoreData.framework',  file_options=strongFileOptions,  force=False, parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CoreMotion.framework', file_options=strongFileOptions,   force=False, parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/EventKitUI.framework', file_options=strongFileOptions,  force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/EventKit.framework',  file_options=strongFileOptions,  force=False, parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/MessageUI.framework', file_options=strongFileOptions,  force=False,  parent=frameworksGroupID,tree='SDKROOT')
        file_options = FileOptions(weak=True,embed_framework=False,code_sign_on_copy=False)
        project.add_file('System/Library/Frameworks/Social.framework', force=False,  parent=frameworksGroupID,file_options=file_options,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/Twitter.framework',file_options=strongFileOptions,    force=False, parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CoreGraphics.framework',file_options=strongFileOptions,   force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CoreLocation.framework',file_options=strongFileOptions,   force=False,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/CoreTelephony.framework', force=False,  parent=frameworksGroupID,file_options=file_options,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/MediaPlayer.framework',  force=False, file_options=strongFileOptions,  parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/QuartzCore.framework', force=False, file_options=strongFileOptions,   parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/StoreKit.framework',  force=False, parent=frameworksGroupID,file_options=file_options,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/SystemConfiguration.framework',force=False,file_options=strongFileOptions,     parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/AdSupport.framework', force=False, file_options=strongFileOptions,   parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/Passkit.framework', force=False,  parent=frameworksGroupID,file_options=file_options,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/Mapkit.framework', force=False,  file_options=strongFileOptions,  parent=frameworksGroupID, tree='SDKROOT')
        project.add_file('System/Library/Frameworks/WebKit.framework', force=False, file_options=strongFileOptions,   parent=frameworksGroupID,tree='SDKROOT')
        project.add_file('System/Library/Frameworks/AVKit.framework',  force=False, parent=frameworksGroupID,file_options=file_options,tree='SDKROOT')  
                
    def add_Adcolony(self):
        parent_path = os.path.dirname(self.xcodeProjectRootPath)
        sDKResourcePath= os.path.join(parent_path, 'sdks/Adcolony')
        #库文件.framework
        file_options = FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
        self.project.add_file(sDKResourcePath+'/Adcolony.framework', force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
        self.project.add_framework_search_paths([sDKResourcePath],recursive=True)
        pass

    def add_Adview(self):
        parent_path = os.path.dirname(self.xcodeProjectRootPath)
        sDKResourcePath= os.path.join(parent_path, 'sdks/Adview')
        #库文件a
        file_options = FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
        self.project.add_file(sDKResourcePath+'/libAdCompViewSDK.a', force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
        # self.project.add_flags('_SEARCH_PATHS',sDKResourcePath+'/**',self.targetName)
        self.project.add_library_search_paths([sDKResourcePath],recursive=True)
        #资源文件.png
        files=self.eachFile(sDKResourcePath+'/res',postfix=".png")
        files_temp=self.scan_files(sDKResourcePath+'/res',postfix=".png")
        for file in files:
            self.project.add_file(file, force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
        #源代码文件
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,"TouchJSON/CDataScanner.m"))
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,'TouchJSON/Experimental/CFilteringJSONSerializer.m'))
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,'TouchJSON/Experimental/CJSONDeserializer_BlocksExtensions.m'))
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,'TouchJSON/Experimental/CJSONSerialization.m'))
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,'TouchJSON/Experimental/CJSONSerializedData.m'))      
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,'TouchJSON/Extensions/CDataScanner_Extensions.m'))
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,'TouchJSON/Extensions/NSDictionary_JSONExtensions.m'))     
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,'TouchJSON/JSON/CJSONDeserializer.m'))
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,'TouchJSON/JSON/CJSONScanner.m'))
        self.modifyXCodeFileCompilerFlag(os.path.join(sDKResourcePath,'TouchJSON/JSON/CJSONSerializer.m'))
        self.project.add_header_search_paths([sDKResourcePath],recursive=True)
        pass

    def updateProjectSettings(self):
        self.project.add_other_ldflags("-ObjC")
        self.project.add_flags('ENABLE_BITCODE',
                               u'NO', self.targetName)

    def add_Facebook(self):
        parent_path = os.path.dirname(self.xcodeProjectRootPath)
        sDKResourcePath= os.path.join(parent_path, 'sdks/Facebook')
        file_options = FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
        self.project.add_file(sDKResourcePath+'/FBAudienceNetwork.framework', force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
        self.project.add_flags('FRAMEWORK_SEARCH_PATHS',sDKResourcePath+'/**',self.targetName)
        pass
    
    def add_Youmi(self):
        parent_path = os.path.dirname(self.xcodeProjectRootPath)
        sDKResourcePath= os.path.join(parent_path, 'sdks/Youmi')
        #库文件a
        file_options = FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
        self.project.add_file(sDKResourcePath+'/libUMVideoSDK.a', force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
        self.project.add_library_search_paths([sDKResourcePath],recursive=True)
        #资源文件.png
        self.project.add_file(sDKResourcePath+'/UMVideo.bundle', force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
        pass

    #获取SDK的所有相关文件
    def get_all_sdk_files(self,dir):
        files_ = []
        list = os.listdir(dir)
        for i in range(0, len(list)):
            path = os.path.join(dir, list[i])
            if os.path.isdir(path):
                #.bundle,.framework会被识别成目录，这里需要做下判断
                if path.endswith('bundle') or path.endswith('framework'):
                    files_.append(path)
                    continue
                else:
                    files_.extend(self.get_all_sdk_files(path))
            if os.path.isfile(path):
                files_.append(path)
        return files_

    # 这个方法用来查询sdk文件夹下的库，资源等数据，以来修改工程配置
    def updateProjectSetsForSDK(self,sdk_path):
        sdk_file_path=self.get_all_sdk_files(sdk_path)
        framework_search_path=[]
        library_search_path=[]
        header_search_path=[]
        for temp_path in sdk_file_path:
            if temp_path.endswith('bundle'):
                file_options = FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
                self.project.add_file(temp_path, force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
                pass
            elif temp_path.endswith('framework'):
                framework_search_path_temp=os.path.dirname(temp_path)
                if not framework_search_path_temp in framework_search_path:
                    framework_search_path.append(framework_search_path_temp)
                #库文件.framework
                mach_file_name=temp_path.split('/')[-1].split('.')[-2]
                file_path= os.path.join(temp_path,mach_file_name)
                #判断是否是动态库
                process=subprocess.Popen('file %s'%(file_path),shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                (stdoutdata, stderrdata) = process.communicate()
                if 'dynamically' in stdoutdata:
                    embed_framework_val=True
                    code_sign_on_copy_val=True
                else:
                    embed_framework_val=False
                    code_sign_on_copy_val=False
                file_options = FileOptions(weak=False,embed_framework=embed_framework_val,code_sign_on_copy=code_sign_on_copy_val)
                self.project.add_file(temp_path, force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
                pass
            elif temp_path.endswith('h'):
                header_search_path_temp=os.path.dirname(temp_path)
                if not header_search_path_temp in header_search_path:
                    header_search_path.append(header_search_path_temp)
                pass
            elif temp_path.endswith('m'):
                #
                strongFileOptions=FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
                addFileReference= self.project.add_file(temp_path,  force=False,  file_options=strongFileOptions, parent=self.frameworksGroupID, tree='SDKROOT')
                #判断是否是非ARC编译,读取内容，看是否有....release]
                fin = open(temp_path,'r')
                result=None
                is_not_arc=False
                for eachLine in fin:
                    if 'release]'in eachLine:
                        is_not_arc=True
                        break
                fin.close()
                if is_not_arc==True:
                    files=self.project.get_build_files_for_file(addFileReference[0].fileRef)
                    for f in files:
                        f.add_compiler_flags('-fno-objc-arc')
                pass
            elif temp_path.endswith('a'):
                library_search_path_temp=os.path.dirname(temp_path)
                if not library_search_path_temp in library_search_path:
                    library_search_path.append(library_search_path_temp)
                file_options = FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
                self.project.add_file(temp_path, force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
                pass
            #图片等资源文件
            else:
                file_options = FileOptions(weak=False,embed_framework=False,code_sign_on_copy=False)
                self.project.add_file(temp_path, force=False,  parent=self.frameworksGroupID,file_options=file_options,tree='SDKROOT')
                pass
            pass
        for temp_path in framework_search_path:
            self.project.add_framework_search_paths([temp_path],recursive=True)
        for temp_path in library_search_path:
            self.project.add_library_search_paths([temp_path],recursive=True)
        for temp_path in header_search_path:
            self.project.add_header_search_paths([temp_path],recursive=True)
        self.addSystemFrameworkOrDylib(self.project)
        self.updateProjectSettings()
        self.project.save()
        pass

    def initProject(self):
        # 初始化
        pbxproj=self.xcodeProjectRootPath+'/project_test.xcodeproj/project.pbxproj'
        infoPlistPath=self.xcodeProjectRootPath+'/project_test/Info.plist'
        #每次从壳工程备份里拷贝源文件到这里，再加载
        try:
            src_path=os.path.join(os.getcwd(),'project.pbxproj')
            infPlist_Src_Path=os.path.join(os.getcwd(),'Info.plist')
            shutil.copy(src_path,pbxproj)
            shutil.copy(infPlist_Src_Path,infoPlistPath)
        except Exception,e:
            print e 
        self.project = XcodeProject.load(pbxproj)
        frameworksGroupID = None
        textfile = open(pbxproj, 'r')
        filetext = textfile.read()
        textfile.close()
        matches = re.findall("([0-9A-F]*) /\* Frameworks \*/ = \{\n\s*isa = PBXGroup;", filetext)
        print "matches:",matches
        try:
            frameworksGroupID = matches[0]
        except:
            pass
        self.frameworksGroupID =self. project.get_or_create_group('Frameworks')

    def embedAssignSDK(self,sdk_name):
        # 引入不同SDK，涉及框架引入，代码文件引入，资源文件引入
        sdk_functions={
            'Adcolony':lambda:self.add_Adcolony(),
            'Adview':lambda:self.add_Adview(),
            'Facebook':lambda:self.add_Facebook(),
            'Youmi':lambda:self.add_Youmi()
        }
        func=sdk_functions[sdk_name]
        func()
        self.addSystemFrameworkOrDylib(self.project)
        self.updateProjectSettings()
        self.project.save()
        pass
        return

