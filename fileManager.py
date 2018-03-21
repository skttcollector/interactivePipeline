import sys
import webbrowser as browser
import os
from functools import partial

import maya.cmds as cmds

import Utilities.assetInfo as ai
import Utilities.versionFile as vf
import openSceneFile as of
import Utilities.utilityFunctions as uf
import saveNewWindows as snw
import Utilities.projectGlobals as pg

widgets = {}

def file_UI_create(*args):
    """
    ui
    """
    if cmds.window("fileWin", exists=True):
        cmds.deleteUI("fileWin")

    w = 740
    h = 480
    widgets["win"] = cmds.window("fileWin", t="File Manager", w=w, h=h, s=False)
    widgets["menu"] = cmds.menuBarLayout()
    widgets["menuFile"] = cmds.menu(label="Presets")
    cmds.menuItem(l='Save Layout', c=save_layout)
    cmds.menuItem(l="Delete Layout", c=delete_layout)

    cmds.setParent(widgets["win"])
    widgets["mainCLO"] = cmds.columnLayout(w=w, h=h)
    widgets["mainFLO"] = cmds.formLayout(w=w, h=h, bgc=(.2,.2,.2))
    widgets["projOM"] = cmds.optionMenu(l="PROJECT:", changeCommand=change_project)

    projs = pg.projects
    for key in projs.keys():    
        cmds.menuItem(label=key)

    aw = 220
    widgets["assetsFLO"] = cmds.formLayout(w=aw, h=430)
    widgets["assetsTab"] = cmds.tabLayout(w=aw,h=430, cc=change_stage_tab)
    widgets["charCLO"] = cmds.columnLayout("CHARS", w=aw, h=400)
    widgets["charTSL"] = cmds.textScrollList(w=aw, h=400)
    cmds.setParent(widgets["assetsTab"])
    widgets["propCLO"] = cmds.columnLayout("PROPS", w=aw, h=400)
    widgets["propTSL"] = cmds.textScrollList(w=aw, h=400)
    cmds.setParent(widgets["assetsTab"])
    widgets["setCLO"] = cmds.columnLayout("SETS", w=aw, h=400)
    widgets["setTSL"] = cmds.textScrollList(w=aw, h=400)
    cmds.setParent(widgets["assetsTab"])
    widgets["stageCLO"] = cmds.columnLayout("STGS", w=aw, h=400)
    widgets["stageTSL"] = cmds.textScrollList(w=aw, h=400)       
    cmds.formLayout(widgets["assetsFLO"], e=True, af = [(widgets["assetsTab"], "top", 10), (widgets["assetsTab"], "left", 0),
        ])
    
    cmds.setParent(widgets["mainFLO"])
    widgets["filesFLO"] = cmds.formLayout(w=350,h=450)

    widgets["filesTSL"] = cmds.textScrollList(w=350, h=400, dcc=open_selected)
    widgets["phaseOM"] = cmds.optionMenu( label='Phase: ', changeCommand=populate_files)
    cmds.menuItem(label="Modeling")
    cmds.menuItem(label="Rigging")
    cmds.menuItem(label="Animation")
    cmds.menuItem(label="Lighting")
    cmds.menuItem(label="Texturing")
    cmds.formLayout(widgets["filesFLO"], e=True, af = [
        (widgets["filesTSL"], "top", 23), (widgets["filesTSL"], "left", 0),
        (widgets["phaseOM"], "top", 0), (widgets["phaseOM"], "left", 10)
        ])

    cmds.setParent(widgets["mainFLO"])

    widgets["openBut"] = cmds.button(l="Open Selected", w=125, h=30, bgc=(.3, .3, .3), c=open_selected)
    widgets["versionBut"] = cmds.button(l="Version Up Current", w=125, h=30, bgc=(.3, .3, .3), c=version_up)
    widgets["saveAsBut"] = cmds.button(l="Save Scene To New File", w=125, h=30, bgc=(.3, .3, .3), c=partial(save_as_new, False))
    widgets["saveSelBut"] = cmds.button(l="Save Selection To New", w=125, h=20, bgc=(.3, .3, .3), c=partial(save_as_new, True))
    widgets["refreshBut"] = cmds.button(l="Refresh Window", w=125, h=30, bgc=(.3, .3, .3), c=load_asset_info)

    cmds.formLayout(widgets["mainFLO"], e=True, af = [
        (widgets["projOM"], "top", 5), (widgets["projOM"], "left", 5),
        (widgets["assetsFLO"], "top", 25), (widgets["assetsFLO"], "left", 5),
        (widgets["filesFLO"], "top", 35), (widgets["filesFLO"], "left", 240),
        (widgets["openBut"], "top", 60),(widgets["openBut"], "left", 600),
        (widgets["versionBut"], "top", 110),(widgets["versionBut"], "left", 600),
        (widgets["saveAsBut"], "top", 260),(widgets["saveAsBut"], "left", 600),
        (widgets["saveSelBut"], "top", 375),(widgets["saveSelBut"], "left", 600),
        (widgets["refreshBut"], "top", 420),(widgets["refreshBut"], "left", 600),
        ])

    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
    cmds.showWindow(widgets["win"])

    set_project_optionMenu()
    load_asset_info("first")


