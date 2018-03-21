import os
from shutil import copy2 as copy2
import fnmatch
from functools import partial

import maya.cmds as cmds
import maya.mel as mel

import Utilities.utilityFunctions as uf
reload(uf)
import Utilities.projectGlobals as pg
reload(pg)
import setAndRunGameExporter as ge
reload(ge)


######
## this is half assed attempt at ui for which refs ot publish
########

# the fbx presets
anmPreset=pg.animFBXExport
rigPreset=pg.rigFBXExport

publishState = True

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
            cmds.warning("AssetPublish.check_correspondence:Couldn't find corresponding jnt and geo grps for: {0}! Aborting!".format(name))
            return()

    for geo in geoList:
        name = geo.split("_Geo_Grp")[0]
        if not cmds.objExists("{0}_Root_Jnt".format(name)):
            cmds.warning("AssetPublish.check_correspondence:Couldn't find corresponding jnt and geo grps for: {0}! Aborting!".format(name))
            return()


def get_reference_list_UI(versionUp=True, origScene=None, *args):
    if cmds.window("getRefWin", exists=True):
        cmds.deleteUI("getRefWin")

    win = cmds.window("getRefWin", t=" References to Export", w=400, h=300, rtf=True)
    cmds.scrollLayout(w=400, h=300)
    column = cmds.columnLayout(w=380, h=600)
    for ref in cmds.file(q=True, reference=True):
        rfn = cmds.referenceQuery(ref, rfn=True)
        cmds.checkBoxGrp(l=rfn, v1=True, cal=[(1, "left"), (2, "left")], cw=[(1, 350),(2, 25)])

    cmds.separator(h=20)
    but = cmds.button(l="Publish Files to MB and FBX!", w=380, h=30, c=partial(pull_refs_from_ui, column, versionUp, origScene))
    cmds.showWindow(win)

def pull_refs_from_ui(uiparent, versionUp=True, origScene=None, *args):
    references = []
    go = None
    # get children of ui (except last 2, sep adn button)
    children = cmds.columnLayout(uiparent, q=True, ca=True)[:-2]
    for cb in children:
        if cmds.checkBoxGrp(cb, q=True, v1=True):
            rfn = cmds.checkBoxGrp(cb, q=True, l=True)
            ref = cmds.referenceQuery(rfn, f=True)
            references.append(ref)

    if references:
        publish_fbx_anim_file(versionUp, origScene, references) 

    if cmds.window("getRefWin", exists=True):
        cmds.deleteUI("getRefWin")  


def publish_fbx_anim_file(versionUp=True, origScene=None, references=None, *args):
    """
    Assumes we're in an anim assembly scene that contains referenced rigs (only one namespace)
    This will spit out maya scenes that are ready for fbx export. One maya scene per reference object in the current scene, each of which contains only the mesh and joint groups that need to be exported. These scenes contain all available 'rigs' from that asset.
    Args:
        versionup (bool): whether we should version up the current scene
        origscene (string): the full path to the original scene we're trying to publish
    Returns:
        bool: whether we've run through all successfully
    """
    cmds.file(s=True)

    # check whether game exporter plugin is loaded, load if not
    uf.plugin_load("gameFbxExporter")

