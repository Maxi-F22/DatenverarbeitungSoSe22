import osmium as o
import shapely.wkb as wkblib
from shapely.geometry import mapping
import os
import random
from math import radians
import bpy

wkbfab = o.geom.WKBFactory()

OSM_PATH = 'D:/Dateien/Uni/Unterricht/5. Semester/DaVinMedPro/Code/DatenverarbeitungSoSe22/Assets/gottenheim.osm'
ASSETS_PATH = 'D:/Dateien/Uni/Unterricht/5. Semester/DaVinMedPro/Code/DatenverarbeitungSoSe22/Assets/allAssets.blend'
STREET_ASSETS_PATH = 'D:/Dateien/Uni/Unterricht/5. Semester/DaVinMedPro/Code/DatenverarbeitungSoSe22/Assets/street.blend'

# OSM_PATH = 'D:/Schule/Datenverarbeitung/DatenverarbeitungSoSe22/Assets/gottenheim.osm'
# ASSETS_PATH = 'D:/Schule/Datenverarbeitung/DatenverarbeitungSoSe22/Assets/allAssets.blend'
# STREET_ASSETS_PATH = 'D:/Schule/Datenverarbeitung/DatenverarbeitungSoSe22/Assets/street.blend'

class BuildingListHandler(o.SimpleHandler):
    # get bound coords of whole map
    f = o.io.Reader(OSM_PATH, o.osm.osm_entity_bits.NOTHING)
    box = f.header().box()
    left = str(box.bottom_left).split("/")[0]
    bottom = str(box.bottom_left).split("/")[1]
    right = str(box.top_right).split("/")[0]
    top = str(box.top_right).split("/")[1]

    map_bounds = {"minlat": float(bottom), "minlon": float(left), "maxlat": float(top), "maxlon": float(right)}

    buildings = []
    forests = []
    streets = []

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

    def way(self, w):
        if 'highway' in w.tags:
            wkb = wkbfab.create_linestring(w)
            poly = wkblib.loads(wkb, hex=True)
            bound = poly.coords
            coords = []
            for coord in list(bound):
                coords.append({"lat": coord[1], "lng": coord[0]})
            self.streets.append(coords)

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

def createForest():
    file_path = ASSETS_PATH
    inner_path = 'Object'
    bpy.ops.wm.append(
        filepath=os.path.join(file_path, inner_path, 'Cube'),
        directory=os.path.join(file_path, inner_path),
        filename='Cube'
    )
    bpy.ops.wm.append(
        filepath=os.path.join(file_path, inner_path, 'TreeTwo'),
        directory=os.path.join(file_path, inner_path),
        filename='TreeTwo'
    )
    bpy.ops.wm.append(
        filepath=os.path.join(file_path, inner_path, 'TreeThree'),
        directory=os.path.join(file_path, inner_path),
        filename='TreeThree'
    )
    obj = bpy.data.objects['Cube']
    for coll in obj.users_collection:
        # Unlink the object
        coll.objects.unlink(obj)
    obj = bpy.data.objects['TreeTwo']
    for coll in obj.users_collection:
        # Unlink the object
        coll.objects.unlink(obj)
    obj = bpy.data.objects['TreeThree']
    for coll in obj.users_collection:
        # Unlink the object
        coll.objects.unlink(obj)

    forest_collection = bpy.data.collections.get("Forests")
        
    if forest_collection:
        forest_objects = []
        for obj in forest_collection.objects:
            if obj.type == 'MESH':
                forest_objects.append(obj)
        ctx = bpy.context.copy()
        ctx['active_object'] = forest_objects[0]
        ctx['selected_editable_objects'] = forest_objects
        bpy.ops.object.join(ctx)

    if bpy.data.objects["forest0"]:
        forest_obj = bpy.data.objects["forest0"]
        forest_obj.modifiers.new("forestTreeOneParticles", type='PARTICLE_SYSTEM')
        forest_obj.modifiers.new("forestTreeTwoParticles", type='PARTICLE_SYSTEM')
        forest_obj.modifiers.new("forestTreeThreeParticles", type='PARTICLE_SYSTEM')
        forest_obj.show_instancer_for_render = False
        forest_obj.show_instancer_for_viewport = False

        for i in range(3):
            partTree = forest_obj.particle_systems[i]
            partTree.seed = random.randrange(1,100)
            settingsTree = partTree.settings
            settingsTree.particle_size = 0.3
            settingsTree.size_random = 0.1
            settingsTree.count = 2000
            settingsTree.type = 'HAIR'
            settingsTree.render_type = 'OBJECT'
            settingsTree.use_rotations = True
            settingsTree.rotation_mode = 'NONE'
            if i == 0:
                settingsTree.instance_object = bpy.data.objects["Cube"]
            elif i == 1:
                settingsTree.instance_object = bpy.data.objects["TreeTwo"]
            elif i == 2:
                settingsTree.instance_object = bpy.data.objects["TreeThree"]

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