def change_project(*args):
    """
    changes the project and checks for drive
    """
# need to set this up to properly call setProject (which CANNOT call back here to reload fileManager)
    project = cmds.optionMenu(widgets["projOM"], q=True, value=True)

    if not project:
        return()

    currProj = None
    projPath = None

    projects = pg.projects
    if project in projects.keys():
        drive = projects[project]
        # check for existence of the drive we're looking for
        if os.path.exists(drive):
            currProj = project
            projPath = projects[project]
            os.environ["MAYA_CURRENT_PROJECT"] = currProj
            os.environ["MAYA_PROJECT_PATH"] = projPath

            print "{0} is now the current project (MAYA_CURRENT_PROJECT env var)\n{1} is now the current project path (MAYA_PROJECT_PATH env var)".format(currProj, projPath)
            
            if cmds.window("setProjectWin", exists=True):
                cmds.deleteUI(widgets["win"])
        else:
            cmds.warning("setProject.set_project_env_variables: It seems you don't have the drive mapped for {0}. See a TD!".format(proj))
            return()

    print "{0} is now the current project (MAYA_CURRENT_PROJECT env var)\n{1} is now the current project path (MAYA_PROJECT_PATH env var)".format(project, pg.projects[project])   
    
    set_project_optionMenu()
    

def set_project_optionMenu(*args):
    """
    gets the current project in the maya environment variables and sets it to the option menu
    """
    ev = os.environ["MAYA_CURRENT_PROJECT"]
    print "fileMgr.ev: ", ev
    cmds.optionMenu(widgets["projOM"], e=True, value=ev)

    load_asset_info("first")


def save_layout(*args):
    """
    saves a small text doc to userpref folder that will tell UI on open which phase to set the option menu to (rigging, anim, etc)
    """
    phaseValue = "{0}\n".format(cmds.optionMenu(widgets["phaseOM"], q=True, value=True))
    #stageValue = "{0}\n".format(cmds.tabLayout(widgets["assetsTab"], q=True, st=True))
    #write to file
    userDir = cmds.internalVar(upd=True) + "frogger_fileManagerLayout.txt"
    file = open(userDir, "w")

    file.write(phaseValue)
    #file.write(stageValue)

    file.close()


def load_layout(*args):
    """
    RETURNS:
        string: the value to set in the phaseOM option menu
    """
    userDir = cmds.internalVar(upd=True) + "frogger_fileManagerLayout.txt"
    if os.path.isfile(userDir):
        file = open(userDir, "r")
        values = []

        for line in file:
            values.append(line.rstrip("\n"))
        file.close()

        cmds.optionMenu(widgets["phaseOM"], e=True, value=values[0])
        # cmds.tabLayout(widgets["assetsTab"], e=True, st=values[1])
        return(values[0])
    else:
        return(None)


