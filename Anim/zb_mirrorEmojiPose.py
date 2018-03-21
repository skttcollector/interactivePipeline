#mirror selected attribute

import maya.cmds as mc

def mirrorPose(*args, **kwargs):
    sel=mc.ls(sl=1,fl=1)
    
    for i in sel:
        mirPre=""
        prefix=i.split(":")[-1].split("_")[0]
        if prefix=="Lf":
            mirPre="Rt"
        elif prefix=="Rt":
            mirPre="Lf"
        else:
           print "No mirrorable side"
        
        if mirPre:
            mirror=i.replace(prefix, mirPre)
            if mc.objExists(mirror):
                for a in ["t","r","s"]:
                    for x in ["x","y","z"]:
                        attr=mc.getAttr("%s.%s%s"%(i,a,x))
                        mirrorAttr="%s.%s%s"%(mirror,a,x)
                        #print "%s >>> %s >>> %s"%(i,mirrorAttr,attr)
                        if "lip" in mirror:
                            setSame(mirrorAttr, attr)
                                
                        if "eye" in mirror or "brow" in mirror:
                            if a=="t" and x=="x":
                                setRev(mirrorAttr, attr)

                            elif a=="r":
                                if x=="y" or x=="z":
                                    setRev(mirrorAttr, attr)
                                else:
                                    setSame(mirrorAttr, attr)
                            else:
                                setSame(mirrorAttr, attr)
def setRev(mirrorAttr, attr):
    rev=(attr*-1)
    try:
        mc.setAttr(mirrorAttr, rev)
        print "setting %s to %s"%(mirrorAttr, rev)
    except:
        print "can't set %s, probably because it's locked"%mirrorAttr

def setSame(mirrorAttr, attr):
    try:
        mc.setAttr(mirrorAttr, attr)
        print "setting %s to %s"%(mirrorAttr, attr)
    except:
        print "can't set %s, probably because it's locked"%mirrorAttr
            
mirrorPose()