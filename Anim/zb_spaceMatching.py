"""
Zed Bennett 11/19/2013
SpaceMatching.py

Description:
UI for switching parent space while maintaining current position in space, with the option to auto key the transition
"""

import maya.cmds as mc

def uiWindow(*args, **kwargs):
    global ssAttr
    ssAttr=["spaceSwitch", "SpaceSwitch", "follow"]
    global prefix
    prefix="spaceMatch"
    global windowNm
    windowNm="%sWindow"%prefix
    mainColumn="Main_%sColumn"%prefix
    global targListColumn
    targListColumn="%s_TargetListColumn"%prefix
    
    if mc.window(windowNm, ex=1):
        mc.deleteUI(windowNm)
        mc.windowPref(windowNm, r=1)
    mc.window(windowNm, t="Space Matcher", s=1, tlb=0, wh=[205,100])
    mc.columnLayout(mainColumn, adj=1)
    mc.columnLayout(targListColumn, adj=1)
    mc.setParent(mainColumn)
    mc.button("%s_reloadButton"%prefix, l="Refresh Space Targets", c=__loadTargets)
    mc.setParent(mainColumn)
    mc.checkBox("%s_AutoKey_CheckBox"%prefix, l="Auto Key", v=1)
    mc.setParent(mainColumn)
    mc.button("%s_keyButton"%prefix, l="Set Key", c=__key)
    mc.setParent(mainColumn)
    mc.button("%s_preKeyButton"%prefix, l="Set Pre Key", c=__preKey)
    mc.showWindow(windowNm)
    
    __loadTargets()
    
def __loadTargets(*args, **kwargs):
    sel=__singleSel()
    
    #build UI target option menu
    global optionMenuNm
    optionMenuNm="%s_optionMenu"%prefix
    
    mc.window(windowNm, e=1)
    mc.setParent(targListColumn)
    
    #if it exists already, blow it away
    if mc.optionMenu(optionMenuNm, ex=1)==1:
        mc.deleteUI(optionMenuNm)
    
    mc.optionMenu(optionMenuNm, l="Space Match Selection To:", h=20, cc=__spaceMatch)

    #if there's nothing selected return None
    if not sel:
        mc.menuItem("None")
    
    #if there is something selected, make sure it has a SpaceSwitch attr
    
    else:
        for i in ssAttr:
            if mc.objExists("%s.%s"%(sel,i))==1:
                global attr
                attr=i
        if not attr:
            mc.confirmDialog(t="ERROR", m="You must select an object with space switching capabilities.", b="Okay, Geeze!", cb="Okay, Geeze!")
            mc.error("Must select a control with space switching capabilies.")
        
        #return a list of the SpaceSwitch enums
        global spaceList
        spaceList=mc.attributeQuery(attr, n=sel, le=1)[0].split(":")
        spaceSel=mc.getAttr("%s.%s"%(sel,attr))+1
        #build the option menu list based on enums
        for x in spaceList:
            mc.menuItem(l=x)
        
        mc.optionMenu(optionMenuNm, e=1, sl=spaceSel)
        
def __spaceMatch(*args, **kwargs):
    sel=__singleSel()
    space=mc.optionMenu(optionMenuNm, q=1, v=1)
    val=spaceList.index(space)
    numAttrs=len(mc.attributeQuery(attr, n=sel, le=1)[0].split(":"))
    autoKey=mc.checkBox("%s_AutoKey_CheckBox"%prefix, q=1, v=1)
    origPos=mc.xform(sel, q=1, rp=1, ws=1)
    origRot=mc.xform(sel, q=1, ro=1, ws=1)
    
    if val>=numAttrs:
        mc.confirmDialog(t="ERROR", m="Wrong space list, refresh your space targets.", b="Okay, Geeze!", cb="Okay, Geeze!")
        mc.error("Your selected target is out of the index range for your selected controller")
    
    if autoKey==1:
        __preKey()
        mc.setAttr("%s.%s"%(sel,attr), val)
        mc.xform(sel, t=origPos, ws=1)
        mc.xform(sel, ro=origRot, ws=1)
        __key()
        
    else:
        mc.setAttr("%s.%s"%(sel,attr), val)
        mc.xform(sel, t=origPos, ws=1)
        mc.xform(sel, ro=origRot, ws=1)
        
def __preKey(*args,**kwargs):
    sel=__singleSel()
    __ctrlCheck
    prevFrame=mc.currentTime(q=1)-1
    mc.setKeyframe(sel, t=prevFrame)
    
def __key(*args, **kwargs):
    sel=__singleSel()
    __ctrlCheck
    currentFrame=mc.currentTime(q=1)
    mc.setKeyframe(sel, t=currentFrame)
    
def __singleSel(*args, **kwargs):
    sel=mc.ls(sl=1,fl=1)
    if sel:
        sel=sel[0]
    return sel
    
def __ctrlCheck(*args, **kwargs):
    sel=__singleSel()
    if sel.endsWith("_Ctrl")==0:
        mc.confirmDialog(t="ERROR", m="You gotta select a controller to do this.", b="Okay, Geeze!", cb="Okay, Geeze!")
        mc.error("Can only set keys on selected controllers")
    else:
        pass
        