# -*- coding: utf-8 -*-
import os
import subprocess
import json

current_Path=os.getcwd()
commendFilePath=current_Path+"/system_dependency_config.json"

def system_dependency_write(bool_val):
    fout = open(commendFilePath,'w')
    js = {}
    js['state_val']=bool_val
    outStr = json.dumps(js,ensure_ascii = False)
    fout.write(outStr.strip().encode('utf-8') + '\n')
    fout.close()

def read_system_dependency():
    if os.path.exists(commendFilePath)==False:
        return None
    fin = open(commendFilePath,'r')
    result=None
    for eachLine in fin:
        line = eachLine.strip().decode('utf-8')
        line = line.strip(',')
        js = None
        try:
            js = json.loads(line)
            result=js['state_val']
            break
        except Exception, e:
            print e
            continue
    return result

def clean_up():
    os.system('cd %s'%(current_Path))
    os.system('rm -rf build dist')
    # os.system('rm -rf setup.py')
    
def generate_main(main_name='gui_main'):

    os.system('cd %s'%(current_Path))
    os.system('pwd')
    state_val=read_system_dependency()
    if state_val==None or state_val==False:
        buildCmd='easy_install -U git+https://github.com/metachris/py2app.git@master'
        process = subprocess.Popen(buildCmd, shell=True)
        process.wait()
        signReturnCode = process.returncode
        if signReturnCode == 0:
            system_dependency_write(True)
        else:
            system_dependency_write(False)
            pass
    process2=subprocess.Popen('py2applet --make-setup %s.py'%(main_name),shell=True)
    #这里可能会提示是否覆盖？？
    process2.wait()

    
    os.system('rm -rf build dist')
    process3=subprocess.Popen('python setup.py py2app',shell=True)
    process3.wait()
    signReturnCode = process3.returncode
    if signReturnCode == 0:
        target_path=os.path.join(current_Path,"dist/%s"%(main_name))
        print '生成MacOSX桌面程序成功！路径在:%s.app'%(target_path)
        os.system('open %s.app'%(target_path))
        pass
    else:
        
        pass
    return

clean_up()
generate_main('gui_main')
