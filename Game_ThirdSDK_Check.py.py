#coding=utf-8

import sys
import os
import  subprocess
import time
import shlex

# 第三方SDK文件夹目录的父级目录
third_SDK_Root_Path=''
# 第三方SDK名称标示,这里实例说明
third_SDK_Names=['Unity',
                 'Admob'
                 ]
# 第三方SDK文件.a或framework的路径目录,这里实例说明
third_SDK_Paths=['Unity/2.1.1/UnityAds.framework/UnityAds',
                 'Admob/7.25.0/GoogleMobileAds.framework/GoogleMobileAds'
                 ]

# 调用子进程，拿到输出结果
# @time_me
def startSubprocessPrograme(shell_cmd,check_classValue,platName):
    start = time.clock()
    #
    cmd=shlex.split(shell_cmd)
    p=subprocess.Popen(cmd,shell=False,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    result = False
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if check_classValue in line:
            result=True
    if p.returncode == 0:
        
        pass
    else:
        print('subprocess failed : [{}]'.format(shell_cmd))
    print(' 完成 :[{}] SDK查找!!!!'.format(platName))
    if result==True:
        print('成功找到SDK: [{}]'.format(platName))
    else:
        print('不是 [{}] SDK'.format(platName))

    end = time.clock()

    print str(end-start)
    return result

# @time_me
def searchFull(search_platName):
    result_platname=''
    for i in range(len(third_SDK_Names)):
        # 组装全路径
        platNamePath = third_SDK_Paths[i]
        # 可能存在多个路径
        arrTemp=platNamePath.split(',')
        for j in range(len(arrTemp)):
            platNamePath=arrTemp[j]
            print(' platNamePath: {}'.format(platNamePath))

            platFullPath = third_SDK_Root_Path + platNamePath

            targetPath = 'strings {}'.format(platFullPath)
            platName = third_SDK_Names[i]

            print(' cmd: {}'.format(targetPath))
            result = startSubprocessPrograme(
                targetPath,
                search_platName, platName)

            if result == True:

                break;

        if result == True:
            result_platname=third_SDK_Names[i]
            break;
    print('=======')
    print('完成SDK查找!!! 目标SDK是:{}'.format(result_platname))
    print('=======')
    pass

if __name__ == '__main__':
    paras_len= len(sys.argv)
    if paras_len>=2:
        third_SDK_Root_Path=sys.argv[1]
        search_platName = sys.argv[2]
        start = time.clock()
        searchFull(search_platName)
        end = time.clock()
        print str(end-start)
    pass