#coding=utf-8

import sys
import os
import  subprocess
import time





def init_a_files():
    specify_str = '.a'
    sdk_path = u'/Users/star.liao/Desktop/三轮测试游戏工程/TempleRun20425/TR2_SDKList/AdS_SDK/AggregationAdThirdSDKs'
    # 搜索指定目录
    results = []
    folders = [sdk_path]

    for folder in folders:
        # 把目录下所有文件夹存入待遍历的folders
        folders += [os.path.join(folder, x) for x in os.listdir(folder) \
                    if os.path.isdir(os.path.join(folder, x))]

        # 把所有满足条件的文件的相对地址存入结果results
        for x in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, x)) and specify_str in x:
                sdk_path = os.path.join(folder, x);
                if '.framework' in sdk_path:
                    continue;
                results.append(sdk_path);
                pass

    return results;

def init_framework_files():
    specify_str = '.framework'
    sdk_path = u'/Users/star.liao/Desktop/三轮测试游戏工程/TempleRun20425/TR2_SDKList/AdS_SDK/AggregationAdThirdSDKs'
    # 搜索指定目录
    results = []
    folders = [sdk_path]

    for folder in folders:
        # 把目录下所有文件夹存入待遍历的folders
        folders += [os.path.join(folder, x) for x in os.listdir(folder) \
                    if os.path.isdir(os.path.join(folder, x))]

        # 把所有满足条件的文件的相对地址存入结果results
        if specify_str in folder:
            framework_result= os.path.split(folder);
            framework_name= framework_result[1];

            framework_name_len=len(framework_name);
            total_len=framework_name_len-len(specify_str);
            result=framework_name[0:total_len];
            framework_name_temp=result;

            if len(result) != 0:


                for x in os.listdir(folder):

                    if x in framework_name_temp:
                        sdk_path = os.path.join(folder, x);
                        results.append(sdk_path);
                        pass;

    return results;



def get_sdk_infos(sdk_path):
    cmd = "lipo -info %s" % sdk_path
    cmpsplit=cmd.split()
    output = subprocess.check_output(cmpsplit)
    result=set(output.split())
    architectures=[];
    thin_sdks=[];
    for d in result:
        if('armv7' in d or 'armv7s' in d or 'arm64' in d or 'x86_64' in d or 'i386' in d):
            architectures.append(d);
            output_path = create_arch_framework(sdk_path, d);
            if ('armv7' in d or 'armv7s' in d or 'arm64' in d):

                thin_sdks.append(output_path);


    # create sdk file

    # os.remove(sdk_path);
    str = '  '.join(thin_sdks)
    created_file_path=sdk_path
    cmd = u"lipo -create %s -output %s" % (str, created_file_path)
    cmpsplit = cmd.split()
    try:
        output = subprocess.check_output(cmpsplit)
    except subprocess.CalledProcessError, e:
        print '%s error:%s!' % (cmd, e)

    # delete
    time.sleep(2)
    for file_temp in thin_sdks:
        if(os.path.exists(file_temp)):
            # os.remove(file_temp)
            pass



    pass

def get_file_path(sdk_path,rename_name):
    root_path = os.path.dirname(sdk_path);
    output_sdk_path = ''
    if (os.path.isfile(sdk_path)):
        array_result= sdk_path.split('/');
        framework_path= array_result[len(array_result)-2];
        framework_sdk_path=array_result[len(array_result)-1];
        if '.a' in framework_sdk_path:

            #    是.a文件
            temp_sdk_path = os.path.split(sdk_path)
            file_name = temp_sdk_path[1];
            file_name_ext = file_name.split('.');
            file_name = file_name_ext[0] + '_%s' % (rename_name);
            new_file_name = '%s/%s.%s' % (root_path, file_name, file_name_ext[1]);
            output_sdk_path = new_file_name;

        else:
            # framework_root_path=os.path.abspath(os.path.dirname(sdk_path) + os.path.sep + "..")
            framework_root_path = os.path.dirname(sdk_path);
            output_sdk_path=os.path.join(framework_root_path,'%s_%s' %(framework_sdk_path,rename_name));
        #     是.framework文件

        pass
    return output_sdk_path;


def create_arch_framework(sdk_path,arch):
    # lipo / Users / star.liao / Desktop / InterstitialAd_branch_1
    # .8
    # .0 / SDK / AggregationAdThirdSDKs / Baidu / 4.5 / BaiduMobAdSDK.framework / BaiduMobAdSDK - thin
    # armv7s - output / Users / star.liao / Desktop / InterstitialAd_branch_1
    # .8
    # .0 / SDK / AggregationAdThirdSDKs / Baidu / BaiduMobAdSDK_7s

    output_sdk_path = get_file_path(sdk_path,arch);

    cmd = u"lipo %s -thin %s -output %s" %(sdk_path,arch,output_sdk_path)
    cmpsplit = cmd.split()
    try:
        output = subprocess.check_output(cmpsplit)
    except subprocess.CalledProcessError, e:
        print '%s error:%s!' %(cmd,e)


    pass
    return output_sdk_path;



def getFileName(path):
    ''' 获取指定目录下的所有指定后缀的文件名 '''

    # print f_list
    for i in os.walk(path):
        # os.path.splitext():分离文件名与扩展名
        if os.path.splitext(i)[1] == '.a':
            print i

if __name__ == '__main__':
    paras_len= len(sys.argv)
    if paras_len>=1:
        source_file_path = sys.argv[1]
        print 'source_file_path:',source_file_path
        result_file_path = get_sdk_infos(source_file_path);
        print 'success!'
    pass