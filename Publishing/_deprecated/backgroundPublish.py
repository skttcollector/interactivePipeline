import sys
import os
from maya.standalone import initialize, uninitialize
import fnmatch

import maya.cmds as cmds
import maya.mel as mel

# import Utilities.utilityFunctions as uf

scriptsFolder = r"//caddy/work/current/FROGGER_MAGFL-N400/Frogger/Production/Code/Maya/Scripts/Python/Publishing"
sys.path.append(scriptsFolder)

def backgroundPublish(mbfolder, fbxfolder, *args):
    """
    folder is the location of the maya files to get
	fbxfolder is the location of the fbx folder to put
    """
    #set up the log file
    saveout = sys.stdout
    fsock = open("{0}/fbxPublish_masterLog.log".format(fbxfolder), "w")
    sys.stdout = fsock
    sys.stderr = fsock

    print "I'm here"
    
    print "-------starting mastering------"

    initialize("python")
    print "== initialized python"

    # uf.plugin_load("gameFbxExporter")

    mbs = fnmatch.filter(os.listdir(mbfolder), "*.mb")
    files = ["{0}/{1}".format(mbfolder, x) for x in mbs]

    # delete this
    cmds.file(files[-1], open=True)
    mel.eval('gameExp_DoExport;')

    # for x in files:
    # 	cmds.file(x, open=True)

    # for mb file in mb folder:
	    # OPEN FILE
	    # select assemblies
	    # open game export 
	    # load preset file
	    # export fbx



    # ---- old
    # cmds.file(rename=currentMaster)	
    # if os.path.isfile(currentMaster): #check if there is a master file currently. If so, move it to the past versions
    #     os.rename(currentMaster, destination)
    #     print "masterFuncs.masterShot:\n------ moving: {0} \n------ to: {1}".format(currentMaster, destination)
    # cmds.file(save=True, type="mayaAscii") # save as master
    # cmds.file(newFile=True, force=True)
    uninitialize()
    return("completed")

    print "== closing socket"
    #close out the log file
    sys.stdout = saveout
    fsock.close()

backgroundPublish(sys.argv[1], sys.argv[2])
