import osmium as o
import shapely.wkb as wkblib
from shapely.geometry import mapping
import os
import random
from math import radians
import bpy

wkbfab = o.geom.WKBFactory()

#OSM_PATH = 'D:/Dateien/Uni/Unterricht/5. Semester/DaVinMedPro/Code/DatenverarbeitungSoSe22/Assets/gottenheim.osm'
#ASSETS_PATH = 'D:/Dateien/Uni/Unterricht/5. Semester/DaVinMedPro/Code/DatenverarbeitungSoSe22/Assets/allAssets.blend'

OSM_PATH = 'D:/Schule/Datenverarbeitung/DatenverarbeitungSoSe22/Assets/gottenheim.osm'
ASSETS_PATH = 'D:/Schule/Datenverarbeitung/DatenverarbeitungSoSe22/Assets/allAssets.blend'

class BuildingListHandler(o.SimpleHandler):

    buildings = []
    forests = []

    def area(self, a):
        if 'building' in a.tags:
            wkb = wkbfab.create_multipolygon(a)
            poly = wkblib.loads(wkb, hex=True)
            centroid = poly.centroid
            self.buildings.append({"lat": centroid.y, "lng": centroid.x})
        
        elif 'natural' or 'landuse' in a.tags:
            wkb = wkbfab.create_multipolygon(a)
            poly = wkblib.loads(wkb, hex=True)
            bound = poly.boundary
            centroid = poly.centroid
            coords = []
            for coord in mapping(bound)["coordinates"]:
                for point_coord in coord:
                    coords.append({"lat": point_coord[1], "lng": point_coord[0]})
            self.forests.append({"center": (centroid.x, centroid.y, 0), "coords": coords})
        

def createHouse(_coordX, _coordY, _iteration):
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
    SELECT_BOT = random.randrange(BOT_MIN,BOT_MAX)
    SELECT_MID = random.randrange(MID_MIN,MID_MAX)
    SELECT_TOP = random.randrange(TOP_MIN,TOP_MAX)
    SELECT_ROT = random.randrange(ROT_MIN,ROT_MAX)

    collection = bpy.data.collections.new("HouseNr" + str(_iteration))
    bpy.context.scene.collection.children.link(collection)
    
    #Select bottom part for the new asset. 
    match SELECT_BOT:
        case 1:
            #load the first part of the house
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'FensterDownOne'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            #rename the object 
            obj = bpy.data.objects['downOne']
            obj.name = 'downOne' + str(_iteration)
            objWindows = bpy.data.objects['FensterDownOne']
            objWindows.name = 'FensterDownOne' + str(_iteration)

            #set the right window material for the choosen Time
            checkDayAndNight(objWindows)
            #add random rotation and the right position. 
            obj.rotation_euler[2] = radians(SELECT_ROT)
            obj.location[0] = _coordX
            obj.location[1] = _coordY
            for coll in objWindows.users_collection:
                # Unlink the object
                coll.objects.unlink(objWindows)
            collection.objects.link(objWindows)
            for coll in obj.users_collection:
                # Unlink the object
                coll.objects.unlink(obj)
            collection.objects.link(obj)      
        case 2:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'FensterDownTwo'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            obj = bpy.data.objects['downTwo']
            obj.name = 'downTwo' + str(_iteration)
            objWindows = bpy.data.objects['FensterDownTwo']
            objWindows.name = 'FensterDownTwo' + str(_iteration)

            checkDayAndNight(objWindows)
            obj.rotation_euler[2] = radians(SELECT_ROT)
            obj.location[0] = _coordX
            obj.location[1] = _coordY
            for coll in objWindows.users_collection:
                # Unlink the object
                coll.objects.unlink(objWindows)
            collection.objects.link(objWindows)
            for coll in obj.users_collection:
                # Unlink the object
                coll.objects.unlink(obj)
            collection.objects.link(obj)
        case 3:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'downThree'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            obj = bpy.data.objects['downThree']
            obj.name = 'downThree' + str(_iteration)
            obj.rotation_euler[2] = radians(SELECT_ROT)
            obj.location[0] = _coordX
            obj.location[1] = _coordY
            for coll in obj.users_collection:
                # Unlink the object
                coll.objects.unlink(obj)
            collection.objects.link(obj)
    #Select middle part for the new asset. 
    match SELECT_MID:
        case 1:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'FensterMid'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            obj = bpy.data.objects['mid']
            obj.name = 'mid' + str(_iteration)
            objWindows = bpy.data.objects['FensterMid']
            objWindows.name = 'FensterMid' + str(_iteration)

            checkDayAndNight(objWindows)
            obj.rotation_euler[2] = radians(SELECT_ROT)
            obj.location[0] = _coordX
            obj.location[1] = _coordY
            for coll in objWindows.users_collection:
                # Unlink the object
                coll.objects.unlink(objWindows)
            collection.objects.link(objWindows)
            for coll in obj.users_collection:
                # Unlink the object
                coll.objects.unlink(obj)
            collection.objects.link(obj)
        case 2:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'FensterMidBalk'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            obj = bpy.data.objects['midbalk']
            obj.name = 'midbalk' + str(_iteration)
            objWindows = bpy.data.objects['FensterMidBalk']
            objWindows.name = 'FensterMidBalk' + str(_iteration)

            checkDayAndNight(objWindows)
            obj.rotation_euler[2] = radians(SELECT_ROT)
            obj.location[0] = _coordX
            obj.location[1] = _coordY
            for coll in objWindows.users_collection:
                # Unlink the object
                coll.objects.unlink(objWindows)
            collection.objects.link(objWindows)
            for coll in obj.users_collection:
                # Unlink the object
                coll.objects.unlink(obj)
            collection.objects.link(obj)
    #Select the roof part for the new asset. 
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
            obj = bpy.data.objects['topRed']
            obj.name = 'topRed' + str(_iteration)
            obj.rotation_euler[2] = radians(SELECT_ROT)
            obj.location[0] = _coordX
            obj.location[1] = _coordY
            for coll in obj.users_collection:
                # Unlink the object
                coll.objects.unlink(obj)
            collection.objects.link(obj)
        case 2:
            file_path = ASSETS_PATH
            inner_path = 'Object'
            object_name = 'topBlue'
 
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
            obj = bpy.data.objects['topBlue']
            obj.name = 'topBlue' + str(_iteration)
            obj.rotation_euler[2] = radians(SELECT_ROT)
            obj.location[0] = _coordX
            obj.location[1] = _coordY
            for coll in obj.users_collection:
                # Unlink the object
                coll.objects.unlink(obj)
            collection.objects.link(obj)

