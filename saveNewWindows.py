import os

import maya.cmds as cmds

import Utilities.assetInfo as ai
import Utilities.utilityFunctions as uf
import Utilities.versionFile as vf
import fileManager as fm

#callback dismiss function to get the values of the stuff inside
class SaveNewAssetUI(object):
    def __init__(self, filePath=None, selectionBased=False, *args):
        self.dict = {}
        self.projEnvPath = os.environ["MAYA_PROJECT_PATH"]
        self.selBased = selectionBased
        self.filePath = filePath
        print "filePath: ", self.filePath
        self.proj = ai.AssetInfo()
        self.pp = uf.PathParser(filePath)
        if not self.pp.compatible:
# dummy check that the folders exist
            files = self.proj.get_asset_contents(self.proj.charsPath[0])
            self.filepath = "{0}{1}".format(self.proj.charsPath[0], files[0])
        self.assetList = self.proj.get_asset_name_list()   
        self.saveAs_UI()


    def saveAs_UI(self):
        if cmds.window("saveAsWin", exists=True):
            cmds.deleteUI("saveAsWin")

        self.win = cmds.window("saveAsWin", t="Save New", w=220, h=220)
        self.form = cmds.formLayout(w=220, h=220)

        t1 = cmds.text(l="Save As New Destination Options:")
        t2 = cmds.text(l="Project: {0}".format(os.environ["MAYA_CURRENT_PROJECT"]), font="boldLabelFont")

        self.assetTypeOM = cmds.optionMenu(l="Asset Type:", w=200, cc=self.change_asset_type)
        cmds.menuItem(l="Character", p=self.assetTypeOM)
        cmds.menuItem(l="Props", p=self.assetTypeOM)
        cmds.menuItem(l="Sets", p=self.assetTypeOM)
        cmds.menuItem(l="Stages", p=self.assetTypeOM)

        if self.pp.compatible:
            cmds.optionMenu(self.assetTypeOM, e=True, value=self.pp.assetType)

        self.phaseOM = cmds.optionMenu(l="Asset Phase:", w=200)
        self.anm = cmds.menuItem(l="Animation", p=self.phaseOM)
        self.mdl = cmds.menuItem(l="Modeling", p=self.phaseOM)
        self.rig = cmds.menuItem(l="Rigging", p=self.phaseOM)
        self.lgt = cmds.menuItem(l="Lighting", p=self.phaseOM)
        self.txt = cmds.menuItem(l="Texturing", p=self.phaseOM)

        self.assetOM = cmds.optionMenu(l="Asset:", w=200)
        self.change_asset_type()
        if self.pp.compatible:
            cmds.optionMenu(self.assetOM, e=True, value=self.pp.name)

        if self.pp.compatible:
            cmds.optionMenu(self.phaseOM, e=True, value=self.pp.phase)

        self.variant = cmds.textFieldGrp(l="Variant:", tx="main", cw=[(1, 50),(2,150)], cal=[(1, "left"), (2,"left")])
        if self.pp.compatible:
            cmds.textFieldGrp(self.variant, e=True, tx=self.pp.variant)

        if self.pp.compatible:
            if self.assetType == "Stages":
                cmds.menuItem(self.mdl, e=True, en=False)
                cmds.menuItem(self.txt, e=True, en=False)
                cmds.menuItem(self.rig, e=True, en=False)

        self.but = cmds.button(l="Save File!", bgc = (.5, .7, .5), w=100, h=30, c=self.save_file)
        self.cancel = cmds.button(l="Cancel", bgc = (.7, .5, .5), w=100, h=30, c=self.cancel)

        cmds.formLayout(self.form, e=True, attachForm = [
            (t1, "top", 2), (t1, "left", 5),
            (t2, "top", 20), (t2, "left", 5),
            (self.assetTypeOM, "top", 45), (self.assetTypeOM, "left", 5),
            (self.assetOM, "top", 75), (self.assetOM, "left", 5),
            (self.variant, "top", 105), (self.variant, "left", 5),
            (self.phaseOM, "top", 135), (self.phaseOM, "left", 5),                             
            (self.but, "top", 175), (self.but, "left", 5),
            (self.cancel, "top", 175), (self.cancel, "left", 120),
        ])

        cmds.window(self.win, e=True, w=230, h=220, rtf=True, s=False)
        cmds.showWindow(self.win)      


    def change_asset_type(self, *args):
        # change the values of self.assetOM
        self.assetType = cmds.optionMenu(self.assetTypeOM, q=True, value=True)
        y=0
        if self.assetType=="Characters":
            y=0
        if self.assetType=="Props":
            y=1
        if self.assetType=="Sets":
            y=2
        if self.assetType=="Stages":
            y=3

        if self.assetType !="Stages":
            cmds.menuItem(self.rig, e=True, en=True)
            cmds.menuItem(self.mdl, e=True, en=True)
            cmds.menuItem(self.txt, e=True, en=True)
        else:
            cmds.menuItem(self.rig, e=True, en=False)
            cmds.menuItem(self.mdl, e=True, en=False)
            cmds.menuItem(self.txt, e=True, en=False)
            cmds.optionMenu(self.phaseOM, e=True, value="Animation")           

        cmds.deleteUI(self.assetOM)
        self.assetOM = cmds.optionMenu(l="Asset:", w=200, p=self.form)
        cmds.formLayout(self.form, e=True, af=[(self.assetOM, "top", 70), (self.assetOM, "left", 5)])
        
        for x in self.assetList[y]:
            cmds.menuItem(l=x, p=self.assetOM)


    def cancel(self, *args):
        cmds.deleteUI("saveAsWin")


    def save_file(self, *args):
        # assemble file name
        sel = []
        if self.selBased:
            sel = cmds.ls(sl=True)
            if not sel:
                cmds.warning("fileManager.save_as_new: You haven't selected anything! Make a selection and try again!")
                return()

        currscene = cmds.file(q=True, sn=True)
        if currscene:
            saveScene =cmds.confirmDialog(t="Save?", m="Should I save the current scene before writing new file?", button=["Yes", "No", "Cancel"], defaultButton="Yes", cancelButton="Cancel", dismissString="Cancel")
            if saveScene == "Yes":
                print "Saving current scene: {0}".format(currscene)
                cmds.file(s=True, f=True)
            elif saveScene == "No":
                pass
            elif saveScene == "Cancel":
                cmds.warning("Cancelling Save As New!")
                return()
        else:
            pass
            # cmds.warning("You must be in a named scene to continue!")
            # return()

        filepath = None
        assettype = cmds.optionMenu(self.assetTypeOM, q=True, value=True)
        if assettype == "Stages":
            basepath = "{0}/Stages".format(self.projEnvPath)
        else:
            basepath = "{0}/Assets/3D/{1}".format(self.projEnvPath, assettype)

        asset = cmds.optionMenu(self.assetOM, q=True, value=True)
        variant = cmds.textFieldGrp(self.variant, q=True, tx=True)
        if not uf.check_for_good_name(variant):
            cmds.warning("No underscores allowed in variant names!")
            return()
        phase = cmds.optionMenu(self.phaseOM, q=True, value=True)

        if assettype == "Stages":
            filepath = "{0}/{1}/{2}/Production/Maya/scenes/{3}_{4}_{5}_Work_v0001.mb".format(basepath, asset, phase, asset, variant, phase)
        else:
            filepath = "{0}/{1}/{2}/Work/Maya/scenes/{3}_{4}_{5}_Work_v0001.mb".format(basepath, asset, phase, asset, variant, phase)

        # confirm and save
        # export to temp, open that
        tempScene = None
        if self.selBased:
            tempScene = create_temp_scene(filepath)
            if tempScene:
                cmds.file(tempScene, open=True, f=True)
            else:
                return()

        write = "Cancel"
        confirm = cmds.confirmDialog(title="Save Confirmation", message = "You are about to 'version up':\n{0}\n\nShould we continue?".format(filepath[:-9]), button = ("Create", "Cancel"), defaultButton = "Save", cancelButton = "Cancel", dismissString = "Cancel", bgc = (.6, .5, .5))
        if confirm == "Create":
            write=="Save"
            print "Saving. . .: ", filepath            
        else:
            write=="Cancel"
            print "Canceling. . ."
            cmds.deleteUI(self.win)

        if write:
            ver = vf.versionClass()
            ver.versionUp(filepath)
            cmds.deleteUI(self.win)
            if tempScene and os.path.isfile(tempScene):
                print "saveNewWindows.save_file: Cleaning up temp scene {0}".format(tempScene)
                os.remove(tempScene)
            cmds.confirmDialog(m="Save successful! You're now in file:\n{0}".format(cmds.file(q=True, sn=True)))

        # Try to refresh the file manager window
        if cmds.window("fileWin", exists=True):
            fm.fileManager()


def create_temp_scene(filepath, *args):
    tempFile = filepath[:-3] + "_temp.mb"
    export = cmds.file(tempFile, exportSelected=True, type="mayaBinary")
    if export==tempFile:
        print "===== saveNewWindow.create_temp_scene: created temp file: {0}".format(tempFile)
        return(tempFile)
    else:
        cmds.warning("==== saveNewWindow.save_file: There was an issue creating the tempfile: {0}".format(tempFile))
        return(False)

    def cancel(self):
        # delete UI and cnacel
        cmds.warning("Cancelling save as new. . . ")
        cmds.deleteUI(self.win)