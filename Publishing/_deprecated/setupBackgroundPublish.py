import subprocess as sub
import maya.cmds as cmds
import sys
import os

userScript = cmds.internalVar(usd=True)

mbfolder = r"X:/Production/Assets/3D/Character/testAsset/Animation/Publish/MB/cloudTest_v0001"
fbxfolder = r"X:/Production/Assets/3D/Character/testAsset/Animation/Publish/FBX/cloudTest_v0001"

if not os.path.isdir(fbxfolder):
    os.mkdir(fbxfolder)

mayapy = "C:/Program Files/Autodesk/Maya2016/bin/mayapy.exe"
bgscript = "X:/Production/Code/Maya/Tools/PipelineTools/Python/Publishing/backgroundPublish.py"

sub.Popen([mayapy, bgscript, mbfolder, fbxfolder])