def createFloor(_length, _width):
    bpy.ops.mesh.primitive_plane_add(size=1)
    obj = bpy.data.objects['Plane']
    obj.scale = (_length, _width, 1)
    obj.location = (_length / 2, - (_width / 2), 0)

    mat_floor = bpy.data.materials.new("Floor Material")
    mat_floor.use_nodes = True
    nodes_floor = mat_floor.node_tree.nodes
    nodes_floor["Principled BSDF"].inputs[0].default_value = [0, 0.3, 0, 1.000000]

    obj.data.materials.append(mat_floor)

def map(_mapLength, _mapWidth, _latSouth, _latNorth, _longWest, _longEast, _buildings, _forests):
    lat_calc = (_mapLength) / (_latNorth - _latSouth)
    long_calc = (_mapWidth) / -((_longWest - _longEast))
    a = 0
    a_forest = 0
    createFloor(_mapLength + 100, _mapWidth + 100)

    file_path = ASSETS_PATH
    inner_path = 'Object'
    object_name = 'TreeTwo'

    bpy.ops.wm.append(
        filepath=os.path.join(file_path, inner_path, object_name),
        directory=os.path.join(file_path, inner_path),
        filename=object_name
    )
    obj = bpy.data.objects['TreeTwo']
    for coll in obj.users_collection:
        # Unlink the object
        coll.objects.unlink(obj)

    while a_forest < len(_forests):
        forest_verts = []
        for forest_border in _forests[a_forest]["coords"]:
            alat_forest = float(forest_border["lat"]) - _latSouth
            along_forest = float(forest_border["lng"]) - _longWest
            x_forest = lat_calc * alat_forest
            y_forest = long_calc * along_forest
            forest_verts.append((x_forest, -y_forest, 0))

        edges = [[i, i+1] for i in range(len(forest_verts)-1)]
        faces = [[i for i in range(len(forest_verts)-1)]]

        mesh = bpy.data.meshes.new("forest" + str(a_forest))
        mesh.from_pydata(forest_verts, edges, faces)
        mesh.update()

        obj = bpy.data.objects.new("forest" + str(a_forest), mesh)

        obj.modifiers.new("forestParticles" + str(a_forest), type='PARTICLE_SYSTEM')
        part = obj.particle_systems[0]
        settings = part.settings
        settings.name = "forestParticlesSettings" + str(a_forest)
        settings.particle_size = 0.25
        settings.size_random = 0.1
        settings.count = 100
        settings.type = 'HAIR'
        settings.render_type = 'OBJECT'
        settings.use_rotations = True
        settings.rotation_mode = 'NONE'
        settings.instance_object = bpy.data.objects["TreeTwo"]

        bpy.context.scene.collection.objects.link(obj)

        a_forest += 1

    # while a < len(_buildings):
    while a < 20:
        alat = float(_buildings[a]["lat"]) - _latSouth
        along = float(_buildings[a]["lng"]) - _longWest
        x = lat_calc * alat
        y = long_calc * along
        createHouse(x, -y, a)
        a += 1

