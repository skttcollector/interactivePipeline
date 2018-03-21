import os
import fnmatch 
import sys
import shutil
from tempfile import mkstemp


# need to add function to remove projects

def add_project_to_project_globals(projectCodePath, pgPath, newName, newDrive):
    """
    adds entry to project globals module dictionary
    ARGS: 
        projectCodePath (string): the path that we need to be able to import the project globals file (we'll temporarily add this to sys.path)
        pgPath (string): the real path to the project globals file we're appending to
        newName (string): the name of the new project to add
        newDrive (string): the letter of the new drive to add

    example: add_project_to_project_globals(r"c:/Users/zethwillie/Desktop", r"c:/Users/zethwillie/Desktop/testFile.py", "newProj", "Z")
    """

    projDict = get_projects_dict(projectCodePath)

# check that name is good and that drive is one letter 
    projDict[newName] = "{0}:/Production".format(newDrive.upper())

    fh, newpath = mkstemp()
    origFile = open(pgPath, "r")

    # rewrite the file injecting the new line
    with os.fdopen(fh, "w") as newFile:
        with open(pgPath) as origFile:
            for line in origFile:
                line.strip()
                if fnmatch.fnmatch(line, "projects*{*}*"):
                    line = "projects = {0}\n".format(projDict)
                newFile.write(line)    

    os.remove(pgPath)
    shutil.move(newpath, pgPath)


def get_projects_dict(projectCodePath):
    """
    returns the dictionary from the project globals file
    """
    deletePath = 0
    if projectCodePath not in sys.path:
        sys.path.append(projectCodePath)
        deletePath = 1
        
    import projectGlobals

    projs = projectGlobals.projects

    # clean up the sys.path if we need to
    if deletePath:
        sys.path.remove(projectCodePath)

    return projs
