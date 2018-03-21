import os
import sys
import maya.cmds as cmds
import Utilities.utilityFunctions as uf

# this is for the project as a whole to gather info on folders and files, fix paths, etc

# TODO - dummy check that the folder exists? 

class AssetInfo(object):
    def __init__(self):
        if "MAYA_PROJECT_PATH" in os.environ:
            self.basePath = os.environ["MAYA_PROJECT_PATH"]
        else: 
            # self.basePath = "X:/Production"
            cmds.warning("assetInfo.__init__: couldn't find the MAYA_PROJECT_PATH environment variable. See a TD!")

        self.charPath = uf.fix_path(os.path.join(self.basePath, "Assets/3D/Character/"))
        self.propPath = uf.fix_path(os.path.join(self.basePath, "Assets/3D/Props/"))
        self.setPath = uf.fix_path(os.path.join(self.basePath, "Assets/3D/Sets/"))
        self.stagePath = uf.fix_path(os.path.join(self.basePath, "Stages/"))

        self.get_asset_path_lists()

    def get_asset_path_lists(self, *args):
        """
        find the lists of assets in the folders, also gets the stage list
        """
        self.charsPaths = sorted([uf.fix_path(os.path.join(self.charPath, y)) for y in os.listdir(self.charPath)], key=str.upper)
        self.propsPaths = sorted([uf.fix_path(os.path.join(self.propPath, y)) for y in os.listdir(self.propPath)], key=str.upper)
        self.setsPaths = sorted([uf.fix_path(os.path.join(self.setPath, y)) for y in os.listdir(self.setPath)], key=str.upper)
        self.stagesPaths = sorted([uf.fix_path(os.path.join(self.stagePath, y)) for y in os.listdir(self.stagePath)], key=str.upper)

        # clean 
        for lst in [self.charsPaths, self.propsPaths, self.setsPaths, self.stagesPaths]:
            for x in lst:
                if not os.path.isdir(x):
                    lst.remove(x)

    def get_asset_name_list(self, *args):
        """
        gets lists of the basenames (i.e. "Fish") of the assets, also gets stages
        Returns:
            list of:
                char (list) - list of char names
                props (list) - list of prop names
                sets (list) - list of set names
                stages (list) - list of stage names
                i.e. [["Fish", "Cube"],["Ball"],["Waterfall"],["CloudStage"]]
        """
        exclude = ["~StageTemplate~", "_Backup", "_old", "~.txt"]
        self.chars = [os.path.basename(x) for x in self.charsPaths if os.path.basename(x) not in exclude]
        self.props = [os.path.basename(x) for x in self.propsPaths if os.path.basename(x) not in exclude]
        self.sets = [os.path.basename(x) for x in self.setsPaths if os.path.basename(x) not in exclude]
        self.stages = [os.path.basename(x) for x in self.stagesPaths if os.path.basename(x) not in exclude]
        return(self.chars, self.props, self.sets, self.stages)

    def get_asset_contents(self, assetpath, *args):
        """
        get asset file contents for each area
        Args:
            assetpath (string) - the path to the top level of the asset folder ("X://.../Production/Assets/3D/Character/Fish")
        """
        exclude = ["0.txt", "edits", "incremental", "_old"]
        self.anmPath = uf.fix_path(os.path.join(assetpath, "Animation/Work/Maya/scenes"))
        self.lgtPath = uf.fix_path(os.path.join(assetpath, "Lighting/Work/Maya/scenes"))
        self.mdlPath = uf.fix_path(os.path.join(assetpath, "Modeling/Work/Maya/scenes"))
        self.rigPath = uf.fix_path(os.path.join(assetpath, "Rigging/Work/Maya/scenes"))
        self.txtPath = uf.fix_path(os.path.join(assetpath, "Texturing/Work/Maya/scenes"))

        self.anmPubPath = uf.fix_path(os.path.join(assetpath, "Animation/Publish/MB/"))
        self.lgtPubPath = uf.fix_path(os.path.join(assetpath, "Lighting/Publish/MB/"))
        self.mdlPubPath = uf.fix_path(os.path.join(assetpath, "Modeling/Publish/MB/"))
        self.rigPubPath = uf.fix_path(os.path.join(assetpath, "Rigging/Publish/MB/"))
        self.txtPubPath = uf.fix_path(os.path.join(assetpath, "Texturing/Publish/MB/"))

        self.anmWorkFiles = [f for f in os.listdir(self.anmPath) if (os.path.isfile(os.path.join(self.anmPath, f)) and f not in exclude)]
        self.lgtWorkFiles = [f for f in os.listdir(self.lgtPath) if (os.path.isfile(os.path.join(self.lgtPath, f)) and f not in exclude)]
        self.mdlWorkFiles = [f for f in os.listdir(self.mdlPath) if (os.path.isfile(os.path.join(self.mdlPath, f)) and f not in exclude)]
        self.rigWorkFiles = [f for f in os.listdir(self.rigPath) if (os.path.isfile(os.path.join(self.rigPath, f)) and f not in exclude)]
        self.txtWorkFiles = [f for f in os.listdir(self.txtPath) if (os.path.isfile(os.path.join(self.txtPath, f)) and f not in exclude)]

        self.anmPubFiles = [f for f in os.listdir(self.anmPubPath) if f not in exclude]
        # self.lgtPubFiles = [f for f in os.listdir(self.lgtPubPath) if (os.path.isfile(os.path.join(self.lgtPubPath, f)) and f not in exclude)]
        self.mdlPubFiles = [f for f in os.listdir(self.mdlPubPath) if  f not in exclude]
        self.rigPubFiles = [f for f in os.listdir(self.rigPubPath) if f not in exclude]
        # self.txtPubFiles = [f for f in os.listdir(self.txtPubPath) if (os.path.isfile(os.path.join(self.txtPubPath, f)) and f not in exclude)]


    def get_stage_contents(self, stagepath, *args):
        exclude = ["0.txt", "edits"]
        self.stageAnmPath = uf.fix_path(os.path.join(stagepath, "Animation/Production/Maya/scenes"))
        # self.stageAudPath = os.path.join(stagepath, "Audio/Production/Maya/scenes")
        # self.stageFxPath = os.path.join(stagepath, "FX/Production/Maya/scenes")
        # self.stageLgtPath = os.path.join(stagepath, "Lighting/Production/Maya/scenes")
        # self.stageTrkPath = os.path.join(stagepath, "Tracking/Production/Maya/scenes")

        stageAnmWorkFiles = [f for f in os.listdir(self.stageAnmPath) if (os.path.isfile(os.path.join(self.stageAnmPath, f)) and f not in exclude)]
        self.stageAnmWorkFiles = sorted(stageAnmWorkFiles)