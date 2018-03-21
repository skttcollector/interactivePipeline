import maya.cmds as cmds

import os
from functools import partial

import Utilities.projectGlobals as pg

widgets = {}

def set_project_UI(*args):
    if cmds.window("setProjectWin", exists=True):
        cmds.deleteUI("setProjectWin")

    widgets["win"] = cmds.window("setProjectWin", t="Set Project", w=200, h=100)
    widgets["mainCLO"] = cmds.columnLayout(w=300, h=200)
    cmds.text("Click the project you'll be working in", al="left")
    cmds.separator(h=10)

    # get dictionary, for each in dictionary, make a button
    projs = pg.projects
    for key in projs.keys():
        widgets[key] = cmds.button(l=key, w=300, h=30, bgc=(.5,.5,.5), c=partial(set_project_env_variables, key))

    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
    cmds.showWindow(widgets["win"])


def set_project_env_variables(proj = None, *args):
    """
    sets two environment variables: MAYA_CURRENT_PROJECT and MAYA_PROJECT_PATH, which we'll use in doing some pipeline stuff
    ARGS:
        proj (string) - the shortcut for the project we're using. Currently only "frog" and "fit", which stand for OutOfBoxExperience and FitAndSetup
    RETURNS:
        string, string: project name, project directory
    """
    print "PROJ: ", proj
    if not proj:
        return()

    currProj = None
    projPath = None

    projects = pg.projects
    if proj in projects.keys():
        drive = projects[proj]
        # check for existence of the drive we're looking for
        if os.path.exists(drive):
            currProj = proj
            projPath = projects[proj]
            os.environ["MAYA_CURRENT_PROJECT"] = currProj
            os.environ["MAYA_PROJECT_PATH"] = projPath

            print "{0} is now the current project (MAYA_CURRENT_PROJECT env var)\n{1} is now the current project path (MAYA_PROJECT_PATH env var)".format(currProj, projPath)
            
            if cmds.window("setProjectWin", exists=True):
                cmds.deleteUI(widgets["win"])

            if cmds.window("fileWin", exists=True):
                print "file win exists"
                cmds.deleteUI("fileWin")
            else:
                reload_file_manager()
        else:
            cmds.warning("setProject.set_project_env_variables: It seems you don't have the drive mapped for {0}. See a TD!".format(proj))
            set_project_UI()

    return(currProj, projPath)

def reload_file_manager(*args):
    import fileManager as fm
    
    fm.fileManager()

def setProject(*args):
    set_project_UI()