# check if there are any gmae export nodes, bail if not

    # version up
    if versionUp:
        verUpFile = get_version_up_name(origScene)
        copy2(origScene, verUpFile)
        print "===== Versioned up {0} to {1}!".format(origScene, verUpFile)
    else:
        print "===== Not versioning up publish of {0}".format(origScene) 

    if not origScene:
        cmds.warning("assetPublish.publish_fbx_anim_file: You haven't passed in a scene path!")
        publishState = False
        return()

    # assuming references
    refs = references
    if not refs:
        cmds.warning("There are no references in this scene. . .")
        publishState = False
        return()

    for ref in refs:
        pp = uf.PathParser(origScene)
        namespace = cmds.file(ref, q=True, ns=True)
        
        # assuming a NAMESPACE
        geoGrp = cmds.ls("{0}:GEO".format(namespace))
        jntGrp = cmds.ls("{0}:EXPORT_JNT_Grp".format(namespace))

        # check for geo grps
        if not geoGrp:
            cmds.warning("AssetPublish.publish_fbx_anim_file:You have no grp called 'GEO' -IN A NAMESPACE-.\n fbx export aborted!")
            publishState = False
            return()
        geos = child_match_check(geoGrp[0], "*_Geo_Grp")
        if not geos:
            publishState = False
            return()

        # check for jnt grps
        if not jntGrp:
            cmds.warning("AssetPublish.publish_fbx_anim_file:You either have no grp called 'EXPORT_JNT_Grp' -IN A NAMESPACE-.\n fbx export aborted!")
            publishState = False
            return()    
        roots = child_match_check(jntGrp[0], "*_Root_Jnt")
        if not roots:
            publishState = False
            return()

        # check correspondence of geo and root jnts
        correspond = check_correspondence(geos, roots)
        if not correspond:
            publishState = False
            return()

        # imports the reference
        cmds.file(ref, ir=True)

        # here's where we'd do the folder (figure out path stuff) - add the variant name
        pubFbxPath = uf.fix_path(os.path.join(pp.phasePath, "Publish/MB/{0}_v{1}".format(pp.variant, pp.versionString)))
        print "------- trying to make dirctory: {0}".format(pubFbxPath)
        if not os.path.exists(pubFbxPath):
            os.makedirs(pubFbxPath)
        tokens = pp.fileName.split("_")
        tokens[-2] = namespace

        start, end = uf.get_frame_range()

        # bake joints
        for r in roots:
            # get child roots if joints
            allD = cmds.listRelatives(r, allDescendents=True)
            jnts = [x for x in allD if cmds.objectType(x, isa="joint")]
            # function to bake selected on all jnts under this root
            bake_selected(jnts, start, end)

        # delete constraints
        cmds.delete(cmds.ls("{0}:*".format(namespace), type="constraint"))
        cmds.select(cl=True)

        # get list of roots in this ref
        fullKeepList = []
        for root in roots:
            basename = root.split(":")[1].split("_Root_Jnt")[0]
            geo = "{0}:{1}_Geo_Grp".format(namespace, basename)
            root = "{0}:{1}_Root_Jnt".format(namespace, basename)
            cmds.parent([geo, root], w=True)
            fullKeepList.append(geo)
            fullKeepList.append(root)
        cmds.select(fullKeepList, r=True)
        delete_other_top_level_nodes(cmds.ls(sl=True))

        try:
            cmds.namespace(mv=[namespace, ":"], f=True)
            cmds.namespace(rm=namespace)
        except:
            cmds.warning("NAMESPACE PROBLEM!", namespace)

        # collect the roots to export
        for root in roots:
            exportList = []
            basename = root.split(":")[1].split("_Root_Jnt")[0]
            geo = "{0}_Geo_Grp".format(basename)
            root = "{0}_Root_Jnt".format(basename)
            nodes = cmds.ls(type="gameFbxExporter")
            exportList.append(root)
            exportList.append(geo)
            for node in nodes:
                exportList.append(node)

            cmds.select(exportList, r=True)
            print "multiRefAnimExport.publish_fbx_anim_file: exporting -- \n {0}".format(exportList)
            # strip away namespace (if it's there)
            tokens[2] = basename
            pubFileName = "_".join(tokens)
            pubFilePath = uf.fix_path(os.path.join(pubFbxPath, pubFileName))

            # if this exists, should we overwrite?
            if os.path.isfile(pubFilePath):
                overwrite = cmds.confirmDialog(title="Overwrite Confirmation", message = "A publish FBX already exists for this file.\nShould we overwrite?", button = ("Overwrite", "Cancel"), defaultButton = "Overwrite", cancelButton = "Cancel", dismissString = "Cancel")

                if overwrite == "Cancel":
                    print "Publish skipped for FBX file (.fbx) called {0}".format(pubFilePath)
                    return() 

            print "===== anim publish:\n- saving {0}".format(pubFilePath)
            cmds.file(pubFilePath + ".mb", es=True, f=True, type="mayaBinary")

    publishState = True    


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