def createStreet(_verts, _iteration):
    bpy.ops.wm.append(
        filepath=os.path.join(STREET_ASSETS_PATH, 'Object', 'StreetPart'),
        directory=os.path.join(STREET_ASSETS_PATH, 'Object'),
        filename='StreetPart'
    )
    street_collection = bpy.data.collections.get("Streets")
    
    obj = bpy.data.objects['StreetPart']
    obj.name = 'StreetPart' + str(_iteration)

    for coll in obj.users_collection:
        # Unlink the object
        coll.objects.unlink(obj)
    street_collection.objects.link(obj)

    curveData = bpy.data.curves.new('streetCurve' + str(_iteration), type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 2
    # map coords to spline
    polyline = curveData.splines.new('POLY')
    polyline.points.add(len(_verts)-1)
    for i, coord in enumerate(_verts):
        x,y,z = coord
        polyline.points[i].co = (x, y, z, 1)
    # create Object
    curveObj = bpy.data.objects.new('street' + str(_iteration), curveData)
    curveData.bevel_depth = 0.01

    # add modifiers to align and multiply StreetPart to Street
    obj.modifiers.new('StreetPartArray' + str(_iteration), type='ARRAY')
    obj.modifiers['StreetPartArray' + str(_iteration)].fit_type = 'FIT_CURVE'
    obj.modifiers['StreetPartArray' + str(_iteration)].curve = curveObj
    obj.modifiers.new('StreetPartCurve' + str(_iteration), type='CURVE')
    obj.modifiers['StreetPartCurve' + str(_iteration)].object = curveObj

    # attach to collection
    street_collection.objects.link(curveObj)

    # create vehicles on streets
    if len(_verts) > 2:
        bpy.ops.wm.append(
            filepath=os.path.join(ASSETS_PATH, 'Object', 'Wagen'),
            directory=os.path.join(ASSETS_PATH, 'Object'),
            filename='Wagen'
        )
            
        objWagon = bpy.data.objects['Wagen']
        objWagon.name = 'Wagon' + str(_iteration)
        for coll in objWagon.users_collection:
            # Unlink the object
            coll.objects.unlink(objWagon)

        street_collection.objects.link(objWagon)

        wagonLoc = random.randrange(1, len(_verts)-1)
        x,y,z = _verts[wagonLoc]
        objWagon.location.x = x
        objWagon.location.y = y
        objWagon.location.z = 0.8


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
    try: 
        mat.node_tree.nodes['Principled BSDF']
    except:
        pass
    else:
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
    
def map(_mapLength, _mapWidth, _latSouth, _latNorth, _longWest, _longEast, _buildings, _forests, _streets):
    lat_calc = (_mapLength) / (_latNorth - _latSouth)
    long_calc = (_mapWidth) / -((_longWest - _longEast))
    a = 0
    a_forest = 0
    a_streets = 0
    createFloor(_mapLength + 100, _mapWidth + 100)

    forest_collection = bpy.data.collections.new("Forests")
    bpy.context.scene.collection.children.link(forest_collection)
    street_collection = bpy.data.collections.new("Streets")
    bpy.context.scene.collection.children.link(street_collection)

    while a_forest < len(_forests):
        forest_verts = []
        for forest_border in _forests[a_forest]["coords"]:
            alat_forest = float(forest_border["lat"]) - _latSouth
            along_forest = float(forest_border["lng"]) - _longWest
            x_forest = lat_calc * alat_forest
            y_forest = long_calc * along_forest
            forest_verts.append((x_forest + 50, - (y_forest - 50), 0))

        faces = [[i for i in range(len(forest_verts)-1)]]

        mesh = bpy.data.meshes.new("forest" + str(a_forest))
        mesh.from_pydata(vertices=forest_verts, edges=[], faces=faces)
        mesh.update()

        obj = bpy.data.objects.new("forest" + str(a_forest), mesh)
        forest_collection.objects.link(obj)

        a_forest += 1
  
    # while a < len(_buildings):
    while a < 20:
        alat = float(_buildings[a]["lat"]) - _latSouth
        along = float(_buildings[a]["lng"]) - _longWest
        x = lat_calc * alat
        y = long_calc * along
        createHouse(x + 50, - (y - 50), a)
        a += 1

    while a_streets < len(_streets):
        street_verts = []

        for street in _streets[a_streets]:
            alat_street = float(street["lat"]) - _latSouth
            along_street = float(street["lng"]) - _longWest
            x_street = lat_calc * alat_street
            y_street = long_calc * along_street
            street_verts.append((x_street + 50, - (y_street - 50), 0))

        createStreet(street_verts, a_streets)
        
        a_streets += 1

    createForest()

def main(_osmfile):
    handler = BuildingListHandler()

    ml = 300
    lats = handler.map_bounds["minlat"]
    latn = handler.map_bounds["maxlat"]
    mw = 700
    lonw = handler.map_bounds["minlon"]
    lone = handler.map_bounds["maxlon"]

    handler.apply_file(_osmfile)

    buildings = handler.buildings
    forests = handler.forests
    streets = handler.streets

    bpy.ops.object.select_all(action='SELECT') # selektiert alle Objekte
    bpy.ops.object.delete(use_global=False, confirm=False) # löscht selektierte objekte
    bpy.ops.outliner.orphans_purge() # löscht überbleibende Meshdaten etc.
    for col in bpy.data.collections:
        bpy.data.collections.remove(col)

    createWindowMaterialDay()
    createWindowMaterialNight()
    addWorldSun()

    map(ml, mw, lats, latn, lonw, lone, buildings, forests, streets)

if __name__ == '__main__':
    main(OSM_PATH)