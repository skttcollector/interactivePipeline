#save file with automatic versioning
import maya.cmds as mc
import os

import maya.cmds as mc
import os

import Utilities.versionFile as vf
import Utilities.getFilePath as gfp

ver=vf.versionClass()

def run(*args, **kwargs):
    #0=save file for the get file fucntion
    filePath=gfp.getFilePath(0)
    ver.versionUp(filePath)