def delete_other_top_level_nodes(keeplist, *args):
    """
    deleles all other top level (in world) transform nodes. keeps the args list
    ARGS:
        keeplist (list) - a list of things to keep in the scene
    """
    for a in ["persp", "top", "front", "side"]:
        keeplist.append(a)
    allN = cmds.ls(assemblies=True)
    for x in allN:
        if x not in keeplist:
            try:
                cmds.delete(x)
            except:
                print "couldn't delete: {0}. Skipping!".format(x)


def delete_other_top_level_nodes_namespace(keeplist, namespace, *args):
    """
    deleles all other top level (in world) transform nodes that have the namespace. keeps the keeplist
    """
    for a in ["persp", "top", "front", "side"]:
        keeplist.append(a)
    allN = cmds.ls("{0}:".format(namespace), assemblies=True)
    for x in allN:
        if x not in keeplist:
            try:
                cmds.delete(x)
            except:
                print "couldn't delete: {0}. Skipping!".format(x)


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


def publish_fbx_folder(path, *args):
    """
    now go through the folder path and open each, open the gameexp, then populate the export path, then exportgo
    """
    pathP = uf.PathParser(path)
    mbpubpath = pathP.phasePath + "/Publish/MB/{0}_v{1}".format(pathP.variant, pathP.versionString)
    fbxpubpath = pathP.phasePath + "/Publish/FBX/{0}_v{1}".format(pathP.variant, pathP.versionString)

    # get the maya files
    mbFiles = fnmatch.filter(os.listdir(mbpubpath), "*.mb")

    for mb in mbFiles:
        mel.eval("gameFbxExporter;")
        print "========= multiRefAnimExport.publish_fbx_folder: opening {0}/{1}".format(mbpubpath, mb)
        cmds.file("{0}/{1}".format(mbpubpath, mb), open=True, f=True)

        # find anything that is not lining up with the file we've opened (ie. came in via export selected connections)
        lookfor = mb.split("_")[2]
        print "LOOK FOR: {0}".format(lookfor)
        exclude = ["persp", "top", "side", "front"]

        assemblies = cmds.ls(assemblies=True)
        print "ASSEMBLIES: ", assemblies
        for a in assemblies:
            if not a.startswith(lookfor) and (a not in exclude):
                print "------ deleting: ", a
                cmds.delete(a)

        cmds.file(s=True, f=True)
        filename = "{0}_{1}_{2}_{3}".format(pathP.name, pathP.variant, "_".join(mb.split("_")[3:-1]), "_".join(mb.split("_")[2:3]))

        if not os.path.isdir(fbxpubpath):
            os.makedirs(fbxpubpath)

        node = cmds.ls(type="gameFbxExporter")[-1]
        # set path and file name
        uf.set_gameExport_info(node, fbxpubpath, filename)

        # run exporter
        print "========= multiRefAnimExport.publish_fbx_folder: trying to publish FBX {0}/{1}".format(mbpubpath, mb)
        mel.eval("gameExp_DoExport;")


def stagePublish(versionUp=True, *args):
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
   
    # # publish the current maya scene to Publish folder
    # if pp.phase in ["Animation"] and pp.stage=="Work":
    #     mayapub = publish_maya_scene(versionUp, origScene)
    #     if not mayapub: # i.e. we've failed somewhere in the func
    #        return()
    # else:
    #     print "===== not doing standard maya anim publish, since you're in {0} phase and {1} stage of the pipeline".format(pp.phase, pp.stage)

    # if it's an anm work file
    if pp.phase in ["Animation"] and pp.stage=="Work":
        get_reference_list_UI(versionUp, origScene)
    if not publishState:
        cmds.warning("There was an issue publishing the assets somewhere. Leaving multiref publishing!")
        return()


    publish_fbx_folder(origScene)

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
    
    if cmds.window("gameExporterWindow", exists=True):
        cmds.deleteUI("gameExporterWindow")

