import os
from shutil import copy2 as copy2
import fnmatch

import maya.cmds as cmds
import maya.mel as mel

import Utilities.utilityFunctions as uf
reload(uf)
import Utilities.projectGlobals as pg
reload(pg)

# the fbx presets
anmPreset=pg.animFBXExport
rigPreset=pg.rigFBXExport

def publish_maya_scene(versionUp=True, origScene=None, *args):
    """
    only do for rigging and modeling phase of assets
    ARGS:
        versionUp (bool): whether to version up the maya scene
        origScene (string): the full path to the file to publish
    """
    if not origScene:
        cmds.warning("assetPublish.publish_maya_scene: You haven't passed in a scene path!")
        return(False)

    pp = uf.PathParser(origScene)
    cmds.file(s=True)

    sel = cmds.ls(sl=True)
    if not sel:
        cmds.warning("assetManager.publish_maya_scene: You haven't selected anything in your scene. Please select what you wish to publish. (hint: for models, your geo/geo grp. For rigs, usually it will be your char group and ctrl set)")
        return(False)

    if versionUp:
        verUpFile = get_version_up_name(origScene)

    # parse the new path/name for publish(current scene)
    pubPath =  uf.fix_path(os.path.join(pp.phasePath, "Publish/MB/"))
    tokens = pp.fileName.split("_")
    tokens[-2] = "Publish"
    pubFileName = "_".join(tokens)
    pubFilePath = uf.fix_path(os.path.join(pubPath, pubFileName))

    if os.path.isfile(pubFilePath):
        overwrite = cmds.confirmDialog(title="Overwrite Confirmation", message = "A publish MB already exists for this file.\nShould we overwrite?", button = ("Overwrite", "Cancel"), defaultButton = "Overwrite", cancelButton = "Cancel", dismissString = "Cancel")

        if overwrite == "Cancel":
            print "Publish skipped (no overwrite) for maya file (.mb) stage of {0}".format(pubFilePath)
            return(True)

    if versionUp:
        # in background copy the orig to the new version 
        # (essentially just versioning up while staying in old version)
        copy2(origScene, verUpFile)
        print "===== Versioned up {0} to {1}!".format(origScene, verUpFile)
    else:
        print "===== Not versioning up publish of {0}".format(origScene)        

    # export selection to publish file
    print "===== AssetPublish.publish_maya_scene: Preparing to export items to publish file: {0}".format(sel)
    export = cmds.file(pubFilePath, exportSelected=True, type="mayaBinary")
    if export==pubFilePath:
        print "===== AssetPublish.publish_maya_scene: Succesfully published file to: {0}".format(pubFilePath)
    return(True)


def get_version_up_name(origScene, *args):
    """
    from orig scene (assuming it's compatible with pipe) will return the fullpath to next version
    """
    pp2 = uf.PathParser(origScene)
    verNum = int(origScene[-7:-3])
    pp2.get_version_info()
    nums = pp2.versionNumbers
    newNum = nums[-1]+1

    verUpFile = "{0}{1}{2}".format(origScene[:-7], str(newNum).zfill(4),".mb")
    return(verUpFile)


def check_correspondence(geoList, jntList):
    """
    checks that a geo grp exists for each root jnt grp and visa versa
    """
    for jnt in jntList:
        name = jnt.split("_Root_Jnt")[0]
        if not cmds.objExists("{0}_Geo_Grp".format(name)):
            cmds.warning("AssetPublish.publish_fbx_file:Couldn't find corresponding jnt and geo grps for: {0}! Aborting!".format(name))
            return(False)

    for geo in geoList:
        name = geo.split("_Geo_Grp")[0]
        if not cmds.objExists("{0}_Root_Jnt".format(name)):
            cmds.warning("AssetPublish.publish_fbx_file:Couldn't find corresponding jnt and geo grps for: {0}! Aborting!".format(name))
            return(False)

    return(True)


def publish_fbx_rig_file(versionUp=True, origScene=None, *args):
    """
    requires an EXPORT_JNT_Grp group with one root for each export rig named: 'name_Root_Jnt'
    requires a GEO group with one folder for each export rig named: 'name_Geo_Grp'
    names should correspond ("fish_Root_Jnt", "fish_Geo_Grp")
    """
    # all happens in current:
    if not origScene:
        cmds.warning("assetPublish.publish_fbx_rig_file: You haven't passed in a scene path!")
        return(False)

    pp = uf.PathParser(origScene)

    geoGrp = cmds.ls("GEO")
    jntGrp = cmds.ls("EXPORT_JNT_Grp")

    # check for geo grps
    if not geoGrp or len(geoGrp)>1:
        cmds.warning("AssetPublish.publish_fbx_rig_file:You either have no grp called 'GEO', or too many objects called 'GEO'.\n fbx export aborted!")
        return(False)
    geos = child_match_check(geoGrp, "*_Geo_Grp")
    if not geos:
        return(False)

    # check for jnt grps
    if not jntGrp or len(jntGrp)>1:
        cmds.warning("AssetPublish.publish_fbx_rig_file:You either have no grp called 'EXPORT_JNT_Grp', or too many objects called 'EXPORT_JNT_Grp'.\n fbx export aborted!")
        return(False)    
    roots = child_match_check(jntGrp, "*_Root_Jnt")
    if not roots:
        return(False)

    # check correspondence
    correspond = check_correspondence(geos, roots)
    if not correspond:
        return(False)

    pubFbxPath = uf.fix_path(os.path.join(pp.phasePath, "Publish/FBX/"))
    tokens = pp.fileName.split("_")
    tokens[-2] = "Publish"
    pubFileName = "_".join(tokens)[:-3] + ".fbx"
    pubFilePath = uf.fix_path(os.path.join(pubFbxPath, pubFileName))

