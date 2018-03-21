import maya.cmds as mc
import maya.mel as mel
import os

import Utilities.projectGlobals as pg

class versionClass():
    def versionUp(self, filePath, *args, **kwargs):
        scenes=pg.filefolder
        self.fileNm=filePath.split("/")[-1]
        self.assetNm=self.__getAssetName()
        self.fileType=self.__getFileType()
        self.scenesDir="%s%s"%(filePath.split(scenes)[0],scenes)
        #self.versionsPath=self.__checkVersionsPath()
        self.version=self.__getVersionNum()
        self.__versionUp(filePath)

    #create Versions folder if it doesnt exist
    def __checkVersionsPath(self, *args, **kwargs):
        versionsPath="%s/Versions"%self.scenesDir
        assetVersionsPath="%s/%s"%(versionsPath, self.assetNm)
        for v in [versionsPath, assetVersionsPath]:
            self.__createFolder(v)
        return assetVersionsPath

    #use os to make folders for versions if they don't exist
    def __createFolder(self, folder, *args, **kwargs):
        if not os.path.exists(folder):
            print "CREATING VERSIONS FOLDER FOR: %s"%folder
            try:
                os.makedirs(folder)
            except:
                print "CANNOT CREATE FOLDER FOR: %s"%folder
        else:
            pass

    #count number of versions in folder
    def __getVersionNum(self, *args, **kwargs):
        pad=pg.padding
        #list all files in version folder
        versions=sorted(self.__versionsFilter(os.listdir(self.scenesDir)))
        #length of versions
        numVersions=len(versions)
        #check for latest version number
        if numVersions==0:
            return "1".zfill(pad)
        #if there are versions, get the latest based on the version number
        if numVersions>0:
            lastBase=versions[-1].split(".")[0]
            if lastBase[pad*(-1):].isdigit():
                last=int(lastBase.split("_v")[-1])
            else:
                last=0
            return str(last+1).zfill(pad)

    #return a list of files from the asset version folder
    def __versionsFilter(self, versions, *args, **kwargs):
        cleanLs=[]
        for v in versions:
            if self.assetNm in v:
                cleanLs.append(v)
        return cleanLs

    #clean up asset name removing extension and any version numbers
    def __getAssetName(self, *args, **kwargs):
        pad=pg.padding
        fileNm=self.fileNm.split(".")[0]
        #check if there is a version number extension
        if fileNm[pad*(-1):].isdigit():
            assetNm="_".join(fileNm.split("_")[:-1])
        else:
            assetNm="_".join(filter(None,fileNm.split("_"))) #if the asset name ends with an underscore, filter the empty string (None)
        #return name with no version number
        return assetNm

    #split the end off of absolute file name for the file extension
    def __getFileType(self, *args, **kwargs):
        return self.fileNm.split(".")[-1]

    #version up by moving current file to versions folder
    def __versionUp(self, filePath, *args, **kwargs):
        versionName="%s/%s_v%s.%s"%(self.scenesDir, self.assetNm, self.version, self.fileType)
        #print "%s >>> %s"%(filePath, versionName)
        ws = os.path.split(self.scenesDir)[0]
        print "SETTING PROJECT TO: %s"%ws
        mel.eval('setProject "{0}";'.format(ws))        
        #update to new version name and save
        mc.file(rn=versionName)
        mc.file(f=1,s=1)
