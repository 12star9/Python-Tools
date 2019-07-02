# -*- coding: utf-8 -*-
from PIL import Image

# def createImg(model):
#     path='%s/AppStore.png' %(appicon_path)
    # filename=model.filename
    # print filename
    # currentPath=appicon_path+'/'+filename
    # im=Image.open(path,'r')
    # im.thumbnail(float(model.get_wh()),float(model.get_wh()))
#     if model.filename.endswith('.png'):
#         im.save("%s" % (currentPath),"png")
#     else:
#         print ''
# def generateAppIcons():
    # return
    # jsonpath=appicon_path+'/Contents.json'
    # jsonpath=appicon_path+"/Contents.json"

#     if not os.path.exists(jsonpath):
#       print("Contents.json path not exite")
#       return
#     with open(jsonpath,'r') as f:
#       jsonstr = f.read()
#     modle = json.loads(jsonstr)
#     arrs = modle['images']
#     # print(arrs)
#     icon_models=[]
#     for obj in arrs:
#       size=obj["size"]
#       idiom=obj["idiom"]
#       filename=obj["filename"]
#       scale=obj["scale"]
#       icom =iconImg(size=size,idiom=idiom,filename=filename,scale=scale)
      # icon_models.append(icom)
#       createImg(icom)

class iconImg(object):
    def __init__(self,size,idiom,filename,scale):
        self.size=size
        self.idiom=idiom
        self.filename=filename
        self.scale=scale
    def show(self):
        print ''
    def get_wh(self):
        return (float(self.size.split('x')[0]))*(float(self.scale.split('x')[0]))