# check if there's any animation in the file (time based), abort if there is
# check for references, etc. . 

    # delete constraints
    cmds.delete(cmds.ls(type="constraint"))
    cmds.select(cl=True)
    # move jnts and geo into world parent
    for root in roots:
        basename = root.split("_Root_Jnt")[0]
        geo = "{0}_Geo_Grp".format(basename)
        cmds.parent([geo, root], w=True)
        # create filename
        tokens[-2] = basename
        pubFileName = "_".join(tokens)[:-3] + ".fbx"
        pubFilePath = uf.fix_path(os.path.join(pubFbxPath, pubFileName))
        cmds.select([root, geo], r=True)

        # if this exists, should we overwrite?
        if os.path.isfile(pubFilePath):
            overwrite = cmds.confirmDialog(title="Overwrite Confirmation", message = "A publish FBX already exists for this file.\nShould we overwrite?", button = ("Overwrite", "Cancel"), defaultButton = "Overwrite", cancelButton = "Cancel", dismissString = "Cancel")

            if overwrite == "Cancel":
                print "Publish skipped for FBX file (.fbx) called {0}".format(pubFilePath)
                return(True) 

        mel.eval('FBXLoadExportPresetFile -f "{0}";'.format(rigPreset))
        mel.eval('FBXExport -f "{0}" -s'.format(pubFilePath))

    return(True)


def publish_fbx_anim_file(versionUp=True, origScene=None, *args):
    # THIS IS FOR ANIM EXPORTING

# save current scene
# move this to end and use Zed's script to version up afterwards? ? maybe?
    # version up
    if versionUp:
        verUpFile = get_version_up_name(origScene)
        copy2(origScene, verUpFile)
        print "===== Versioned up {0} to {1}!".format(origScene, verUpFile)
    else:
        print "===== Not versioning up publish of {0}".format(origScene) 

    if not origScene:
        cmds.warning("assetPublish.publish_fbx_anim_file: You haven't passed in a scene path!")
        return(False)

# assuming references
    refs = cmds.file(q=True, r=True)
    if not refs:
        cmds.warning("There are no references in this scene. . .")
        return(False)
    if len(refs) > 1:
        cmds.warning("There are too many references in this scene. . .")
        return(False)
# below would all be under a for loop for each reference in the stages? 
    pp = uf.PathParser(origScene)

# assuming a namespace
    geoGrp = cmds.ls("*:GEO")
    jntGrp = cmds.ls("*:EXPORT_JNT_Grp")

    # check for geo grps
    if not geoGrp or len(geoGrp)>1:
        cmds.warning("AssetPublish.publish_fbx_anim_file:You either have no grp called 'GEO' -IN A NAMESPACE-, or too many objects called 'GEO'.\n fbx export aborted!")
        return(False)
    geos = child_match_check(geoGrp[0], "*_Geo_Grp")
    if not geos:
        return(False)

    # check for jnt grps
    if not jntGrp or len(jntGrp)>1:
        cmds.warning("AssetPublish.publish_fbx_anim_file:You either have no grp called 'EXPORT_JNT_Grp' -IN A NAMESPACE-, or too many objects called 'EXPORT_JNT_Grp'.\n fbx export aborted!")
        return(False)    
    roots = child_match_check(jntGrp[0], "*_Root_Jnt")
    if not roots:
        return(False)

    cmds.file(refs[0], ir=True)

    # check correspondence of geo and root jnts
    correspond = check_correspondence(geos, roots)
    if not correspond:
        return(False)

    pubFbxPath = uf.fix_path(os.path.join(pp.phasePath, "Publish/FBX/"))
    tokens = pp.fileName.split("_")
    tokens[-2] = "Publish"
    pubFileName = "_".join(tokens)[:-3] + ".fbx"
    pubFilePath = uf.fix_path(os.path.join(pubFbxPath, pubFileName))

    start, end = uf.get_frame_range()

    # bake joints
    for r in roots:
        # get child roots if joints
        allD = cmds.listRelatives(r, allDescendents=True)
        jnts = [x for x in allD if cmds.objectType(x, isa="joint")]
        # function to bake selected on all jnts under this root
        bake_selected(jnts, start, end)

    namespace = cmds.file(refs[0], q=True, ns=True)
    uf.remove_namespaces()

    # delete constraints
    cmds.delete(cmds.ls(type="constraint"))
    cmds.select(cl=True)
    # move jnts and geo into world parent
    for root in roots:
        rootremove = "{0}:".format(namespace)
        basename = root.split(":")[1].split("_Root_Jnt")[0]
        geo = "{0}_Geo_Grp".format(basename)
        root = "{0}_Root_Jnt".format(basename)
        cmds.parent([geo, root], w=True)
        tokens[-2] = basename
        pubFileName = "_".join(tokens)[:-3] + ".fbx"
        pubFilePath = uf.fix_path(os.path.join(pubFbxPath, pubFileName))
        rootremove = "{0}:".format(namespace)
        cmds.select([root, geo], r=True)

        # if this exists, should we overwrite?
        if os.path.isfile(pubFilePath):
            overwrite = cmds.confirmDialog(title="Overwrite Confirmation", message = "A publish FBX already exists for this file.\nShould we overwrite?", button = ("Overwrite", "Cancel"), defaultButton = "Overwrite", cancelButton = "Cancel", dismissString = "Cancel")

            if overwrite == "Cancel":
                print "Publish skipped for FBX file (.fbx) called {0}".format(pubFilePath)
                return(True) 

        mel.eval('FBXLoadExportPresetFile -f "{0}";'.format(anmPreset))
        mel.eval('FBXExport -f "{0}" -s'.format(pubFilePath))

    return(True)    

    # for stages:
    # loop through namespaces/references:
    #   import reference
    #   delete namespace
    #   loop through joint grps, geo grps:
    #       bake jnts
    #       clean up joints shit

    #       "CloudStage_Tree_main_Rig1_A_v0001.fbx"
    #           stage     asset ns    subgrp  version
        
    #       check for version folder, create it if it doesn't exist


