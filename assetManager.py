import fnmatch
import os
from functools import partial

import maya.cmds as cmds

import Utilities.assetInfo as ai
import Utilities.utilityFunctions as uf

# TODO 
# current scene info at top
# change namespace functionality? right click
# add import functionality
# add replace ref functionaliity
# add select top node in namespace functionality


proj = ai.AssetInfo()
widgets = {}
refObjList = []
namespaceList = []
nameFilter = "*_main_*_v*.m?" # this means we're filtering for file name structure and ONLY 'main' type. Change this if necessary

def asset_UI_create(*args):
    """
    ui
    """
    if cmds.window("assetWin", exists=True):
        cmds.deleteUI("assetWin")

    w = 820
    h = 550
    widgets["win"] = cmds.window("assetWin", t="Asset Manager", w=w, h=h)
    widgets["mainCLO"] = cmds.columnLayout(w=w, h=h)
    widgets["mainFLO"] = cmds.formLayout(w=w, h=h, bgc=(.2,.2,.2))

    widgets["phaseOM"] = cmds.optionMenu( label='Phase: ')#, changeCommand=temp)
    cmds.menuItem(label="Modeling")
    cmds.menuItem(label="Rigging")
    cmds.menuItem(label="Animation")
    cmds.optionMenu(widgets["phaseOM"], e=True, value = "Rigging")   

    widgets["assetsFLO"] = cmds.formLayout(w=200, h=500)
    widgets["assetsTab"] = cmds.tabLayout(w=200,h=500)
    widgets["charCLO"] = cmds.columnLayout("CHARS", w=200, h=500)
    widgets["charTSL"] = cmds.textScrollList(w=200, h=500)
    cmds.setParent(widgets["assetsTab"])
    widgets["propCLO"] = cmds.columnLayout("PROPS", w=200, h=500)
    widgets["propTSL"] = cmds.textScrollList(w=200, h=500)
    cmds.setParent(widgets["assetsTab"])
    widgets["setCLO"] = cmds.columnLayout("SETS", w=200, h=500)
    widgets["setTSL"] = cmds.textScrollList(w=200, h=500)   
    cmds.formLayout(widgets["assetsFLO"], e=True, af = [(widgets["assetsTab"], "top", 30), (widgets["assetsTab"], "left", 0),
        ])

    cmds.setParent(widgets["mainFLO"])
    widgets["refBut"] = cmds.button(l=">>>Ref in>>>", w=70, h=30, bgc=(.5,.5,.5), c=create_new_ref)
    # widgets["impBut"] = cmds.button(l=">>>Import in>>>", w=70, h=30, en=False, bgc=(.5,.5,.5), c=create_new_import)

    widgets["execBut"] = cmds.button(l="Execute Changes", w=120, h=40, bgc=(.5,.5,.5), c=execute)
    widgets["reloadBut"] = cmds.button(l="Reload/Refresh", w=120, h=40, bgc=(.5,.5,.5), c=reload_ref_list)   

    cmds.setParent(widgets["mainFLO"])
    widgets["refSLO"] = cmds.scrollLayout(w=520, h=400, bgc=(0,0,0))
    widgets["refCLO"] = cmds.columnLayout(w=520, rowSpacing=2, bgc = (.0,.0,.0), p=widgets["refSLO"])

    cmds.formLayout(widgets["mainFLO"], e=True, af = [(widgets["assetsFLO"], "top", 20), (widgets["assetsFLO"], "left", 5),
        (widgets["phaseOM"], "top", 10), (widgets["phaseOM"], "left", 0),
        (widgets["refSLO"], "top", 70), (widgets["refSLO"], "left", 290),
        (widgets["refBut"], "top", 100), (widgets["refBut"], "left", 210),
        # (widgets["impBut"], "top", 150), (widgets["impBut"], "left", 210),
        (widgets["execBut"], "top", 485), (widgets["execBut"], "left", 680),
        (widgets["reloadBut"], "top", 485), (widgets["reloadBut"], "left", 540),
        ])

    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
    cmds.showWindow(widgets["win"])

    load_asset_info()
    create_ref_list()


