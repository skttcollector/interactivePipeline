#Zed Bennett 3/19/2014

#Tool for exporting flattened hierarchy rigs setup with the 'psyGames_jointSetup.py' script.
#Bakes simulation on floating joints in flattened hierarchy.
#Strips constraints.
#Isolates geometry and joints and exports for use as unity asset.

import maya.cmds as mc
import maya.mel as mel
import sys

class rigExport():
    def setup(self):
        oopsTest=mc.confirmDialog(t="HEADS UP!", m="DID YOU REMEMBER TO SET YOUR FRAME RANGE IN THE PLAYBACK SLIDER?", 
                                    b=["Yarp.","Narp."], db="Yarp.", cb="Narp.", ds="Narp.")
        if oopsTest=="Narp.":
            sys.exit("Whoops, go fix your playback range, dummy.")
        
        self.jntGrp="EXPORT_JNT_Grp"
        self.geoGrp="GEO"
        self.root=self.getRoot()
        self.start=mc.playbackOptions(q=1, min=1)
        self.end=mc.playbackOptions(q=1, max=1)
    
    def run(self, *args, **kwargs):
        self.setup()
        self.getFileData()
        self.refImport()
        self.bakeJoints()
        self.cleanup()
        self.eulerFilter()
        self.export()

    def getRoot(self, *args, **kwargs):
        #list Skar Nodes
        root=mc.ls("*:*ROOT")
        if root:
            return root[0]
        else:
            mc.error("NO REFERENCED ROOT NODE")
            
    def getParent(self, obj, *args, **kwargs):
        return mc.listRelatives(obj, p=1)
    
    def getFileData(self, *args, **kwargs):
        multipleFilters="FBX (*.fbx);;Maya Binary (*.mb);;All Files (*.*)"
        self.fileTarget=mc.fileDialog2(fileFilter=multipleFilters, dialogStyle=1, rf=1)
        self.currentFile=mc.file(q=1, sn=1)
        if self.fileTarget==None:
            sys.exit("OPERATION CANCELLED")
    
    def refImport(self, *args, **kwargs):
        jntGrpWildcard="*:%s"%self.jntGrp
        mc.select(jntGrpWildcard, r=1)
        refGrpLs=mc.ls(sl=1, fl=1)
        if len(refGrpLs)>1:
            mc.error("There are too many FLAT_JNT_Grp nodes in this scene, make sure you are using this script on isolated assets for best results.")
        refGrp=refGrpLs[0]
        
        if mc.objExists(refGrp):
            if mc.referenceQuery(refGrp, inr=1):
                rn=mc.referenceQuery(refGrp, rfn=1)
                fileName=mc.referenceQuery(rn, f=1)
                ns=refGrp.split(":")[0]
                mc.file(fileName, ir=1)
                mc.namespace(rm=ns, mnp=1)
            else:
                pass
        else:
            pass
            
    def bakeJoints(self, *args, **kwargs):
        #build joint list with children of Flat Jnt Grp        
        jnts=[]
        if mc.objExists(self.jntGrp):
            for i in mc.listRelatives(self.jntGrp, ad=1):
                if mc.objectType(i)=="joint":
                    jnts.append(i)
        else:
            mc.error("There is no 'FLAT_JNT_Grp' in this scene.")
        
        #make all joints keyable
        for j in jnts:
            attr=["t","r","s"]
            co=["x","y","z"]
            attrLs=[]
            for at in attr:
                for c in co:
                    attrLs.append("%s.%s%s"%(j,at,c))
            for x in attrLs:
                try:
                    mc.setAttr(x, k=1)
                except:
                    pass
                    
        ##  BAKE ANIMATION ON JOINTS  ==========================================================  BAKE ANIMATION ON JOINTS

        #bake that shit
        mc.bakeResults(jnts, t=(self.start,self.end), sm=1, sb=1, sac=0, mr=0)

        ## Clean up joint bake
        #delete static channels on joints
        #mc.delete(jnts, sc=1)
        
    def cleanup(self, *args, **kwargs):
        root=self.root
        #blow away constraints
        const=mc.ls(type="constraint")
        if const:
            mc.delete(const)
        
        #kill display layers
        dispLayers=mc.ls(type="displayLayer")
        if dispLayers:
            mc.delete(dispLayers)
        
        #flatten geometry hierarchy
        if mc.objExists(self.geoGrp):
            geo=[]
            for obj in mc.listRelatives(self.geoGrp, ad=1):
                if mc.objectType(obj)=="mesh" and self.getParent(self.getParent(obj))!=self.geoGrp:
                    geo.append(self.getParent(obj)[0])
            geo=list(set(geo))
            try:
                mc.parent(geo, self.geoGrp)
            except:
                print "Can't parent %s to %s"%(geo, self.geoGrp)
                pass

            #delete non mesh groups in geo group
            geoChildren=mc.listRelatives(self.geoGrp, c=1)
            for dag in geoChildren:
                meshes=None
                children=mc.listRelatives(dag, c=1)
                if children:
                    for child in children:
                        if mc.objectType(child)=="mesh":
                            meshes=child
                if not meshes:
                    mc.delete(dag)
        else:
            mc.group(em=1, n=self.geoGrp)
            mc.parent(mc.listRelatives(mc.ls(type="mesh"), p=1), self.geoGrp)
        
        #clean out root and move joints and geo into root
        if mc.objExists(root)!=1:
            mc.group(em=1, n=root)
        else:
            mc.parent(mc.listRelatives(root, c=1), w=1)
        
        mc.parent(self.geoGrp, root)
        
        mc.lockNode(self.jntGrp, l=0)
        mc.parent(self.jntGrp, root)
        
        safeList=mc.listRelatives(root, ad=1)
        safeList.append(root)
        
        killList=mc.ls(dag=1)
        for i in safeList:
            try:
                killList.remove(i)
            except:
                pass
        
        mc.delete(killList)
        
    def eulerFilter(self, *args, **kwargs):
        try:
            curveSel=mc.ls(type="animCurve")
            mc.selectKey(curveSel, add=1, k=1)
            mel.eval('filterCurve %s;'%" ".join(curveSel))
            mel.eval('keyTangent -itt linear -ott linear;')
            mc.selectKey(cl=1)
        except:
            print "can't run euler filter"
        
    def export(self, *args, **kwargs):
        file=self.fileTarget
        path=file[0]
        type=file[1]
        currentFile=self.currentFile
        preset="X:/Production/Code/Maya/Tools/PipelineTools/Python/Publishing/Cali_Scale_Cm.fbxexportpreset"
        print 'FBXLoadExportPresetFile -f "%s";' % preset
        mc.select(self.root)
        if type=='FBX':
            mel.eval('FBXLoadExportPresetFile -f "%s";' % preset)
            mel.eval('FBXExport -f "%s" -s' % path)
        
        mc.file(currentFile, o=1, f=1)
"""
exe=rigExport()
exe.getFileData()
exe.refImport()
exe.bakeJoints()
exe.cleanup()
exe.eulerFilter()
exe.export()
"""