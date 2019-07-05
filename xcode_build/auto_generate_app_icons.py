# -*- coding: utf-8 -*-
import os ,threading
from PIL import Image
import subprocess
import json

class ImgManager(object):
  thread_lock = threading.Lock()
  @classmethod
  def sharedinstance(cls):
    with ImgManager.thread_lock:
      if not hasattr(ImgManager,"instance"):
        ImgManager.instance = ImgManager()
    return ImgManager.instance
 
  # 运行shell命令
  def runshellCMD(self,cmd,dsr):
    progress = subprocess.Popen(cmd,shell=True)
    progress.wait()
    result = progress.returncode
    if result !=0:
      print("%s失败"%(dsr))
    else:
      print("%s成功"%(dsr))
 
  #创建图片
  def createImg(self,model):
    path = '%s/project_test/project_test/Assets.xcassets/AppIcon.appiconset/AppStore.png'%(os.getcwd())
    currentPath = "%s/Images/%s"%(os.getcwd(),model.filename)
    print(currentPath)
    im = Image.open(path,'r')
    # w,h=im.size
    # print("%s,%s"%(str(w),str(h)))
    #
    im.thumbnail((float(model.get_wh()),float(model.get_wh())))
    if model.filename.endswith('.png'):
      im.save("%s" % (currentPath),"png")
    else:
      # self.runshellCMD("sudo cp %s %s" % (path, currentPath), "拷贝")
      self.addTransparency(im)
      im.save("%s" % (currentPath), "jpeg")
      # r, g, b, alpha = im.split()
      # print("%s"%(str(im.split()[0])))
 
#修改透明度
  def addTransparency(img, factor=0.0):
    img = img.convert('RGBA')
    img_blender = Image.new('RGBA', img.size, (0, 0, 256, 256))
    img = Image.blend(img_blender, img, factor)
    return img
 
 
#解析Contents.json，这个文件每一个Images.xcassets 的AppIcon文件夹都有，直接复用就可以了
  def handle_icon_images(self):
 
    jsonpath = os.getcwd() +"/project_test/project_test/Assets.xcassets/AppIcon.appiconset/Contents.json"
    if not os.path.exists(jsonpath):
      print("Contents.json path not exite")
      return
    with open(jsonpath,'r') as f:
      jsonstr = f.read()
    modle = json.loads(jsonstr)
    arrs = modle['images']
    # print(arrs)
    icon_models=[]
    for obj in arrs:
      size=obj["size"]
      idiom=obj["idiom"]
      filename=obj["filename"]
      scale=obj["scale"]
      icom =iconImg(size=size,idiom=idiom,filename=filename,scale=scale)
      # icon_models.append(icom)
      self.createImg(icom)
 
 
  #json 数据里面有效数据的类
class iconImg(object):
  def __init__(self,size,idiom,filename,scale):
    self.size = size
    self.idiom = idiom
    self.filename = filename
    self.scale = scale
 
  def show(self):
    print("%s,%s,%s,%s"%(self.size,self.idiom,self.filename,self.scale))
 
 
  def get_wh(self):
    return (float(self.size.split('x')[0]))*(float(self.scale.split('x')[0]))

 
if __name__ == '__main__':
  ImgManager.sharedinstance().handle_icon_images()