# NEED TO BE MORE EXPLICIT ABOUT HOW WE TELL IF SOMETHING IS IN OUR PIPELINE. .. (X TO Y)

class ReferenceObject(object):
    """
    class to create UI and info for each reference in the scene (existing or proposed via the ui) 
    ARGS:
        ns (string) - namespace
        ref (string) - reference path (should include the {} if they're at the end)
        deferred (bool) - is this reference deferred?
        status (string) - 'current' or 'pending' - is this an existing (current) ref or a pending create ref
    """
    existingRefList = []
    currentObjList = []
    pendingObjList = []
    allObjectList = []

    def __init__(self, ns, ref, deferred, status):
        self.pathParse = uf.PathParser(ref)
        self.compatible = self.pathParse.compatible
        self.ref = ref # the reference path
        self.namespace = ns # the namespace
        self.versionNums = [] # list of strings of the version numberss (i.e. ["0001", "0003"])
        self.versionNum = "" # astring of the version number (ie. "0005")
        self.status = status # status = "current" or "pending"
        self.killState = False # should this be killed?
        self.loadState = not deferred # should this be loaded (vs. unloaded)?
        self.state = False  # False means it has NOT been changed
        self.vchange = False # version change state
        self.lchange = False # load change state
        self.kchange = False # kill change state

        if self.status == "current":
            ReferenceObject.currentObjList.append(self)
        if self.status == "pending":
            ReferenceObject.pendingObjList.append(self)
        ReferenceObject.existingRefList.append(self.ref)
        ReferenceObject.allObjectList.append(self)

        self.create_UI()

    def create_UI(self):
        # creates the ui for the ref object
        self.mainFLO = cmds.formLayout(bgc=(.2,.2,.2), w=500, h=40, p=widgets["refCLO"])
        if self.status=="pending":
            cmds.formLayout(self.mainFLO, e=True, bgc=(.7, .7,.7))
        self.stateBut = cmds.button(l="", w=20, h=26, p=self.mainFLO, en=False, bgc=(.5, .5, .5))
        if self.status != "current":
            cmds.button(self.stateBut, e=True, bgc=(0, 0, 0))
        self.nsTxt = cmds.text(self.namespace, p=self.mainFLO)
        cmds.popupMenu(p=self.nsTxt)
        cmds.menuItem(l=self.ref)
        self.verOM = cmds.optionMenu(l="V:", p=self.mainFLO, w=75, bgc=(.5, .9, .5), changeCommand=self.change_number)
        if self.compatible:
            self.get_versions_list()
            for a in self.versionNums:
                cmds.menuItem(label=a)
            cmds.optionMenu(self.verOM, e=True, value=self.versionNum)
        else:
            cmds.optionMenu(self.verOM, e=True, bgc=(.5, .5,.5))

        self.loadBut = cmds.button(l="L", w=20, h=26, en=False, bgc=(.5,.9,.5), c=self.unload_toggle)
        if not self.loadState:
            cmds.button(self.loadBut, e=True, bgc=(.9, .5, .5))
        if self.status == "current":
            cmds.button(self.loadBut, e=True, en=True)
        self.killBut = cmds.button(l="X", w=20, h=26, bgc=(.2,.2,.2), c=self.kill_toggle)
        # if it's not in the pipeline kill some options
        if not self.compatible:
            cmds.formLayout(self.mainFLO, e=True, bgc=(.4, .2, .2))
            cmds.optionMenu(self.verOM, e=True, en=False)

        cmds.formLayout(self.mainFLO, e=True, af = [
            (self.stateBut, "top", 8),(self.stateBut, "left", 2),
            (self.nsTxt, "top", 12),(self.nsTxt, "left", 40),
            (self.verOM, "top", 12),(self.verOM, "left", 350),
            (self.loadBut, "top", 8),(self.loadBut, "left", 440),
            (self.killBut, "top", 8),(self.killBut, "left", 470),
            ])

    def get_versions_list(self):
        # just populates the existing versionNumbers instance variable
        self.pathParse.get_version_info()
        self.versionNums = self.pathParse.versionNumbersString
        self.versionNum = self.pathParse.versionString
        if self.versionNum != self.versionNums[-1]:
            cmds.optionMenu(self.verOM, e=True, bgc=(.9, .5, .5))
        else:
            cmds.optionMenu(self.verOM, e=True, bgc=(.5, .9, .5))

    def change_state_check(self):
        """
        to identify that an existing ref's params have been changed
        true means it has been changed
        Args:
            changed (bool)
        """
        if self.vchange or self.lchange or self.kchange:
            cmds.button(self.stateBut, e=True, bgc=(.9, .8, .3))
            self.state = True
        else:
            cmds.button(self.stateBut, e=True, bgc=(.5, .5, .5))
            self.state = False

    def unload_toggle(self, *args):
        if self.status=="current":
            if self.loadState == True:
                self.loadState = False
                cmds.button(self.loadBut, e=True, bgc=(.9, .5,.5))
            else:
                self.loadState = True
                cmds.button(self.loadBut, e=True, bgc=(.5,.9,.5))
            deff = cmds.file(self.ref, q=True, deferReference=True)
            if deff != self.loadState:
                self.lchange = False
            else:
                self.lchange = True

            self.change_state_check()

    def kill_toggle(self, *args):
        """
        kill option for refs, actually kills proposed objs on the spot
        """
        if self.status=="current":
            if self.killState == False:
                self.killState = True
                cmds.button(self.killBut, e=True, bgc=(.7, .2,.2))
                self.kchange = True

            else:
                self.killState = False
                cmds.button(self.killBut, e=True, bgc=(.2,.2,.2))
                self.kchange = False

            self.change_state_check()
        else:
            cmds.deleteUI(self.mainFLO)
            ReferenceObject.pendingObjList.remove(self)
            ReferenceObject.allObjectList.remove(self)
            ReferenceObject.existingRefList.remove(self.ref)
            # delete the object from all lists to delete it?          

    def change_number(self, *args):
        # replaces the current ref file with new one based on values in ui
        if self.compatible:
            chngchk = self.check_vnum_against_current(cmds.optionMenu(self.verOM, q=True))
            if chngchk:
                self.vchange=True
            else:
                self.vchange=False
            if self.status == "current":
                self.change_state_check()

    def check_vnum_against_current(self, vnum):
        """
        checks whether we should revert to unchanged state
        Args:
            vnum (string) - the number from the ui
        Returns:
            changed (bool) - is the number changed from the orig ref?
        """
        value = cmds.optionMenu(self.verOM, q=True, value=True)
        
        if value == self.pathParse.versionString:
            return(False)

        return(True)

    def gather_info(self, *args):
        """
        gets the info from the UI we'll need to create/edit the refs
        """
        if self.state == "default":
            state = False
        if self.state == "changed":
            state = True
        if self.compatible:
            self.versionNum = cmds.optionMenu(self.verOM, q=True, value=True)
            if fnmatch.fnmatch(self.ref, "*{*}"):
                brackets = "{" + self.ref.partition("{")[2]
