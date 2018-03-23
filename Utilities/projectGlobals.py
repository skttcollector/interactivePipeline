project="Frogger"
padding=4
filefolder="scenes"
defaultPath="//caddy/work/current/FROGGER_MAGFL-N400/Frogger/Production"
riggingPath="%s/Code/Maya/RiggingTools"%defaultPath

# project dictionary key=project name, value = project path
projects = {'OutOfBoxExperience': 'X:/Production', 'FitAndSetup': 'Y:/Production'}

# might need to the os.environ var to these paths if they're different for each project. . . 
rigFBXExport = "X:/Production/Code/Maya/Tools/PipelineTools/Python/Publishing/fbxPresets/rig_cm_triang_binary.fbxexportpreset"
animFBXExport = "X:/Production/Code/Maya/Tools/PipelineTools/Python/Publishing/fbxPresets/anim_cm_triang_binary.fbxexportpreset"
modelFBXExport = "X:/Production/Code/Maya/Tools/PipelineTools/Python/Publishng/fbxPresets/model_cm_triang_binary.fbxexportpreset"