def delete_layout(*args):
    userDir = cmds.internalVar(upd=True) + "frogger_fileManagerLayout.txt"
    if os.path.isfile(userDir):
        os.remove(userDir)
        print "Deleted saved layout for fileManager"


def load_asset_info(counter=None, *args):
    """
    gets the info for the assets in the project
    ARGS:
        counter (string) 
    """
    clear_asset_lists()

    proj = ai.AssetInfo()
    assetNames = proj.get_asset_name_list()

    for asset in assetNames[0]:
        cmds.textScrollList(widgets["charTSL"], e=True, a=asset, sc=partial(populate_files, proj))
    for asset in assetNames[1]:
        cmds.textScrollList(widgets["propTSL"], e=True, a=asset, sc=partial(populate_files, proj))
    for asset in assetNames[2]:
        cmds.textScrollList(widgets["setTSL"], e=True, a=asset, sc=partial(populate_files,proj))
    for asset in assetNames[3]:
        cmds.textScrollList(widgets["stageTSL"], e=True, a=asset, sc=partial(populate_files, proj))

    select_initial(proj, counter)


def select_initial(proj, counter, *args):
    """
    tries to select the first item in chars, if not, then props, etc. If no item, pass
    !! finish this later
    
    ARGS:
        proj (AssetInfo object)
        counter (string) 
    """

    # if we're in a scene with a name
    filename = cmds.file(q=True, sn=True)

    if filename:
        fileObj = uf.PathParser(filename)
        # if that scene is compatible
        if fileObj.compatible and fileObj.stage == "Work":
            # get the asset type - select the tab
            if fileObj.assetType == "Character":
                assType, assTab = "CHARS", "charTSL"
            if fileObj.assetType == "Props":
                assType, assTab = "PROPS", "propTSL"
            if fileObj.assetType == "Sets":
                assType, assTab = "SETS", "setTSL"              
            if fileObj.assetType == "Stages":
                assType, assTab = "STGS", "stageTSL"
            cmds.tabLayout(widgets["assetsTab"], e=True, st=assType)
            # get the phase - select the menu
            cmds.optionMenu(widgets["phaseOM"], e=True, value=fileObj.phase)  
            cmds.textScrollList(widgets[assTab], e=True, si=fileObj.name)
        else:
            #get current tab, select the first item in the corresponding tsl
            tab = cmds.tabLayout(widgets["assetsTab"], q=True, st=True)
            if tab == "CHARS":
                asstab = "charTSL"
            if tab == "PROPS":
                asstab = "propTSL"
            if tab == "SETS":
                asstab = "setTSL"
            if tab == "STGS":
                asstab = "stageTSL"
            cmds.textScrollList(widgets[asstab], e=True, sii=1)
    else:
        cmds.tabLayout(widgets["assetsTab"], e=True, st="CHARS")
        cmds.textScrollList(widgets["charTSL"], e=True, sii=1)
    if counter:
        load = load_layout()
        if load:
            cmds.optionMenu(widgets["phaseOM"], e=True, v=load)

    counter = None

    populate_files(proj)


def clear_asset_lists(*args):
    """
    clears all the asset text scroll lists
    """
    cmds.textScrollList(widgets["charTSL"], e=True, ra=True)
    cmds.textScrollList(widgets["propTSL"], e=True, ra=True)
    cmds.textScrollList(widgets["setTSL"], e=True, ra=True)
    cmds.textScrollList(widgets["stageTSL"], e=True, ra=True)


def clear_file_list(*args):
    """
    clears file text scroll list
    """
    cmds.textScrollList(widgets["filesTSL"], e=True, ra=True)


