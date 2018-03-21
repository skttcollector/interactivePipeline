#save file with automatic versioning
import maya.cmds as mc
import os

import Utilities.versionFile as vf

ver = vf.versionClass()

def run(*args, **kwargs):
    filePath=mc.file(q=1, l=1)[0]
    ver.versionUp(filePath)

"""
#create Versions folder if it doesnt exist
def __checkVersionsPath(path, assetNm, *args, **kwargs):
    versionsPath="%s/Versions"%path
    assetVersionsPath="%s/%s"%(versionsPath, assetNm)
    __createFolder(versionsPath)
    __createFolder(assetVersionsPath)
    return assetVersionsPath

def __createFolder(folder, *args, **kwargs):
    if not os.path.exists(folder):
        print "CREATING VERSIONS FOLDER FOR: %s"%folder
        try:
            os.makedirs(folder)
        except:
            print "CANNOT CREATE FOLDER FOR: %s"%folder
    else:
        pass

def __getVersionNum(path, assetNm, padding, *args, **kwargs):
    #list all files in version folder
    versions=__versionsFilter(os.listdir(path), assetNm)
    #length of versions
    numVersions=len(versions)
    #check for latest version number
    if numVersions==0:
        return "1".zfill(padding)
    if numVersions>0:
        versions.sort()
        last=int(versions[-1].split(".")[0].split("_v")[-1])
        return str(last+1).zfill(padding)

#return a list of files from the asset version folder
def __versionsFilter(versions, fileNm):
    cleanLs=[]
    for v in versions:
        if fileNm in v:
            cleanLs.append(v)
    return cleanLs

#clean up asset name removing extension and any version numbers
def __getAssetName(fileNm, padding, *args, **kwargs):
    assetNm=fileNm.split(".")[0]
    #check if there is a version number extension
    if fileNm[padding*-1:].isdigit():
        assetNm="_".join(fileNm.split("_")) 
    else:
        pass
    #return name with no version number
    return assetNm

def __getFileType(fileNm, *args, **kwargs):
    return fileNm.split(".")[-1]

#version up by moving current file to versions folder
def __versionUp(scenesDir, filePath, versionsPath, assetNm, version, fileType, *args, **kwargs):
    versionName="%s_v%s.%s"%(assetNm, version, fileType)
    srcPath="%s/%s"%(scenesDir, versionName)
    targetPath="%s/%s"%(versionsPath, versionName)
    #print "%s >>> %s"%(filePath, nextFileVersionPath)
    os.rename(filePath, targetPath)
    mc.file(f=1,s=1)
"""