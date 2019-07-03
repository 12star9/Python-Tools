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
from xcode_build_module import XCodeBuild

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

def test(projectPathList):
    #appicon图片存储路径
    # appicon_path=mainPath+"/project_test/Assets.xcassets/AppIcon.appiconset"
    current_work_path=os.getcwd()
    for index in range(0,len(projectPathList)):
        projectPath=projectPathList[index]
        xcode_build=XCodeBuild(projectPath, projectPath+"/project_test/Info.plist",
        True,"project_test","Release","iPhone Distribution: nanxing liao (73889W623Z)",current_work_path+"/provisioning_profile/project_test_dis_provisioning_profile.mobileprovision",current_work_path+"/exportOptions.plist")
        xcode_build.checkWorkSpace()
        xcode_build.allowFinder()
        xcode_build.allowKeychain()
        xcode_build.clearPbxproj()
        xcode_build.cleanPro()
        if index==0 or index>4:
            pass
        else:
            sdk_functions={
                1:lambda :xcode_build.embedAssignSDK('Adcolony'),
                2:lambda :xcode_build.embedAssignSDK('Adview'),
                3:lambda :xcode_build.embedAssignSDK('Facebook'),
                4:lambda :xcode_build.embedAssignSDK('Youmi')
            }
            func=sdk_functions[index]
            func()
        xcode_build.buildApp()
    return

current_work_path=os.getcwd()
projecttest_path=current_work_path+"/project_test"

projectPathList=[projecttest_path]
for index in range(0,4):
    resultPath=projecttest_path+"/../backup%s"%(index)
    try:
        shutil.rmtree(resultPath)
    except BaseException:
        pass
        # print 'error!'
    pass

for index in range(0,4):
    resultPath=projecttest_path+"/../backup%s"%(index)
    try:
        shutil.copytree(projecttest_path, resultPath)
    except BaseException:
        pass
        # print 'error.'
    finally:
        projectPathList.append(resultPath)
    pass

test(projectPathList)
# ImgManager.sharedinstance().handle_icon_images()
# generateAppIcons()