# deal with the fact that the {} might contain an arbitrary amount of digits!!!!              
                path = uf.fix_path(self.pathParse.pathNoNum + self.versionNum + ".mb" + brackets)
            else:   
                path = uf.fix_path(self.pathParse.pathNoNum + self.versionNum + ".mb")              
            return(path, self.state, self.namespace, self.killState, self.loadState)
        else: # not compatible
            return(self.ref, self.state, self.namespace, self.killState, self.loadState)


def load_asset_info(*args):

    clear_asset_lists()

    proj = ai.AssetInfo()
    assetNames = proj.get_asset_name_list()
    for asset in assetNames[0]:
        cmds.textScrollList(widgets["charTSL"], e=True, a=asset)#, sc=temp)
    for asset in assetNames[1]:
        cmds.textScrollList(widgets["propTSL"], e=True, a=asset)#, sc=temp)
    for asset in assetNames[2]:
        cmds.textScrollList(widgets["setTSL"], e=True, a=asset)#, sc=temp)

    select_the_first()

def select_the_first(*args):
    """
    tries to select the first item in chars, if not, then props, etc. If no item, pass
    """
    cmds.textScrollList(widgets["charTSL"], e=True, sii=1)


def clear_asset_lists(*args):
    """
    clears all the asset text scroll lists
    """
    cmds.textScrollList(widgets["charTSL"], e=True, ra=True)
    cmds.textScrollList(widgets["propTSL"], e=True, ra=True)
    cmds.textScrollList(widgets["setTSL"], e=True, ra=True)