def change_stage_tab(*args):
    """
    when tab changes, just select first in the list
    """
    proj = ai.AssetInfo()

    currTab = cmds.tabLayout(widgets["assetsTab"], q=True, st=True)
    currScene = cmds.file(q=True, sn=True)
    if currTab == "CHARS":
        tsl = "char"
        cmds.optionMenu(widgets["phaseOM"], e=True, en=True)
    if currTab == "PROPS":
        tsl = "prop"
        cmds.optionMenu(widgets["phaseOM"], e=True, en=True)
    if currTab == "SETS":
        tsl = "set"
        cmds.optionMenu(widgets["phaseOM"], e=True, en=True)
    if currTab == "STGS":
        tsl = "stage"   
        cmds.optionMenu(widgets["phaseOM"], e=True, en=False, v="Animation")

    if currScene:
        # try to find in the current scene
        pp = uf.PathParser(currScene)
        if pp.compatible:
            if pp.name in cmds.textScrollList(widgets["{0}TSL".format(tsl)], q=True, allItems=True):
                cmds.textScrollList(widgets["{0}TSL".format(tsl)], e=True, si=pp.name)
            else:
                cmds.textScrollList(widgets["{0}TSL".format(tsl)], e=True, sii=1)
        else:
            cmds.textScrollList(widgets["{0}TSL".format(tsl)], e=True, sii=1)
    else:
        cmds.textScrollList(widgets["{0}TSL".format(tsl)], e=True, sii=1)

    populate_files(proj)


def populate_files(proj, *args):
    """
    clears the file list, then populates based on the phase and the selected asset in the asset TSL
    """
    proj = ai.AssetInfo()

    clear_file_list()

    selTab = cmds.tabLayout(widgets["assetsTab"], q=True, st=True)

    tab, phase, assetPath, assetFiles = [None, None, None, None]

    if selTab != "STGS":
        tab, phase, assetPath, assetFiles = get_asset_info(proj)
    else:
        tab, phase, assetPath, assetFiles = get_stage_info(proj)

    if assetFiles:
        for file in assetFiles:
            a = cmds.textScrollList(widgets["filesTSL"], e=True, a=os.path.basename(file))
    else:
        cmds.textScrollList(widgets["filesTSL"], e=True, a="No Files")

    # add popmenu to the list object to go to explorer
    cmds.popupMenu(p=widgets["filesTSL"])
    cmds.menuItem(l="Open Folder in Explorer", c=get_path_explorer)

    # try to line up the current scene in the file list
    currFile = cmds.file(q=True, sn=True)
    if currFile:
        fileObj = uf.PathParser(currFile)
        if fileObj.compatible and (os.path.basename(currFile) in assetFiles):
            cmds.textScrollList(widgets["filesTSL"], e=True, si=os.path.basename(currFile))
    else:
        # get the last file and select that
        numItems = cmds.textScrollList(widgets["filesTSL"], q=True, ni=True)
        cmds.textScrollList(widgets["filesTSL"], e=True, sii=numItems)


def get_path_explorer(*args):
    # construct path from ui
    currTab = cmds.tabLayout(widgets["assetsTab"], q=True, st=True)
    if currTab == "CHARS":
        tsl = "char"
        assType = "Character"
    if currTab == "PROPS":
        tsl = "prop"
        assType = "Props"
    if currTab == "SETS":
        tsl = "set"
        assType = "Sets"
    if currTab == "STGS":
        tsl = "stage"
        assType = "Stages"
    
    phase = cmds.optionMenu(widgets["phaseOM"], q=True, value=True)
    asset = cmds.textScrollList(widgets["{0}TSL".format(tsl)], q=True, si=True)[0]
    base = os.environ["MAYA_PROJECT_PATH"]
    if currTab != "STGS":
        path = "{0}/Assets/3D/{1}/{2}/{3}/Work/Maya/scenes/".format(base, assType, asset, phase)
    else:
        path = "{0}/Stages/{1}/{2}/Production/Maya/scenes/".format(base, asset, phase )

    if os.path.isdir(path):
        open_explorer(path)
    else: 
        print "Couldn't find the path: {0}".format(path)


