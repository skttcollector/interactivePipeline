import maya.cmds as mc

def run(*args, **kwargs):
    root="X:"
    #root=r"D:\3D_work\work\professional\Frogger"
    templatePath=r"%s\Production\Code\Maya\Tools\RiggingTools\rigTemplate.mb"%root
    mc.file(templatePath, i=1, type="mayaBinary", iv=1, rpr="rigTemplate", mnc=0, pr=1)