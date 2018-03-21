import os

import maya.cmds as cmds
import maya.mel as mel

import Utilities.utilityFunctions as uf


def set_and_export(filepath):

    pathField = None
    fileField = None
    filepath = uf.fix_path(filepath)
    path = "/".join(filepath.split("/")[:-1])
    file = os.path.basename(filepath).split(".")[0]
    # open the exporter
    mel.eval("gameFbxExporter;")

    # get the exporter nodes (I'm still not sure which one, so we'll use the last later)
    nodes = mel.eval("gameExp_GetGameFbxExporterNodeList()")
    # preset = "X:/Production/Code/Maya/Tools/PipelineTools/Python/Publishing/assetAnimGameExpPreset.mel"

# can we get the whole frame range?

    # set it to the correct tab
    tab = "gameExporterWindow|gameExporterTabFormLayout|gameExporterTabLayout"
    cmds.tabLayout(tab, e=True, st="gameExporterAnimationTab")

    # assign preset (on the last node?)
    # hold = mel.eval('gameExp_ApplyPresetOnNode("{0}", "{1}");'.format(nodes[-1], preset))

    # find the text fields
    for ctrl in cmds.lsUI(ctl=True, l=True):
        if ctrl.startswith("gameExporterWindow") and ctrl.split("|")[-1]=="anim_gameExporterExportFilename":
            fileField = ctrl
        if ctrl.startswith("gameExporterWindow") and ctrl.split("|")[-1]=="anim_gameExporterExportPath":
            pathField = ctrl

    mel.eval('gameExp_BrowseFolder')
    # populate the text fields  
    # changetext = cmds.textField(pathField, e=True, tx=path)
    # cmds.textField(fileField, e=True, tx=file)


    # print mel.eval('getAttr ($gGameFbxExporterCurrentNode + ".exportPath");')

    # mel.eval('connectControl -preventContextualMenu true -fileName {0} ($gGameFbxExporterCurrentNode + ".exportPath");'.format(pathField))
    # mel.eval('connectControl -preventContextualMenu true {0}($gGameFbxExporterCurrentNode + ".exportFilename");'.format(fileField)) 

    # do the export
    # mel.eval('gameExp_DoExport;')


