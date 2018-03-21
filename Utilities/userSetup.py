import maya.cmds as mc
import maya.mel as mel
import sys

print "In user setup"

current = r"\\caddybak\BuckInteractive\pipelineTools\current\interactivePipelineTools"
development = r"\\caddybak\BuckInteractive\pipelineTools\development\interactivePipelineTools"

#change this to set the pipeline tools to development (git repo) or to current (should be default)
pipelineTools = current

if pipelineTools not in sys.path:
    sys.path.insert(0, pipelineTools)
    
#build frogger project menu
def buildFrogger(*args, **kwargs):
    import FroggerMenu_v01 as fm
    reload(fm)
    fm.Menu()

try:
    mc.evalDeferred("buildFrogger()")
except:
    print "\n-----FROGGER MENU FAILED TO LOAD-----\n"