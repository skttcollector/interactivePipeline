"""
look under folder for what we want (maybe 3 checks?) in case it already exists - look for "production" folder?
copy folder structure over
"""

import Tkinter as Tk
from tkFileDialog import askdirectory
import os
import sys
import shutil

import changeProjectsInPipeline as chngProj


class DirectoryCreator(object):
    def __init__(self):
        # set the path to the template - need to get the two folders under here
        self.templatePath = r"//caddybak/BuckInteractive/pipelineTools/templates/ProjectDirectory/"
        # get the path to the sys.path we need and the projectGlobals file
        self.sysPath = r"\\caddybak\BuckInteractive\pipelineTools\development\interactivePipelineTools\Utilities"
        self.pgFile = r"\\caddybak\BuckInteractive\pipelineTools\development\interactivePipelineTools\Utilities\projectGlobals.py"
        self.tkui()        

    def getPath(self, event):
        """
        cretes a file browser dialog to put the selected path in the pathEntry text field
        """
        filename = askdirectory()
        self.pathEntry.delete(0, "end")
        self.pathEntry.insert(0, filename)

    def create(self, event):
        """
        calls the module func to make the changes in the document and copies folders to that location
        """
        # check at the location for Production and Traffic folders 
        folders = ["Production", "Traffic"]
        path = self.pathEntry.get()
        print path
        for folder in folders:
            # check location
            chkpath = "{0}/{1}".format(path, folder)
            print("checking: {0}".format(chkpath))
            if os.path.isdir(chkpath):
                print "oops"
            else:
                print "{0} is ok to create.".format(chkpath)
                shutil.copytree("{0}/{1}".format(self.templatePath, folder), "{0}/{1}".format(path, folder))

        chngProj.add_project_to_project_globals(self.sysPath, self.pgFile, self.nameEntry.get(), self.selDrive.get())
        print("Added to projectGlobals projects dictionary - Project: {0}".format(self.nameEntry.get()))
        print("                                            - Drive: {0}".format(self.selDrive.get()))

        self.root.destroy

    def tkui(self):
        # main ui
        self.root = Tk.Tk()
        self.topframe = Tk.Frame(self.root, w=400, bg="white")
        self.topframe.grid(row=0, sticky="nsew")
        self.bottomframe = Tk.Frame(self.root, bg="gray", w=400)
        self.bottomframe.grid(row=1, sticky="nsew")

        # top frame widgets
        tmpString = self.construct_stringvar()
        print tmpString
        self.projMsg = Tk.Message(self.topframe, text=tmpString, bg="white", width=400)

        # bottom frame widgets
        self.root.title("Add project to Interactive Pipe")
        self.nameTxt = Tk.Label(self.bottomframe, text="Project Name", bg="gray")
        self.locTxt = Tk.Label(self.bottomframe, text="Path", bg="gray")
        self.nameEntry = Tk.Entry(self.bottomframe)
        self.pathEntry = Tk.Entry(self.bottomframe, width=70)
        self.butGetPath = Tk.Button(self.bottomframe, text="Browse", fg="blue", bg="gray")
        self.butGetPath.bind("<Button-1>", self.getPath)
        self.butCreate = Tk.Button(self.bottomframe, text="Create!", fg="Red", bg="white", width=60)
        self.butCreate.bind("<Button-1>", self.create)

        drives = ["A", "B", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        self.selDrive = Tk.StringVar()
        self.selDrive.set(drives[0])
        self.driveMenu = Tk.OptionMenu(self.bottomframe, self.selDrive, *drives)

        # placing the widgets
        #top
        self.projMsg.grid(row=0, column=0, sticky="nsew")
        #bottom
        self.nameTxt.grid(row=0, column=0, sticky="ew")
        self.nameEntry.grid(row=0, column=1, sticky="ew")
        self.locTxt.grid(row=1, column=0, sticky="ew")
        self.pathEntry.grid(row=1, column=1, sticky="ew")
        self.butGetPath.grid(row=1, column=2, sticky="e")
        self.driveMenu.grid(row=2,column=1, sticky="w")
        self.butCreate.grid(row=3, column=1)

        self.root.mainloop()


    def construct_stringvar(self):
        projects = chngProj.get_projects_dict(self.sysPath)
        
        # get the list of projects/drives as one string
        projs = []
        for key in projects.keys():
            projs.append("{0}:  {1}\n".format(projects[key], key))

        projs.sort()
        projString = "".join(projs)            

        return(projString)


if __name__ == "__main__":
    creator = DirectoryCreator()