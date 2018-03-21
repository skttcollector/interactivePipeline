import maya.cmds as mc

import Utilities.projectGlobals as pg

#open file dialog to return file path
#state is 0=save file, 1=open file
def getFilePath(state, *args, **kwargs):
    #default path from frogger project
    path=mc.workspace(q=1,o=1)
    defaultPath=pg.defaultPath
    directory="%s/%s"%(path, pg.filefolder)
    #the types of file
    filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    #check if the directory is in the project assets
    if defaultPath not in directory:
        directory=defaultPath.replace("/","\\")
    #print directory
    #open file dialog with filders in the determined workspace
    file=mc.fileDialog2(ff=filters, dir=directory, fm=state, ds=1, sff="Maya Binary")
    #return the selected file path
    if file:
        return file[0]
    else:
        pass