# -*- coding: utf-8 -*-
import zipfile
import os.path
import os
import time
import shutil
import subprocess
import plistlib
import commands


class ReSignIpaLOgic(object):
  def __init__(self,ipa_path):
    self.ipa_path = ipa_path
    self.embedCode=False
    self.signextensions=['.framework/']

  # def printMobileProvisionProfile(self):
  #   os.system('security cms -D -i %s'%(self.mobileProvisionProfilePath))

  #导入证书，获取证书名，处理部署Mac机器上没有导入对应证书的情况
  def importP12CerFile(self,cer_path,cer_password):
    p12Name=''
    p = subprocess.call('security import %s -k ~/Library/Keychains/login.keychain -P %s -T /usr/bin/codesign'%(cer_path,cer_password),shell=True)
    if p == 0:
        p = subprocess.check_output('openssl pkcs12 -nodes -in %s -info -nokeys -passin "pass:%s" 2>/dev/null | grep "friendlyName"'%(cer_path,cer_password),shell=True)
        p= str(p)
        p= p.strip()
        p= p.replace('friendlyName:','',1)
        p = p.rstrip('\n')
        p12Name = p
    return p12Name

  def copyprovsion2appdir(self,originpath,mobileprovision):
    for dirpath, dirnames, filenames in os.walk(originpath):
      if dirpath[dirpath.rfind('.'):] == '.app':
        shutil.copy(mobileprovision,'%s/%s' % (dirpath,'embedded.mobileprovision'))
        return True
    return False

  def start_generate_entitlements(self,mobileprovisionpath,entilementspath):
    entilementfull = entilementspath[:entilementspath.rfind('.')] + '_full.plist'
    (status1, output1) = commands.getstatusoutput('security cms -D -i "%s" > %s' % (mobileprovisionpath, entilementfull))
    (status2, output2) = commands.getstatusoutput('/usr/libexec/PlistBuddy -x -c "Print:Entitlements" %s > %s' % (entilementfull,entilementspath))
    return status1 == 0 and status2 == 0

  def isneedsign(self,filename):
    for signextension in self.signextensions:
      if signextension == filename[filename.rfind('.'):]:
        return True
    return False


  def codesign(self,certificate,entilement,signObj,extrapath):
    # 开始注入代码
    if self.embedCode==True and '.app' in signObj and not '.framework' in signObj and not '/PlugIns/' in signObj and not '.dylib' in signObj:
      machFileName= signObj.split('/')[-2].split('.')[-2]
      machFilePath= os.path.join(extrapath,signObj,machFileName)
      os.system('chmod +x %s'%(machFilePath))
      machFileFrameworkPath= os.path.join(extrapath,signObj,'Frameworks')
      machFoloerPath=os.path.join(extrapath,signObj)
      insert_sdks_path=os.path.join(os.getcwd(),'insert_sdks')
      shutil.copytree('%s/MobGiAdsToolModuleBundle.bundle'%(insert_sdks_path),os.path.join(extrapath,signObj,'MobGiAdsToolModuleBundle.bundle'))
      if not os.path.exists(machFileFrameworkPath):
        shutil.copytree('%s/Frameworks'%(insert_sdks_path),os.path.join(extrapath,signObj,'Frameworks'))
        pass
      else:
        for temp_path in os.listdir('%s/Frameworks'%(insert_sdks_path)):
          if '.framework' in temp_path:
            shutil.copytree(os.path.join('%s/Frameworks'%(insert_sdks_path),temp_path),os.path.join(machFileFrameworkPath,temp_path))
        pass
      os.system('chmod +x %s'%('%s/yololib'%(os.getcwd())))
      cmd1='%s/yololib %s %s'%(os.getcwd(),machFilePath,'Frameworks/MobGiAdsToolModule.framework/MobGiAdsToolModule')
      print cmd1
      os.system(cmd1)

      frameworkPath2= os.path.join(machFileFrameworkPath,'SDKCommonModule.framework/SDKCommonModule')
      os.system('%s/yololib %s %s'%(os.getcwd(),machFilePath,'Frameworks/SDKCommonModule.framework/SDKCommonModule'))

      sign_cmd='codesign -f -s "%s" --entitlements "%s" "%s"' % (certificate,entilement,os.path.join(machFileFrameworkPath,'MobGiAdsToolModule.framework/'))
      os.system(sign_cmd)


      sign_cmd='codesign -f -s "%s" --entitlements "%s" "%s"' % (certificate,entilement,os.path.join(machFileFrameworkPath,'SDKCommonModule.framework/'))
      os.system(sign_cmd)

    sign_cmd='codesign -f -s "%s" --entitlements "%s" "%s"' % (certificate,entilement,'%s%s' % (extrapath,signObj))
    print sign_cmd
    (status, output) = commands.getstatusoutput(sign_cmd)
    if status == 0 and 'replacing existing signature' in output:
      print 'replacing %s existing signature successed' % signObj
      return True
    else:
      print(output)
      return False

  def startsign(self,certificate,entilement,zfilelist,extrapath):
    print("----------------开始签名----------------")
    for filename in zfilelist:
      if self.isneedsign(filename):
        if not self.codesign(certificate,entilement,filename,extrapath):
          return False
      
    return True

  def zipcompress(self,originpath,destinationzfile):
    resignedzfile = zipfile.ZipFile(destinationzfile,'w',zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(originpath):
      fpath = dirpath.replace(originpath,'')
      fpath = fpath and fpath + os.sep or ''
      for filename in filenames:
        resignedzfile.write(os.path.join(dirpath, filename), fpath+filename)
    resignedzfile.close()

  def verifySignature(self,extralfilepath):
    for dirpath, dirnames, filenames in os.walk(extralfilepath):
      if dirpath[dirpath.rfind('.'):] == '.app':
        (status,output) = commands.getstatusoutput('codesign -v "%s"' % dirpath)
        if len(output) == 0:
          return True
        else:
          print(output)
          return False
    return False

  def startInvoke(self):
    zipFilePath = self.ipa_path
    extrapath = '%s/Payload_From_Ipa/' % (os.path.dirname(zipFilePath))
    certificate='iPhone Developer: nanxing liao (H6KAK88X9G)'
    mobileprovision = '/Users/star.liao/Desktop/Git/Python-Tools/re-sign-ipa/embedded.mobileprovision'
    self.mobileProvisionProfilePath=mobileprovision
    # self.printMobileProvisionProfile()
    entilement  = extrapath + "entitlements.plist"
    destinationzfile = zipFilePath[:zipFilePath.rfind('.')] + '_resigned.ipa'
    originzfile = zipfile.ZipFile(zipFilePath,'r')
    zfilelist = originzfile.namelist()
    zfilelist.reverse()
    originzfile.extractall(extrapath)
    self.copyprovsion2appdir(extrapath, mobileprovision)
    if not self.start_generate_entitlements(mobileprovision,entilement):
      originzfile.close()
      shutil.rmtree(extrapath)
      return False
    try:
      #开始签名
      if zfilelist != None and self.startsign(certificate,entilement,zfilelist,extrapath):
        if self.verifySignature(extrapath):
          self.zipcompress(extrapath,destinationzfile)
          print "重签名打包成功,请查看：%s" % destinationzfile
        else:
          pass
      else:
        pass
    finally:
      originzfile.close()
      shutil.rmtree(extrapath)
      
reSignIpaLOgic=ReSignIpaLOgic('/Users/star.liao/Desktop/Git/Python-Tools/re-sign-ipa/1.ipa')
reSignIpaLOgic.embedCode=True
reSignIpaLOgic.startInvoke()
  