def bake_selected(bakeList, start, end, *args):
    """
    bakes objects (joints) in given list
    """
    for j in bakeList:
        attr=["t","r","s"]
        co=["x","y","z"]
        attrLs=[]
        for at in attr:
            for c in co:
                attrLs.append("%s.%s%s"%(j,at,c))
        for x in attrLs:
            try:
                cmds.setAttr(x, k=1)
            except:
                pass

    cmds.bakeResults(bakeList, t=(start, end), sm=1, sb=1, sac=0, mr=0)


def child_match_check(topNode, childString, *args):
    """
    returns a list of children of the top node that match the childstring
    """
    children = cmds.listRelatives(topNode, c=True)
    if not children:
        cmds.warning("AssetPublish.child_match_check:Couldn't find anything under {0}! Aborting!".format(topNode))
        return(None)
    goodChildren = fnmatch.filter(children, childString)
    if not goodChildren:
        cmds.warning("AssetPublish.child_match_check:Couldn't find objects with '{0}' under {1}! Aborting!".format(childString, topNode))
        return(None)
    return(goodChildren)


def assetPublish(versionUp=True, *args):
    """
    checks the current scene if it's compatible, if not kick out
    ARGS:
        versionUp (bool): whether to version up the work file on publish
    """
    origScene = cmds.file(q=True, sn=True)
    pp = uf.PathParser(origScene)

    # bail if current scene is not compatible
    if not pp.compatible:
        cmds.warning("assetPublish.publish_maya_scene: You're not in a project compatible scene! Sorry. See a TD")
        return()
   
    # if it's not a stage file or a publish file and it's either modeling or rigging phase
    if pp.assetType != "Stages" and pp.phase in ["Rigging", "Modeling"] and pp.stage=="Work":
        mayapub = publish_maya_scene(versionUp, origScene)
        if not mayapub: # i.e. we've failed somewhere in the func
           return()
    else:
        print "===== skipping maya scene publish, since you're in {0} phase and {1} stage of the pipeline".format(pp.phase, pp.stage)

    # if it's a rig work file
    if pp.assetType != "Stages" and pp.phase in ["Rigging"] and pp.stage=="Work":
        fbxPub = publish_fbx_rig_file(versionUp, origScene)
        if not fbxPub:
            return()

    # if it's an anm work file
    if pp.assetType != "Stages" and pp.phase in ["Animation"] and pp.stage=="Work":
        fbxPub = publish_fbx_anim_file(versionUp, origScene)
        if not fbxPub:
            return()

    if versionUp:
        verNum = int(pp.path[-7:-3])
        pp.get_version_info()
        nums = pp.versionNumbers
        newNum = nums[-1]

        verUpFile = "{0}{1}{2}".format(origScene[:-7], str(newNum).zfill(4),".mb")

        if os.path.isfile(verUpFile):
            print "assetPublish.assetPublish: Opening version up file:", verUpFile
            cmds.file(verUpFile, open=True, force=True)
        else:
            print "assetPublish.assetPublish: Couldn't find version up, opening original file: ",pp.path
            cmds.file(pp.path, open=True, force=True)
    else:
        print "assetPublish.assetPublish: Opening original file: ",pp.path 
        cmds.file(pp.path, open=True, force=True)