def open_explorer(path, *args):
    """takes in path and opens it in os folder"""
    if os.path.isdir(path):
        if sys.platform == "win32":
            winPath = path.replace("/", "\\")
            browser.open(winPath)
        elif sys.platform == "darwin":
            pass
        elif sys.platform == "linux" or sys.platform=="linux2":
            pass


def get_asset_info(proj, *args):
    """
    gets info from state of the ui
    ARGS: 
        proj (AssetInfo object) - the info for the current set project
    Returns:
        tab (string) - which tab is selected ("CHARS", "SETS", "PROPS")
        phase (string) - which phase we're in ("Modeling", "Rigging", etc)
        assetPath (string) - the path to the asset folder ("x://.../Assets/Character/Fish") based on above
        assetFiles (list) - list of asset file paths based on above
    """
    proj = ai.AssetInfo()

    asset = None
    assetFiles = None
    tab = cmds.tabLayout(widgets["assetsTab"], q=True, st=True)
    phase = cmds.optionMenu(widgets["phaseOM"], q=True, value=True)

    if tab == "CHARS":
        asset = cmds.textScrollList(widgets["charTSL"], q=True, si=True)[0]
        assetPath = os.path.join(proj.charPath, asset)
    if tab == "PROPS":
        asset = cmds.textScrollList(widgets["propTSL"], q=True, si=True)[0]
        assetPath = os.path.join(proj.propPath, asset)
    if tab == "SETS":
        asset = cmds.textScrollList(widgets["setTSL"], q=True, si=True)[0]
        assetPath = os.path.join(proj.setPath, asset)

    proj.get_asset_contents(assetPath)
    if phase == "Modeling":
        assetPath = proj.mdlPath
        assetFiles = sorted(proj.mdlWorkFiles)
    if phase == "Rigging":
        assetPath = proj.rigPath
        assetFiles = sorted(proj.rigWorkFiles)
    if phase == "Animation":
        assetPath = proj.anmPath
        assetFiles = sorted(proj.anmWorkFiles)
    if phase == "Lighting":
        assetPath = proj.lgtPath
        assetFiles = sorted(proj.lgtWorkFiles)
    if phase == "Texturing":
        assetPath = proj.txtPath
        assetFiles = sorted(proj.txtWorkFiles)

    return(tab, phase, assetPath, assetFiles)


def get_stage_info(proj, *args):
    """
    gets info from state of the ui
    ARGS:
        proj (AssetInfo object) - the info for the current project files
    Returns:
        tab (string) - which tab is selected ("CHARS", "SETS", "PROPS", "STGS")
        phase (string) - which phase we're in ("Modeling", "Rigging", etc)
        assetPath (string) - the path to the asset folder ("x://.../Stage/FireFlyStage") based on above
        assetFiles (list) - list of asset file paths based on above
    """
    proj = ai.AssetInfo()
    asset = None
    assetFiles = None
    assetR = cmds.textScrollList(widgets["stageTSL"], q=True, si=True)
    if not assetR:
        assetR = cmds.textScrollList(widgets["stageTSL"], q=True, sii=0)
    asset = assetR[0]
    assetPath = os.path.join(proj.stagePath, asset)  
    tab = "STGS"
    phase = "Animation"
    proj.get_stage_contents(assetPath)
    assetPath = proj.stageAnmPath
    assetFiles = proj.stageAnmWorkFiles

    return(tab, phase, assetPath, assetFiles)    


