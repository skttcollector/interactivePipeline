import os
import re
import maya.cmds as cmds
import fnmatch

import Utilities.projectGlobals as pg

# relevant environment variables set by "setProject" script: MAYA_CURRENT_PROJECT, MAYA_PROJECT_PATH

def fix_path(path):
    """
    changes "\" to "/" in file path
    Args:
        path (string) - the path to fix
    Returns:
        string - the fixed path
    """
    newPath = path.replace("\\", "/")
    return(newPath)


class PathParser(object):
    """
    this is for a specific file path to extract info about the file and it's related stuff
    ARGS:
        path (string) - the file path to a specific file in the pipeline
    """
    def __init__(self, path):

        self.path = fix_path(path) # ex. X:/Production/Assets/3D/Character/Fish/Rigging/Publish/MB/Fish_main_Rigging_Publish_v0005.mb
        self.compatible = True
        # checks drive and file name to see it's valid
        projFormat = self.check_format(self.path)
        if projFormat:
            self.get_path_info(self.path)
        else:
            self.compatible = False
            #cmds.warning("Utitities.utilityFunctions.PathParser: The path you've provided doesn't fit our project specs. See a TD")

    def get_path_info(self, path):
        pad = pg.padding
        if self.compatible:
            if fnmatch.fnmatch(self.path, "*{*}"):
                noBrackets = path.partition("{")[0]
                self.fileName = noBrackets.split("/")[-1]
            else:
                self.fileName = path.split("/")[-1] # ex. Fish_main_Rigging_Publish_v0005.mb
            
            self.path = path  
            self.name = self.fileName.split("_")[0] # ex. Fish
            self.variant = self.fileName.split("_")[-4] # ex. main
            self.phase = self.fileName.split("_")[-3] # ex. Rigging
            self.stage = self.fileName.split("_")[-2] # ex. Publish
            self.versionString = self.fileName.split("_")[-1].partition(".")[0][1:] # ex. "0005"
            self.versionNum = int(self.fileName.split("_")[-1].partition(".")[0][1:]) # ex. 5
            self.assetPath = fix_path("/".join(path.split("/")[:-1])) # ex. X:/Production/Assets/3D/Character/Fish/
            # get the asset type (stage or assets differ) [this is kind of a hack]
            self.assetType = os.path.basename(fix_path("/".join(self.assetPath.split("/")[:-5]))) # ex. ""
            if self.assetType == "Production":
                self.assetType = "Stages"
                self.assetPath = fix_path("/".join(path.split("/")[:-5]))
            # get the phase path (stage or asset differ)
            if self.assetType in ["Character", "Props", "Sets"]:
                self.phasePath = fix_path("/".join(path.split("/")[:7])) # ex. X:/Production/Assets/3D/Character/Fish/Rigging
            else:
                self.phasePath = fix_path("/".join(path.split("/")[:5])) # ex. X:/Production/Stages/CloudStage/Animation
            
            if fnmatch.fnmatch(path, "*{*}"):
                noBrackets = path.partition("{")[0]
                self.pathNoNum = noBrackets[:-7]
            else:
                self.pathNoNum = path[:-7]
            # get the stage path to find the correct maya files
            if self.stage == "Work":
                if self.assetType != "Stages":
                    self.stagePath = fix_path("/".join(path.split("/")[:-1])) # ex. X:/Production/Assets/3D/Character/Fish/Rigging/Work/Maya/scenes
                else:
                    self.stagePath = fix_path("/".join(path.split("/")[:-1])) # ex. X:/Production/Stages/CloudStage/Animation/Production/Maya/scenes
            else:
                self.stagePath = fix_path("/".join(path.split("/")[:-1])) # ex. X:/Production/Assets/3D/Character/Fish/Rigging/Publish/MB
            self.refPath = self.path

            # if fnmatch.fnmatch(self.path, "*{*}"):
            #     self.refPath = self.path[:-3]
            checkpaths = [self.assetPath, self.phasePath, self.stagePath]
            # for p in checkpaths:
            #     print p
            for p in checkpaths:
                if not os.path.isdir(p):
                    cmds.warning("Utitities.utilityFunctions.PathParser: The path I've calculated doesnt' exist. See a TD: {0}".format(p))


    def get_variants_list(self):
        """
        gets all the variant names in the given path's stage path
        """
        varList = []
        if self.compatible:
            dirContents = sorted([fix_path(os.path.join(self.stagePath, x)) for x in os.listdir(self.stagePath)])
            if dirContents:
                for file in dirContents:
                    comp = self.check_format(file)
                    if comp:
                        var = file.split("_")[:-3][1]
                        varList.append(var)

        varList = sorted(list(set(varList)))
        self.variantList = varList


    def get_version_info(self):
        """
        sets all the versioning info in the object based on the stagepath and file names("X:/Production/Fish_main_RIgging_Work_v0001.mb") 
        """
        if self.compatible:
            allVersions = sorted([x for x in os.listdir(self.stagePath)])
            if allVersions:
                self.versions = fnmatch.filter(allVersions, "{0}*".format(self.fileName.split(".")[0][:-6])) # list of versions ex. ["Fish_main_Rigging_Publish_v0005.mb", "Fish_main_Rigging_Publish_v0006.mb"]
                self.versionNumbersString = [x[-7:-3] for x in self.versions] # strings of the version numbers ex. ["0001", "0002"]
                self.versionNumbers = [int(x[-7:-3]) for x in self.versions] # ints of the version numbers ex. [1, 2]
                # if nothing there, then returns empty list


    def check_format(self, path):
        """
        checks if the path is in the format we need... 
        """
        projectPath = os.environ["MAYA_PROJECT_PATH"] # ex "X:/Production"
        # for now check that it's on the the x drive, in Production
        regex = r"\b(?:[\w]+_){4}v\d{4}\.mb\b"   
        test_str = path
        matches = re.search(regex, test_str, re.IGNORECASE)

        if matches and "/".join(path.split("/")[:2]) == projectPath:
            return(True)
        else:
            return(False)


