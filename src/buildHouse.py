
from itertools import count
import bpy
import os
import random
from math import radians

def createHouse():
    ASSETS_PATH = 'D:/Dateien/Uni/Unterricht/5. Semester/DaVinMedPro/Code/DatenverarbeitungSoSe22/Assets/allAssets.blend'

    #Set the range for the diffrent parts for the house. 
    BOT_MIN = 1
    BOT_MAX = 4

    MID_MIN = 1
    MID_MAX = 3

    TOP_MIN = 1
    TOP_MAX = 3

    ROT_MIN = 1
    ROT_MAX = 361

    #Great new random values for each part of the house. 
    SELECT_BOT = random.randrange(BOT_MIN, BOT_MAX)
    SELCET_MID = random.randrange(MID_MIN,MID_MAX)
    SELECT_TOP = random.randrange(TOP_MIN,TOP_MAX)
    SELECT_ROT = random.randrange(ROT_MIN,ROT_MAX)

    collection = bpy.data.collections.new("House")
    bpy.context.scene.collection.children.link(collection)
    
    #Selcet bottom part for the new asset. 
    match SELECT_BOT:
        case 1:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'FensterDownOne'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            test = bpy.data.objects['downOne']
            test.rotation_euler[2] = radians(SELECT_ROT)
            bpy.data.collections['House'].objects.link(test)
          
        case 2:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'FensterDownTwo'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            test = bpy.data.objects['downTwo']
            test.rotation_euler[2] = radians(SELECT_ROT)
            bpy.data.collections['House'].objects.link(test)
        case 3:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'downThree'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            test = bpy.data.objects['downThree']
            test.rotation_euler[2] = radians(SELECT_ROT)
            bpy.data.collections['House'].objects.link(test)
    #Selcet middel part for the new asset. 
    match SELCET_MID:
        case 1:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'FensterMid'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            test = bpy.data.objects['mid']
            test.rotation_euler[2] = radians(SELECT_ROT)
            bpy.data.collections['House'].objects.link(test)
        case 2:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'FensterMidBalk'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            test = bpy.data.objects['midbalk']
            test.rotation_euler[2] = radians(SELECT_ROT)
            bpy.data.collections['House'].objects.link(test)
    #Selcet the roof part for the new asset. 
    match SELECT_TOP:
        case 1:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'topRed'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            test = bpy.data.objects['topRed']
            test.rotation_euler[2] = radians(SELECT_ROT)
            bpy.data.collections['House'].objects.link(test)
        case 2:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'topBlue'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            test = bpy.data.objects['topBlue']
            test.rotation_euler[2] = radians(SELECT_ROT)
            bpy.data.collections['House'].objects.link(test)


# Szene leeren
bpy.ops.object.select_all(action='SELECT') # selektiert alle Objekte
bpy.ops.object.delete(use_global=False, confirm=False) # löscht selektierte objekte
bpy.ops.outliner.orphans_purge() # löscht überbleibende Meshdaten etc.

createHouse()

 


