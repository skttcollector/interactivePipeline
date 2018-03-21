#check current file path and set project accordingly
import maya.cmds as mc

def run(*args, **kwargs):
	filepath=mc.file(q=1, l=1)
	project="/".join(filepath.split("/")[:-2])
	mc.workspace(dir=project)
	print "Project Set To: %s"&project