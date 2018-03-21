import maya.cmds as cmds
import maya.mel as mel
#from pyautogui import press

# write out a preset!!!
# mel.eval("gameExp_SaveAttrPreset;")

# change the values in the preset to the correct ones (mostly paths, but could check on other stuff as well, ORRR use a template

# test object export sets - does it cycle through each set to make a new file?

sn = "X:/Production/Assets/3D/Character/testAsset/Animation/Publish/MB/cloudTest_v0001/testAsset_cloudTest_Animation_Cloud_main_Rig7_v0001.mb"

nodes = mel.eval("gameExp_GetGameFbxExporterNodeList()")
preset = "C:/Users/zethwillie/Desktop/gameExportPresetExample.mel"

mel.eval("gameFbxExporter;")
mel.eval('gameExp_ApplyPresetOnNode("{0}", "{1}");'.format(nodes[-1], preset))

mel.eval('gameExp_DoExport;')

cmds.file(sn, open=True, f=True)


message
caching
isHistoricallyInteresting
nodeState
binMembership
frozen
presetName
overridePresetValue
isTheLastOneSelected
isTheLastOneUsed
useFilenameAsPrefix
viewInFBXReview
exportTypeIndex
exportSetIndex
selectionSetName
smoothingGroups
splitVertexNormals
tangentsBinormals
smoothMesh
selectionSets
convertToNullObj
preserveInstances
referencedAssetsContent
triangulate
convertNurbsSurfaceTo
exportAnimation
useSceneName
removeSingleKey
quarternionInterpMode
animClips
animClips.animClipName
animClips.animClipStart
animClips.animClipEnd
animClips.exportAnimClip
animClips.animClipId
animClips.animClipSrcNode
fileSplitType
includeCombinedClips
bakeAnimation
bakeAnimStart
bakeAnimEnd
bakeAnimStep
resampleAll
deformedModels
skinning
blendshapes
curveFilters
constantKeyReducer
ckrTranslationPrecision
ckrRotationPrecision
ckrScalingPrecision
ckrOtherPrecision
ckrAutoTangentOnly
constraints
skeletonDefinitions
includeCameras
includeLights
upAxis
embedMedia
inputConnections
autoScaleFactor
unitConversion
showWarningManager
generateLogData
fileType
fileVersion
exportPath
exportFilename


setAttr("gameExporterPreset2.animClips[0].animClipStart") 5;

print cmds.getAttr("{0}.animClips[0].animClipName".format(ge))

numClips = cmds.getAttr("{0}.animClips".format(ge), size=True)
print cmds.getAttr("{0}.animClips[0].animClipName".format(ge))
path = "some/path/to/some/shit"
filename = "yyaaaa"
cmds.setAttr("{0}.exportPath".format(ge), path, type="string")
cmds.setAttr("{0}.exportFilename".format(ge), filename, type="string")