def createWindowMaterialDay():
    #Create the normal blue Window color
    material = bpy.data.materials.new(name='Fenster')
    material.use_nodes=True
    material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.211,0.629,0.636,1.0)

def createWindowMaterialNight():
    # Create the material for the night version 
    material = bpy.data.materials.new(name='Licht_Fenster')
    material.use_nodes=True

    #Delete Principled BSDF
    mat = bpy.data.materials['Licht_Fenster']
    node_to_delete =  mat.node_tree.nodes['Principled BSDF']
    mat.node_tree.nodes.remove( node_to_delete )

    #Add Emission Shader
    emission_Node = mat.node_tree.nodes.new('ShaderNodeEmission')
    emission_Node.location = (0,320)

    #Add right values to the shader
    emission_Node.inputs[0].default_value = (1.0,0.534,0.029,1.0)
    emission_Node.inputs[1].default_value = 4.0
    
    #Conect nodes
    shaderOutput = mat.node_tree.nodes.get('Material Output')
    mat.node_tree.links.new(emission_Node.outputs[0], shaderOutput.inputs[0] )
    
    #Configure scene settings 
    eeveeObj = bpy.data.scenes['Scene'].eevee
    eeveeObj.use_bloom = True
    eeveeObj.bloom_color = (1.0,0.425,0.006)
    eeveeObj.bloom_intensity = 0.5

def checkDayAndNight(objWindows):
    dayNightSet = False
    #Check if user set checkbox for the day or night time
    if(dayNightSet==False):
        #set window material 
        mat = bpy.data.materials.get('Fenster')
        objWindows.data.materials.append(mat)
        
        #change the color of the sun to night
        sonne = bpy.data.lights.get('Sonne')
        sonne.color = (1,0.828,0.676)

        #change world background-color
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.163,0.135,0.110,1)
        
    elif(dayNightSet==True):
        #set window material 
        mat = bpy.data.materials.get('Licht_Fenster')
        objWindows.data.materials.append(mat)

        #change the color of the sun to night
        sonne = bpy.data.lights.get('Sonne')
        sonne.color = (0.107,0.122,0.298)

        #change world background-color
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0,0,0,1)

def addWorldSun():
    # create light and set attributes
    sun_data = bpy.data.lights.new(name="Sonne", type='SUN')
    sun_data.energy = 1

    # create new object with the sun 
    sonne = bpy.data.objects.new(name="Sonne", object_data=sun_data)

    # link light object
    bpy.context.collection.objects.link(sonne)

    # make it active 
    bpy.context.view_layer.objects.active = sonne

    #change location and rotation of the sun
    sonne.location = (-39, -284, 40)
    sonne.rotation_euler[0]= radians(-19)
    sonne.rotation_euler[1]= radians(-43)
    sonne.rotation_euler[2]= radians(8)
    
def main(_osmfile):
    ml = 300
    lats = 48.0489500
    latn = 48.0520900
    mw = 700
    lonw = 7.7151600
    lone = 7.7235800

    handler = BuildingListHandler()

    handler.apply_file(_osmfile)

    buildings = handler.buildings
    forests = handler.forests

    bpy.ops.object.select_all(action='SELECT') # selektiert alle Objekte
    bpy.ops.object.delete(use_global=False, confirm=False) # löscht selektierte objekte
    bpy.ops.outliner.orphans_purge() # löscht überbleibende Meshdaten etc.
    for col in bpy.data.collections:
        bpy.data.collections.remove(col)

    createWindowMaterialDay()
    createWindowMaterialNight()
    addWorldSun()

    map(ml, mw, lats, latn, lonw, lone, buildings, forests)

if __name__ == '__main__':
    main(OSM_PATH)