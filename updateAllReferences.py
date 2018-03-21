import maya.cmds as cmds

import Utilities.projectGlobals as pg
import Utilities.utilityFunctions as uf

import os
import fnmatch

def update_all_references(*args):
    
# if scene is modded, should we save? 
    mod = cmds.file(q=True, modified=True)
    if mod:
        test = save_current_dialog()
        if not test:
            return()
            
    # get all refs
    refs = cmds.file(q=True, r=True)

    # # for each ref file
    for ref in refs:
        # make path object
        print "updateAllReferences: checking: {0}".format(ref)
        rfn = cmds.file(ref, q=True, rfn=True)
        path = None
        pathparse = uf.PathParser(ref)
        if pathparse.compatible:
            brackets = ""
            if fnmatch.fnmatch(ref, "*{*}"):
                parts = ref.partition("{")
                brackets = parts[1] + parts[2]
            # get current version string
            thisVer = pathparse.versionString
            #   get the version list for that file
            pathparse.get_version_info()
            print "Current: {0} vs. {1}".format(thisVer, pathparse.versionNumbersString[-1])
            if thisVer != pathparse.versionNumbersString[-1]:
                print "----- updating {1} to version {1}".format(rfn, pathparse.versionNumbersString[-1])
                path = pathparse.pathNoNum + pathparse.versionNumbersString[-1] + ".mb" + brackets
                cmds.file(path, loadReference=rfn, type="mayaBinary")
        else:
            print "Not a pipeline compatible ref. Skipping! -- {0}".format(ref)
        
        pathparse = None


def save_current_dialog(*args):
    save = cmds.confirmDialog(title="Save Confirmation", message = "Save current scene?", button = ("Save", "Don't Save", "Cancel"), defaultButton = "Save", cancelButton = "Cancel", dismissString = "Cancel")
    if save == "Save":
        cmds.file(save=True)
        return(True)
    elif save == "Don't Save":
        return(True)
    else:
        return(False)