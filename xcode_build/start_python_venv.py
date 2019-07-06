# -*- coding: utf-8 -*-
import os
import shutil
import time
import subprocess

#Git下载代码后，开始部署虚拟环境并激活
def start_python_venv():
    os.chdir('%s'%(os.getcwd()))
    os.system('virtualenv %s'%('venv'))
    os.chdir('%s'%('venv'))
    os.system('pwd')
    os.system('source ./bin/activate')
    os.system('pip install -r ../requirements.txt')

def ready_push_git():
    os.chdir('%s/venv'%(os.getcwd()))
    os.system('pip freeze > ../requirements.txt')
    shutil.rmtree(os.getcwd())

def venv_deactivate():
    os.system('deactivate')