def get_existing_refs(*args):
    """
    gets existing refs
    Returns:
        Dict of refs:
            keys (string) are namespaces
            value is a list of:
                referencepath (string)
                versionList (list) - list of number strings i.e. ["0001", "0002"]
                deferred (bool)
    """
    refDict = {}
    #get reference paths
    refs = cmds.file(q=True, r=True)

    for ref in refs:
        #get the associated namespace
        ns = cmds.file(ref, q=True, ns=True)
        refDict[ns] = [ref]

        deferred = cmds.file(ref, q=True, deferReference=True)
        refDict[ns].append(deferred)     

    return(refDict)


def create_ref_list(*args):
    # creates the list of refs in the scene
    clear_ref_list()
    refDict = get_existing_refs()

    keys = [x for x in refDict.keys()]
    keys.sort()
    for ref in keys:
        r = ReferenceObject(ref, refDict[ref][0], refDict[ref][1], "current")
        namespaceList.append(ref)


def clear_ref_list(*args):
    # delete instances from ref List
    if ReferenceObject.existingRefList:
        for obj in ReferenceObject.existingRefList:
            del obj
    # delete ui and remake it
    cmds.deleteUI(widgets["refCLO"])
    widgets["refCLO"] = cmds.columnLayout(w=700, rowSpacing = 2, bgc = (.0,.0,.0), p=widgets["refSLO"])
    # clear the ref list
    ReferenceObject.existingRefList = []


def reload_ref_list(*args):
    clear_ref_list()
    create_ref_list()
    clear_all_object_info()


def create_new_ref(*args):
    """
    creates a new reference obj in the UI
    """
    # get selected asset, parse whether there are files in that particular phase
    tab, phase, assetPath, assetFiles = [None, None, None, None]
    tab, phase, assetPath, assetFiles = get_asset_info()
    
    if not assetFiles:
        cmds.warning("There are no published files for that asset")
        return()

    filePath = uf.fix_path(os.path.join(assetPath, assetFiles[-1]))

    # create the namespace from the file path
    ns = create_namespace(filePath)

    # create the ref object
    y = ReferenceObject(ns, filePath, False, "pending")
    namespaceList.append(ns)


def get_asset_info(*args):
    """
    gets info from asset sel in the ui
    Returns:
        tab (string): which tab is selected ("CHARS", "SETS", "PROPS")
        phase (string): which phase we're in ("Modeling", "Rigging", etc)
        assetPath (string): the path to the asset folder ("x://.../Assets/Character/Fish") based on above
        assetFiles (list): list of asset file paths based on above
    """
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
        assetPath = proj.mdlPubPath
        # filtering for only matches (see global variable at top)
        assetFiles = sorted(fnmatch.filter(proj.mdlPubFiles, nameFilter))
    if phase == "Rigging":
        assetPath = proj.rigPubPath
        # filtering for only matches (see global variable at top)
        assetFiles = sorted(fnmatch.filter(proj.rigPubFiles, nameFilter))
    if phase == "Animation":
        assetPath = proj.anmPubPath
        # filtering for only matches (see global variable at top)
        assetFiles = sorted(fnmatch.filter(proj.anmPubFiles, nameFilter))

    return(tab, phase, assetPath, assetFiles)


