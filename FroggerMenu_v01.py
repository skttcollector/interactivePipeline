# maya imports
import maya.cmds as mc
import maya.mel as mel

# python imports
from functools import partial
import os 
import webbrowser as web

#Utility imports
import Utilities.projectGlobals as pg

def initialize_projects():
    """
    looks through the project globals til it finds a valid project and initializes that
    """
    projects = pg.projects
    print "frogger init PROJECTS: ", projects

    drv = None
    for proj in projects.keys():
        tmpdrv = projects[proj]
        if os.path.exists(tmpdrv):
            os.environ["MAYA_CURRENT_PROJECT"] = proj
            drv = projects[proj]
            os.environ["MAYA_PROJECT_PATH"] = projects[proj]
            print "MAYA_PROJECT_DIR: ", os.environ["MAYA_PROJECT_PATH"]
            print "MAYA_PROJECT: ", os.environ["MAYA_CURRENT_PROJECT"]
            break

    if not drv:
        mc.confirmDialog(t="No Projects Found!", m="Couldn't find a valid project drive on your machine. Call a TD!", b="OK")
        return()

# initialize the maya env variables
initialize_projects()

helpdocs = "https://docs.google.com/document/d/1cNsxLUXJu-CyAdWVTAz31QhK2i0ipl2gH8_f6XyiyuU/edit?usp=sharing"

# Pipeline imports
import openSceneFile as osf
import saveSceneVersion as ssv
import saveSceneAsVersion as sav
import fileManager as fileMgr
import assetManager as assMgr
import setProject as sp
import Utilities.utilityFunctions as uf
import saveNewWindows as snw
import Utilities.assetInfo as ass

# Publishing imports
import Publishing.AssetPublish as assPub
import Publishing.multiRefAnimExport as mre
import updateAllReferences as upd

#import anim tools
import Anim.zb_spaceMatching as zbsm

#import rigging tools
import Rigging.importTemplate_v01 as it

imps = [osf, ssv, sav, fileMgr, assMgr, sp, assPub, mre, upd, pg, zbsm, it, uf, snw, ass]
for i in imps:
    reload(i)

#set UI version
global uiVersion
uiVersion=1.0


#main menu building function
def Menu(*args, **kwargs):
    #project prefix for unique UI names and basic naming variables
    proj=pg.project
    menuName="%s Menu"%proj
    pMainMenu="%s_MainMenu"%proj

    MainMayaWindow=mel.eval("$tempVar=$gMainWindow")

    if mc.menu(pMainMenu, q=1, ex=1):
        mc.deleteUI(pMainMenu)
    else:
        pass

    #build menu to main menu
    mc.menu(pMainMenu, to=1, l=menuName, p=MainMayaWindow)
    mc.menuItem(l="Refresh", c=rebuild, p=pMainMenu)

    #pipeline tools submenu
    pPipelineMenu=mc.menuItem(sm=1, l="Pipeline Tools", p=pMainMenu)
    mc.menuItem(l="File Manager", c=fileManager, p=pPipelineMenu)
    mc.menuItem(l="Asset Manager", c=assetManager, p=pPipelineMenu)
    mc.menuItem(l="Update All References", c=updateRefs, p=pPipelineMenu)
    mc.menuItem(l="Version Up Current", c=saveVersion, p=pPipelineMenu)
    mc.menuItem(l="Asset Publish And Version Up", c=partial(assPublishVersion, True), p=pPipelineMenu)
    mc.menuItem(l="Asset Publish Don't Version Up", c=partial(assPublishVersion, False), p=pPipelineMenu)
    mc.menuItem(l="Stage Publish (multi reference)", c=partial(stagePublish, False), p=pPipelineMenu)
    mc.menuItem(l="Change Project", c=setProject, p=pPipelineMenu)   

    #anim tools submenu
    animMenu=mc.menuItem(sm=1, l="Anim Tools", p=pMainMenu)
    mc.menuItem(l="Space Matching", c=spaceMatching, p=animMenu)

    #rigging tools submenu
    riggingMenu=mc.menuItem(sm=1, l="Rigging Tools", p=pMainMenu)
    mc.menuItem(l="Import Template", c=importTemplate, p=riggingMenu)

    #lookDev tools submenu
    lookdevMenu=mc.menuItem(sm=1, l="Look Dev Tools", p=pMainMenu)
    mc.menuItem(l="Collect Textures", c=collectTextures, p=lookdevMenu)

    # run project setter
    os.environ["MAYA_PROJECT_PATH"] = "X:/Production"
    os.environ["MAYA_CURRENT_PROJECT"] = "Frogger"

    # help stuff
    helpMenu = mc.menuItem(sm=1, l="Help", p=pMainMenu)
    mc.menuItem(l="Open Help Docs", c=open_help, p=helpMenu)

    # set project window
    sp.setProject()

#assembly functions for menu buttons
    
def rebuild(*args, **kwargs):
    print "----- REBUILDING FROGGER MENU v%s -----"%uiVersion
    import FroggerMenu_v01 as fm
    reload(fm)
    fm.Menu()

#PIPELINE MENU ITEMS#===========================================================
def setProject(*args):
    reload(sp)
    sp.setProject()

def openFile(*args, **kwargs):
    reload(osf)
    osf.run()

def saveVersion(*args, **kwargs):
    reload(ssv)
    ssv.run()

def saveAsVersion(*args, **kwargs):
    reload(sav)
    sav.run()

def assPublishVersion(versionUp, *args, **kwargs):
    reload(assPub)
    assPub.assetPublish(versionUp)

def stagePublish(versionUp, *args):
    reload(mre)
    mre.stagePublish(versionUp)

def fileManager(*args):
    reload(fileMgr)
    fileMgr.fileManager()

def assetManager(*args):
    reload(assMgr)
    assMgr.assetManager()

def updateRefs(*args):
    reload(upd)
    upd.update_all_references()

#ANIM MENU ITEMS#=================================================================
def spaceMatching(*args, **kwargs):
    reload(zbsm)
    zbsm.uiWindow()

#RIGGING MENU ITEMS#===============================================================
def importTemplate(*args, **kwargs):
    reload(it)
    it.run()

#LOOK DEV MENU ITEMS#======================================================
def collectTextures(*args, **kwargs):
    mel.eval('source "X:/Production/Code/Maya/Scripts/Mel/collectTextures.mel";')
    mel.eval("collectTextures;")


# HELP STUFF
def open_help(*args):
    web.open(helpdocs, new=1) # 1 means tries to open in new window