def open_selected(*args):
    proj = ai.AssetInfo()
    # if no file then warn and skip
    selFile = cmds.textScrollList(widgets["filesTSL"], q=True, si=True)[0]
    if selFile == "No Files":
        cmds.warning("No files available to open!")
        return()

    # construct the paths
    tab, phase, assetPath, assetFiles = [None, None, None, None]
    selTab = cmds.tabLayout(widgets["assetsTab"], q=True, st=True)
    if selTab != "STGS":
        tab, phase, assetPath, assetFiles = get_asset_info(proj)
    else:
        tab, phase, assetPath, assetFiles = get_stage_info(proj)
    selIndex = cmds.textScrollList(widgets["filesTSL"], q=True, sii=True)[0]
    filePath = os.path.join(assetPath, assetFiles[selIndex - 1])

    # check mods, if so then. . 
    changed = cmds.file(q=True, modified=True)
    svState = True
    if changed:
        svState = save_current_dialog()
    if svState:
        of.run(filePath)
    else:
        return()


def save_current_dialog(*args):
    save = cmds.confirmDialog(title="Save Confirmation", message = "Save current scene?", button = ("Save", "Don't Save", "Cancel"), defaultButton = "Save", cancelButton = "Cancel", dismissString = "Cancel")
    if save == "Save":
        cmds.file(save=True)
        return(True)
    elif save == "Don't Save":
        return(True)
    else:
        return(False)


def version_up(*args):
    """
    versions the current file based on Zed's class/modules
    """

    filePath = cmds.file(q=True, sn=True)
    ver = vf.versionClass()
    ver.versionUp(filePath)

    load_asset_info()


def save_as_new(selectionBased=False, *args):

    proj = ai.AssetInfo()

    # construct the paths
    filePath = None
    selTab = cmds.tabLayout(widgets["assetsTab"], q=True, st=True)
    if selTab != "STGS":
        tab, phase, assetPath, assetFiles = get_asset_info(proj)
    else:
        tab, phase, assetPath, assetFiles = get_stage_info(proj)

    selItem = None
    if cmds.textScrollList(widgets["filesTSL"], q=True, sii=True):
        selIndex = cmds.textScrollList(widgets["filesTSL"], q=True, sii=True)[0]
        selItem = cmds.textScrollList(widgets["filesTSL"], q=True, si=True)[0]

    if not selItem or selItem == "No Files":
        if tab == "CHARS":
            asset = cmds.textScrollList(widgets["charTSL"], q=True, si=True)[0]
        if tab == "PROPS":
            asset = cmds.textScrollList(widgets["propTSL"], q=True, si=True)[0]
        if tab == "SETS":
            asset = cmds.textScrollList(widgets["setTSL"], q=True, si=True)[0]
        if tab == "STGS":
            asset = cmds.textScrollList(widgets["stageTSL"], q=True, si=True)[0]

        filename = "{0}_main_{1}_Work_v0001.mb".format(asset, phase)
        filePath = uf.fix_path(os.path.join(assetPath, filename))

    # or use the path from selections
    else:
        filePath = uf.fix_path(os.path.join(assetPath, assetFiles[selIndex - 1]))

    savenewdata = snw.SaveNewAssetUI(filePath, selectionBased)

    # # if file already exists then bail out
    # if os.path.isfile(filePath):
    #     cmds.confirmDialog(title="File Exists!", message = "This file type already exists, you should use the version up instead!", button = ("OK"))
    #     return()

    # confirm = cmds.confirmDialog(title="Save Confirmation", message = "You are about to create:\n{0}\n\nShould we continue?".format(filePath), button = ("Create", "Cancel"), defaultButton = "Save", cancelButton = "Cancel", dismissString = "Cancel", bgc = (.6, .5, .5))
    # if confirm == "Create":
    #     write=True
    # else:
    #     write=False

    # if write:
    #     ver = vf.versionClass()
    #     ver.versionUp(filePath)

    # populate_files()


def fileManager(*args):
    if cmds.window("saveAsWin", exists=True):
        cmds.deleteUI("saveAsWin")
    file_UI_create()