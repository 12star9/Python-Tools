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
# import appicon_generate
#用来操作XCode工程配置，以便进行多项目不同配置打包！
from mod_pbxproj import XcodeProject
#编译配置
configuration_set="Release"
#工程名
targetName = "project_test"
#项目工程主路径
mainPath = "/Users/star.liao/Desktop/Git/Python-Tools/xcode_build/project_test"
EXPORT_OPTIONS_PLIST = "exportOptions.plist"
#appicon图片存储路径
appicon_path=mainPath+"/project_test/Assets.xcassets/AppIcon.appiconset"
#证书名
certificateName = "iPhone Distribution: nanxing liao (73889W623Z)"
#mobileprovision文件先用Xcode打开一次，不然XCodeBuild会找不到
provisioning_profile_file="/Users/star.liao/Desktop/Git/Python-Tools/xcode_build/provisioning_profile/project_test_dis_provisioning_profile.mobileprovision"
provisioning_profile=''
#判断是否是workspace
isWorkSpace = False
#钥匙链相关
keychainPath="~/Library/Keychains/login.keychain-db"
keychainPassword="123456789"

mobileprovision_path="/Users/"+getpass.getuser()+"/Library/MobileDevice/Provisioning Profiles"
infoPlistFilePath=mainPath+"/project_test/"+"Info.plist"



def isNone(para):
    if para == None or len(para) == 0:
        return True
    else:
        return False
    
def allowFinder():
    os.system("chmod -R 777 %s"%mainPath)
    return
    
def scan_files(directory,postfix):
  files_list=[]
  for root, sub_dirs, files in os.walk(directory):
    for special_file in sub_dirs:
        if special_file.endswith(postfix):
            files_list.append(os.path.join(root,special_file))    
  return files_list
  
def isFinderExists():
    return os.path.exists(mainPath)
  
def cleanPro():
    global isWorkSpace
    if isWorkSpace:
        os.system('cd %s;xcodebuild -workspace %s.xcworkspace -scheme %s clean'%(mainPath,targetName,targetName))
    else:
        os.system('cd %s;xcodebuild -target %s clean'%(mainPath,targetName))

    build_path=mainPath+"/build"
    cleanCmd = "rm -r %s" %(build_path)
    process = subprocess.Popen(cleanCmd, shell = True)
    process.wait()
    print "cleaned build: %s" %(build_path)

    return

def clearPbxproj():
    print "start clearPbxproj!"
    
    global all_the_text
    path = "%s/%s.xcodeproj/project.pbxproj"%(mainPath,targetName)
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

    print "completed clearPbxproj!"
    return

def allowKeychain():
    print "security unlock-keychain -p '%s' %s"%(keychainPassword,keychainPath)
    os.system("security unlock-keychain -p '%s' %s"%(keychainPassword,keychainPath))
    return

def buildApp():
    global isWorkSpace
    files_list=scan_files(mainPath,postfix=".xcodeproj")
    temp = -1
    for k in range(len(files_list)):
        if files_list[k] == mainPath + "/" + targetName + ".xcodeproj":
            temp = k
    if temp >= 0:
        files_list.pop(temp)

    archivePath=buildArchivePath(targetName)

    for target in files_list:
        target=target.replace(".xcodeproj","")
        tmpList=target.split('/')
        name=tmpList[len(tmpList)-1]
        path=target.replace(name,"")
        path=path[0:len(path)-1]
        os.system("cd %s;xcodebuild -target %s -configuration '%s' PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s' archive -archivePath %s -destination generic/platform=iOS"%(path,name,configuration_set,provisioning_profile,certificateName,archivePath))
    if isWorkSpace:
        os.system("cd %s;xcodebuild -workspace %s.xcworkspace -configuration '%s' -scheme %s PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s' -derivedDataPath build/ archive -archivePath %s -destination generic/platform=iOS"%(mainPath,targetName,configuration_set,targetName,provisioning_profile,certificateName,archivePath))
    else:
        os.system("cd %s;xcodebuild -target %s -configuration '%s' PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s' archive -archivePath %s -destination generic/platform=iOS"%(mainPath,targetName,configuration_set,provisioning_profile,certificateName,archivePath))
    exportArchive(archivePath)
    return
    
def cerateIPA():
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
    

def exportArchive(archivePath):
    exportDirectory=buildExportDirectory()
    exportCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s' -exportOptionsPlist %s" %(archivePath, exportDirectory,provisioning_profile,certificateName,EXPORT_OPTIONS_PLIST)
    process = subprocess.Popen(exportCmd, shell=True)
    (stdoutdata, stderrdata) = process.communicate()
    signReturnCode = process.returncode
    if signReturnCode != 0:
        print 'ipa打包失败!'
    else:
        print 'ipa打包成功，路径在:%s'%(exportDirectory)
        os.system('open %s'%(exportDirectory))



def buildArchivePath(tempName):
    archiveName = "%s.xcarchive" %(tempName)
    archivePath = mainPath + '/' + archiveName
    cleanCmd = "rm -r %s" %(archivePath)
    process = subprocess.Popen(cleanCmd, shell = True)
    process.wait()
    print "cleaned archiveFile: %s" %(archivePath)
    return archivePath