def create_namespace(filepath, *args):
    """
        get a file path and trim that down to new namespace, which will be incremented based on existing namespaces
        ex. instead of "Fish_Main_Rigging_Publish_v0002", will be "Fish_Main_Rig" or "Fish_Main_Rig1"
        ARGS:
            filepath (string): the filepath to derive the name from
        RETURN:
            string: the incremented namespace
    """
    f = uf.PathParser(filepath)
    phase = f.phase
    if phase == "Modeling":
        phase = "Mdl"
    if phase == "Rigging":
        phase = "Rig"
    if phase == "Animation":
        phase = "Anm"
    if phase == "Lighting":
        phase = "Lgt"                    
    namespace = "{0}_{1}_{2}".format(f.name, f.variant, phase)

    if namespace in namespaceList:
        incrementedName = increment_namespace(namespace, namespaceList)
    else:
        incrementedName = namespace
    print "creating Namespace {0} for {1}".format(incrementedName, filepath)
    return(incrementedName)


def increment_namespace(ns, nslist, *args):
    """
    increments the namespace to latest
    Args:
        ns(string) - the proposed namespace
        nslist(string) - the list of current namespaces
    Returns:
        string - a namespace that will be after last (ie. "Fish_main_Rig22")
    """
    outns = None
    print "finding {0} in {1}".format(ns, nslist)
    matches = fnmatch.filter(nslist, "{0}*".format(ns))
    if matches:
        lastNum = matches[-1].strip(ns)
        print "----------", matches[-1]
        if lastNum:
            lastInt = int(lastNum)
            newNum = lastInt + 1
            outns = ns + str(newNum)
        else:
            outns = ns + "1"
    else:
        outns = ns
    return(outns)



def execute(*args):
    # get list of current ref objs
    currentRefs = ReferenceObject.currentObjList
    for obj in currentRefs:
        path, state, namespace, killstate, loadstate = obj.gather_info()
        if state:
            print "===== AssetManager.execute: processing namespace: {0} ---- path: {1} . . . . . ".format(namespace, path)
            if killstate:
# throw up a confirm dialog?
                print "   --killing reference"
                cmds.file(path, removeReference=True)
            # do other stuff
            else:
                rfn = cmds.file(obj.ref, q=True, referenceNode=True)
                # replace the file
                if obj.vchange:
                    "    --replacing reference file"
                    cmds.file(path, loadReference=rfn, type="mayaBinary")
                #update the load state
                if loadstate:
                    "    --loading reference"
                    cmds.file(path, loadReference=rfn, type="mayaBinary")
                if not loadstate:
                    "    --unloading reference"
                    cmds.file(path, unloadReference=rfn)


    # get list of proposed ref objs
    pendingRefs = ReferenceObject.pendingObjList
    for obj in pendingRefs:
        path, state, namespace, killstate, loadstate = obj.gather_info()
        print "===== AssetManager.execute: creating ref in namespace: {0} ---- path: {1} . . . . . ".format(namespace, path)
        print "    --creating and loading reference"
        cmds.file(path, r=True, ns=namespace)

    # clear all the lists and objs
    print "      clearing and reloading UI. . . "
    clear_ref_list()
    clear_all_object_info()
    print "      ref info cleared"
    # refresh the whole
    assetManager()
    print "      ui reloaded"


# def create_new_import(*args):
#     pass

def clear_all_object_info(*args):
    proj = ai.AssetInfo()
    refObjList = []
    namespaceList = []
    widgets = {}
    ReferenceObject.existingRefList = []
    ReferenceObject.currentObjList = []
    ReferenceObject.pendingObjList = []
    ReferenceObject.allObjectList = []


def create_new_import(*args):
    pass


def assetManager(*args):
    asset_UI_create()

