# -*- coding: utf-8 -*-
import optparse
import os
import sys
import getpass
import json
import hashlib
import smtplib
import commands

#编译配置
configuration_set="Debug"
#工程名
targetName = "project_test"
#项目工程主路径
mainPath = "/Users/star.liao/Desktop/Git/Python-Tools/xcode_build/project_test"
#证书名
certificateName = "iPhone Developer: nanxing liao (H6KAK88X9G)"
provisioning_profile_file="/Users/star.liao/Desktop/Git/Python-Tools/xcode_build/provisioning_profile/project_test_dev_provisioning_profile.mobileprovision"
provisioning_profile=''
#判断是否是workspace
isWorkSpace = False
#钥匙链相关
keychainPath="~/Library/Keychains/login.keychain-db"
keychainPassword="123456789"

mobileprovision_path="/Users/"+getpass.getuser()+"/Library/MobileDevice/Provisioning Profiles"


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
    for target in files_list:
        target=target.replace(".xcodeproj","")
        tmpList=target.split('/')
        name=tmpList[len(tmpList)-1]
        path=target.replace(name,"")
        path=path[0:len(path)-1]
        os.system("cd %s;xcodebuild -target %s -configuration '%s' PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s'"%(path,name,configuration_set,provisioning_profile,certificateName))
    if isWorkSpace:
        os.system("cd %s;xcodebuild -workspace %s.xcworkspace -configuration '%s' -scheme %s PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s' -derivedDataPath build/"%(mainPath,targetName,configuration_set,targetName,provisioning_profile,certificateName))
    else:
        os.system("cd %s;xcodebuild -target %s -configuration '%s' PROVISIONING_PROFILE='%s' CODE_SIGN_IDENTITY='%s'"%(mainPath,targetName,configuration_set,provisioning_profile,certificateName))
    return
    
def cerateIPA():
    os.system ("cd %s;rm -r -f %s-%s.ipa"%(mainPath,targetName,configuration_set))
    build_path="build"
    if isWorkSpace:
        build_path="build/Build/Products"
    else:
        build_path="build"
    os.system ("cd %s;xcrun -sdk iphoneos PackageApplication -v %s/%s/%s-iphoneos/%s.app -o %s/%s-%s.ipa CODE_SIGN_IDENTITY='%s'"%(mainPath,mainPath,build_path,configuration_set,targetName,mainPath,targetName,configuration_set,certificateName))
    os.system("open %s/%s/%s-iphoneos/"%(mainPath,build_path,configuration_set))
    app_path="%s/%s/%s-iphoneos/%s.app" %(mainPath,build_path,configuration_set,targetName);
    device_udid="booted";
    unInstallApp(device_udid,app_path)
    installApp(device_udid,app_path)
    # startApp(device_udid,"com.star.project-test")
    return

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
    
    print 'install app result:%s' %(results)

# def startApp(device_udid,app_bundle_id):
#     (status,results)=commands.getstatusoutput("sudo xcrun simctl launch %s '%s'" %(device_udid,app_bundle_id));
#     print status, results

#主函数
def main():
    print "开始打开.mobileprovision文件位置"
    os.system("open %s"%(mobileprovision_path))
    global provisioning_profile
    #开始获取.mobileprovision文件的uuid值
    (status, provisioning_profile_temp) = commands.getstatusoutput("/usr/libexec/PlistBuddy -c 'Print UUID' /dev/stdin <<< $(/usr/bin/security cms -D -i %s)" %(provisioning_profile_file))
    provisioning_profile=provisioning_profile_temp
    checkWorkSpace()
    allowFinder()
    allowKeychain()
    clearPbxproj()
    cleanPro()
    buildApp()
    cerateIPA()
    return

main()
