import maya.cmds as cmds
import os
import shutil

"""
will add/replace or remove userSetup.py for interactivePipline on the current machine
"""

# do this outside of maya? os.path.expanduser("~") -- which versions? 
# option to set current to devlopment or current. . . 

userSD = cmds.internalVar(userScriptDir=True)
generalSD = os.path.join(os.path.abspath(os.path.join(userSD, "../..")), "scripts")

origUserSetup = r"\\caddybak\BuckInteractive\pipelineTools\current\interactivePipelineTools\Utilities\userSetup.py"

def add_userSetup():
    check = confirm_dialog("This will replace your userSetup.py file\nIs that okay?")
    if not check:
        return()
    remove_userSetup(confirm=False)
    shutil.copy2(origUserSetup, "{0}/{1}".format(userSD, "userSetup.py"))


def remove_userSetup(confirm=True):
    """
    deletes userSetup.py from maya/scripts and maya/version/scripts folders
    """
    if confirm:
        check = confirm_dialog("This will DELETE your userSetup.py file.\nIs that okay?")
        if not check:
            return()
        for path in [userSD, generalSD]:
            if "userSetup.py" in os.listdir(path):
                if confirm:
                    os.remove("{0}/{1}".format(path, "userSetup.py"))


def confirm_dialog(message="Are you sure?"):
    check = cmds.confirmDialog(title="Confirm", bgc =(.7, .4, .4),  message = message, button = ("Yes", "Cancel"), defaultButton = "Yes", cancelButton = "Cancel", dismissString = "Cancel")
    if check=="Yes":
        confirm=True
    else:
        confirm=False

    return(confirm)


def userSetup_UI():
    pass

# if __name__ == "__main__":
#   userSetup_UI()