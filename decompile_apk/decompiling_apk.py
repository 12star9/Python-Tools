#!/usr/bin/env python
# coding=utf-8

import os
import zipfile;
import base64;

# apk 的存储路径
apkPath = u'./APKs/'

dirlist = os.listdir(apkPath)

# 用apktool 反编译apk 之后的存储路径
outputPath = u'./apktool_out/'


def zip_apk_file_path(input_path, output_path, output_name):
    f = zipfile.ZipFile(output_path + '/' + output_name, 'w', zipfile.ZIP_DEFLATED)
    filelists = []
    get_zip_file(input_path, filelists)
    for file in filelists:
        f.write(file);
    f.close()
    return output_path + r"/" + output_name

def apkToolFunction(APKPath, APK,apkoutPath):
    targetPath=apkoutPath;
    cmd = "apktool d -f {0} -o {1}".format(APKPath, targetPath)  
    os.system(cmd)
    output_path=os.path.dirname(targetPath);
    zipName=APK+'.zip';
    result= zip_apk_file_path(targetPath,output_path,zipName);
    ipa_file_define_name=base64.b64encode(result);
    filePath=base64.b64decode(ipa_file_define_name);
    directory = os.path.dirname(filePath);
    filename = os.path.basename(filePath);
    print 'result:'+result;

def get_zip_file(input_path, result):
    files = os.listdir(input_path)
    for file in files:
        if os.path.isdir(input_path + '/' + file):
            get_zip_file(input_path + '/' + file, result)
        else:
            result.append(input_path + '/' + file)

for i in range(len(dirlist)):  
    filelist = apkPath + dirlist[i]  
    filelist = filelist.decode('gbk');
    apklist = os.listdir(filelist)  
    category_output = outputPath + dirlist[i]  

    if not os.path.exists(category_output):  
        os.makedirs(category_output)

    for APK in apklist:
        portion = os.path.splitext(APK)  
        apkoutPath = os.path.join(category_output, portion[0]) 
        result_APK = os.path.join(apkPath + dirlist[i], APK)
        # if not os.path.exists(apkoutPath):
        #    os.makedirs(apkoutPath)
        # cmd = "apktool d -f {0} -o {1}".format(APK, apkoutPath)  # 反编译出来apk 之后按照文件名在存储
        # os.system(cmd)
        apkToolFunction(result_APK,APK,apkoutPath);


print "all work done!~"