def get_top_nodes(objects = [], *args):
    """
    from given list of objects return a list of the top nodes in DAG hierarchy
    Args:
        objects (list): list of scene objects
    Return:
        list: any top nodes of the given objects 
    """ 
    roots = []
    
    for objs in objects:
        obj = ""
        if cmds.objectType(objs)=="transform":
            obj = cmds.ls(objs, l=True, dag=True)[0]
        if obj:
            root = (obj.split("|")[:2])
        if root:
            if len(root) > 1 and root[1] not in roots:
                roots.append(root[1])

    return(roots)


def remove_namespaces(*args):
    """
    looks in the current scene and removes namespaces
    """
    defaults = ['UI', 'shared']

    def num_children(ns): #function to used as a sort key
        return ns.count(':')

    namespaces = [ns for ns in cmds.namespaceInfo(lon=True, r=True) if ns not in defaults]

    namespaces.sort(key=num_children, reverse=True) # reverse the list

    for ns in namespaces:
        try:
            #get contents of namespace and move to root namespace
            cmds.namespace(mv=[ns, ":"], f=True)
            cmds.namespace(rm=ns)
        except RuntimeError as e:
            # namespace isn't empty, so you might not want to kill it?
            cmds.warning("couldn't delete: {0}\n{1}".format(ns, e))
    return(namespaces)


def get_frame_range(*args):
    start = float(cmds.playbackOptions(q=True, min=True))
    end = float(cmds.playbackOptions(q=True, max=True))
    return(start, end)


def check_for_good_name(name, *args):
    if "_" in name:
        return(False)
    return(True)


def plugin_load(plugin, *args):
    """
    checks whether plugin is loaded. Loads it if not
    Args: 
        plugin (string): actual name of plugin to check for
    """
    loaded = cmds.pluginInfo(plugin, q=True, loaded=True)
    if not loaded:
        cmds.loadPlugin(plugin)


def set_gameExport_info(gameExpNode, filepath, filename, *args):
    # set path and file
    cmds.setAttr("{0}.exportPath".format(gameExpNode), filepath, type="string")
    cmds.setAttr("{0}.exportFilename".format(gameExpNode), filename, type="string")

    # check and set values
    #cmds.setAttr("{0}.overridePresetValue".format(gameExpNode), 1) # override settings
    cmds.setAttr("{0}.embedMedia".format(gameExpNode), 0)
    cmds.setAttr("{0}.triangulate".format(gameExpNode), 1)
    cmds.setAttr("{0}.fileSplitType".format(gameExpNode), 1) # save to single file
    cmds.setAttr("{0}.bakeAnimation".format(gameExpNode), 0) # don't bake anim
    cmds.setAttr("{0}.exportSetIndex".format(gameExpNode), 1) # export all
    cmds.setAttr("{0}.inputConnections".format(gameExpNode), 0) # no input connections
    cmds.setAttr("{0}.fileType".format(gameExpNode), 0) # set to binary