# 
def buildExportDirectory():
    dateCmd = 'date "+%Y-%m-%d_%H-%M-%S"'
    process = subprocess.Popen(dateCmd, stdout=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = process.communicate()
    exportDirectory = "%s/%s" %(mainPath, stdoutdata.strip())
    return exportDirectory

def checkWorkSpace():
    global isWorkSpace
    if os.path.exists("%s/%s.xcworkspace"%(mainPath,targetName)):
        isWorkSpace = True
    else:
        isWorkSpace = False
    return

def unInstallApp(device_udid,app_bundle_id):
    (status,results)=commands.getstatusoutput("xcrun simctl uninstall %s '%s'" %(device_udid,app_bundle_id));
    print status, results

def installApp(device_udid,app_path):
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


# 启用沙盒文件访问
def setUIFileSharingEnabled(infoPlistFilePath):
    os.system('/usr/libexec/PlistBuddy -c "Add :UIFileSharingEnabled bool True" %s'%(infoPlistFilePath))
    os.system('/usr/libexec/PlistBuddy -c "Set :UIFileSharingEnabled True" %s'%(infoPlistFilePath))

# 禁用沙盒文件访问
def setUIFileSharingDisabled(infoPlistFilePath):
    os.system('/usr/libexec/PlistBuddy -c "Add :UIFileSharingEnabled bool False" %s'%(infoPlistFilePath))
    os.system('/usr/libexec/PlistBuddy -c "Set :UIFileSharingEnabled False" %s'%(infoPlistFilePath))

# 设置参与编译的.m文件的compiler-flag为'-fno-objc-arc'
def modifyXCodeFileCompilerFlag(project,relativeFolderPath,mmFilePath):
    filePath=os.path.join(relativeFolderPath,mmFilePath)
    fileid=project.get_file_id_by_path(filePath)
    files=project.get_build_files(fileid)
    for f in files:
        f.add_compiler_flag('-fno-objc-arc')

# 设置域名添加到白名单里，以通过https审核
def setAdapteHttps(domainAddress):
    os.system('/usr/libexec/PlistBuddy -c "Add :NSAppTransportSecurity:NSExceptionDomains:%s:NSIncludesSubdomains bool True" %s'%(domainAddress,infoPlistFilePath))
    os.system('/usr/libexec/PlistBuddy -c "Set :NSAppTransportSecurity:NSExceptionDomains:%s:NSIncludesSubdomains True" %s'%(domainAddress,infoPlistFilePath))
    os.system(
        '/usr/libexec/PlistBuddy -c "Add :NSAppTransportSecurity:NSExceptionDomains:%s:NSTemporaryExceptionAllowsInsecureHTTPLoads bool True" %s' % (domainAddress,
        infoPlistFilePath))
    os.system(
        '/usr/libexec/PlistBuddy -c "Set :NSAppTransportSecurity:NSExceptionDomains:%s:NSTemporaryExceptionAllowsInsecureHTTPLoads True" %s' % (domainAddress,
        infoPlistFilePath))


def addNSAppTransportSecurity():
    os.system('/usr/libexec/PlistBuddy -c "Add :NSAppTransportSecurity:NSAllowsArbitraryLoads bool True" %s'%(infoPlistFilePath))
    os.system('/usr/libexec/PlistBuddy -c "Set :NSAppTransportSecurity:NSAllowsArbitraryLoads True" %s'%(infoPlistFilePath))

def updateAppDisplayName(displayName):
    os.system('/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName %s" %s'%(displayName,infoPlistFilePath))
    # os.system('CFBundleDisplayName')


def setProjectAppDisplayName(displayName):
    project = XcodeProject.load('project_test/project_test.xcodeproj/project.pbxproj')
    # backup_file = project.backup()

    updateAppDisplayName(displayName)
    project.save();

    # project.save('project_test/project-%s.pbxproj'%(displayName))




#主函数
def main():
    # print buildArchivePath('project_test')
    # return
    # print "sys.path[0]:",sys.path[0]
    # print "sys.path[1]:",sys.path[1]
    # print "sys.argv[0]:scriptPath:", sys.argv[0]
    # print "sys.argv[1]:argv[1]:", sys.argv[1]
    # print "sys.argv[2]:argv[2]:", sys.argv[2]
    # print "len(sys.argv):",len(sys.argv)
    # setProjectAppDisplayName('firstBuild121414')
    #开始打包
    test()



def test():
    print "开始打开.mobileprovision文件位置"
    os.system("open %s"%(mobileprovision_path))
    global provisioning_profile
    #开始获取.mobileprovision文件的uuid值
    (status, provisioning_profile_temp) = commands.getstatusoutput("/usr/libexec/PlistBuddy -c 'Print UUID' /dev/stdin <<< $(/usr/bin/security cms -D -i %s)" %(provisioning_profile_file))
    provisioning_profile=provisioning_profile_temp
    print 'provisioning_profile :'
    print provisioning_profile
    checkWorkSpace()
    allowFinder()
    allowKeychain()
    clearPbxproj()
    cleanPro()
    buildApp()
    return



# shutil.copytree(mainPath, mainPath+"/../backup1")


test()
# ImgManager.sharedinstance().handle_icon_images()
# generateAppIcons()
