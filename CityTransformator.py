from pydoc import describe
import osmium as o
import shapely.wkb as wkblib
from shapely.geometry import mapping
import os
import random
from math import radians
import bpy

bl_info = {
    "name" : "City Transformator",
    "description" : "Builds a medieval looking, low-poly style city with houses, roads and forests from real-world map data.",
    "author" : "Felix Iltgen, Maximilian Flack",
    "version" : (1, 0, 0),
    "blender" : (3, 1, 0),
    "category" : "Add Mesh",
}

user_asset_path = os.path.expanduser('~\Documents\Blender\Assets')

wkbfab = o.geom.WKBFactory()

OSM_PATH = user_asset_path + "\\map.osm"
ASSETS_PATH = user_asset_path + "\\allAssets.blend"

MAP_LENGTH = 300
MAP_WIDTH = 700
LAT_SOUTH = 0
LAT_NORTH = 0
LON_WEST = 0
LON_EAST = 0
BUILDINGS = []
FORESTS = []
STREETS = []

PROP_NIGHTTIME = False
PROP_EPOXY = False
PROP_NUMBER_HOUSES = 0
PROP_NUMBER_TREES = 0
PROP_NUMBER_GRASS = 0

class PanelProps(bpy.types.PropertyGroup):
    bl_idname = "Props"

    time_night: bpy.props.BoolProperty(name="Nighttime", description="Sets the boolean value if the time in the model should be night.", default=False)

    epoxy_model: bpy.props.BoolProperty(name="Epoxy Model", description="Sets the boolean value if the model should be surrounded by an epoxy layer.", default=False)

    houses_count: bpy.props.IntProperty(name="House Count", description="Sets the maximum number of houses in the model.", soft_min=0, soft_max=1000, default=20)

    trees_count: bpy.props.IntProperty(name="Tree Count", description="Sets the maximum number of each tree type (3 total).", soft_min=0, soft_max=4000, default=400)

    grass_count: bpy.props.IntProperty(name="Grass Count", description="Sets the maximum number of grass shrouds.", soft_min=0, soft_max=6000, default=1000)

class TRANSFORMATOR_PT_panel(bpy.types.Panel):
    """Creates a Panel for User Interaction in the scene context of the properties editor"""
    bl_label = "City Transformator"
    bl_idname = "TRANSFORMATOR_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Transformator Addon'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = scene.prop_data

        row1 = layout.row()
        row2 = layout.row()
        row3 = layout.row()
        row4 = layout.row()
        row5 = layout.row()
        row1.prop(data, "time_night")
        row2.prop(data, "epoxy_model")
        row3.prop(data, "houses_count")
        row4.prop(data, "trees_count")
        row5.prop(data, "grass_count")
        layout.operator('button.execute', text='Transform')

class executeAction(bpy.types.Operator):
    bl_idname = "button.execute"
    bl_label = "execute"

    def execute(self, context):
        global PROP_NIGHTTIME, PROP_EPOXY, PROP_NUMBER_HOUSES, PROP_NUMBER_TREES, PROP_NUMBER_GRASS
        PROP_NIGHTTIME = bpy.data.scenes["Scene"].prop_data.time_night
        PROP_EPOXY = bpy.data.scenes["Scene"].prop_data.epoxy_model
        PROP_NUMBER_HOUSES = bpy.data.scenes["Scene"].prop_data.houses_count
        PROP_NUMBER_TREES = bpy.data.scenes["Scene"].prop_data.trees_count
        PROP_NUMBER_GRASS = bpy.data.scenes["Scene"].prop_data.grass_count

        CityTransformator().start()
        return {'FINISHED'}

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
            if 'amenity' in a.tags:
                pass
            else:
                if a.tags.get('landuse') != 'residential' and a.tags.get('natural') != 'water':
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

class CityTransformator():
    def start(self):
        bpy.ops.object.select_all(action='SELECT') # selektiert alle Objekte
        bpy.ops.object.delete(use_global=False, confirm=False) # löscht selektierte objekte
        bpy.ops.outliner.orphans_purge() # löscht überbleibende Meshdaten etc.
        for col in bpy.data.collections:
            bpy.data.collections.remove(col)
        CityTransformator.createWindowMaterialDay()
        CityTransformator.createWindowMaterialNight()
        CityTransformator.addWorldSun()
        CityTransformator.createMap(MAP_LENGTH, MAP_WIDTH, LAT_SOUTH, LAT_NORTH, LON_WEST, LON_EAST, BUILDINGS, FORESTS, STREETS)

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
                CityTransformator.checkDayAndNight(objWindows)
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

                CityTransformator.checkDayAndNight(objWindows)
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

                CityTransformator.checkDayAndNight(objWindows)
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

                CityTransformator.checkDayAndNight(objWindows)
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

    def createForest(_length, _width):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(_length / 2, -(_width / 2), 45), scale=(_length - 10, _width - 10, 100))
        obj = bpy.data.objects['Cube']
        obj.name = "BoundingBox"
        cube_obj = bpy.data.objects['BoundingBox']
        file_path = ASSETS_PATH
        inner_path = 'Object'
        bpy.ops.wm.append(
            filepath=os.path.join(file_path, inner_path, 'TreeOne'),
            directory=os.path.join(file_path, inner_path),
            filename='TreeOne'
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
        obj = bpy.data.objects['TreeOne']
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
            
        if len(forest_collection.objects) > 0:
            forest_objects = []
            for obj in forest_collection.objects:
                if obj.type == 'MESH':
                    forest_objects.append(obj)
            ctx = bpy.context.copy()
            ctx['active_object'] = forest_objects[0]
            ctx['selected_editable_objects'] = forest_objects
            bpy.ops.object.join(ctx)

            try:
                bpy.data.objects["forest0"]
            except:
                pass
            else:
                forest_obj = bpy.data.objects["forest0"]
                forest_obj.modifiers.new("forestTreeOneParticles", type='PARTICLE_SYSTEM')
                forest_obj.modifiers.new("forestTreeTwoParticles", type='PARTICLE_SYSTEM')
                forest_obj.modifiers.new("forestTreeThreeParticles", type='PARTICLE_SYSTEM')
                forest_obj.show_instancer_for_render = False
                forest_obj.show_instancer_for_viewport = False

                for i in range(3):
                    partTree = forest_obj.particle_systems[i]
                    partTree.seed = random.randrange(1,101)
                    settingsTree = partTree.settings
                    settingsTree.particle_size = 0.3
                    settingsTree.size_random = 0.1
                    settingsTree.count = PROP_NUMBER_TREES
                    settingsTree.type = 'HAIR'
                    settingsTree.render_type = 'OBJECT'
                    settingsTree.use_rotations = True
                    settingsTree.rotation_mode = 'OB_Z'
                    settingsTree.phase_factor_random = 2
                    settingsTree.distribution = 'RAND'
                    if i == 0:
                        settingsTree.instance_object = bpy.data.objects["TreeOne"]
                    elif i == 1:
                        settingsTree.instance_object = bpy.data.objects["TreeTwo"]
                    elif i == 2:
                        settingsTree.instance_object = bpy.data.objects["TreeThree"]
                
                forest_obj.modifiers.new('forestBoolean', type='BOOLEAN')
                forest_obj.modifiers['forestBoolean'].object = cube_obj
                forest_obj.modifiers['forestBoolean'].solver = 'FAST'
                forest_obj.modifiers['forestBoolean'].operation = 'INTERSECT'
                bpy.context.view_layer.objects.active = forest_obj
                bpy.ops.object.modifier_apply(modifier="forestBoolean")

        for coll in cube_obj.users_collection:
            # Unlink the object
            coll.objects.unlink(cube_obj)


    def createFloor(_length, _width):
        bpy.ops.mesh.primitive_plane_add(size=1)
        objFloorPlane = bpy.data.objects['Plane']
        objFloorPlane.name = "FloorPlane"
        objFloorPlane.scale = (_length, _width, 1)
        objFloorPlane.location = (_length / 2, - (_width / 2), 0)

        bpy.ops.mesh.primitive_cube_add(size=1, location=(_length / 2, -(_width / 2), -2.5), scale=(_length, _width, 5))
        obj = bpy.data.objects['Cube']
        obj.name = "Floor"

        mat_floor = bpy.data.materials.new("Floor Material")
        mat_floor.use_nodes = True
        nodes_floor = mat_floor.node_tree.nodes
        nodes_floor["Principled BSDF"].inputs[0].default_value = [0.01498, 0.238117, 0.015376, 1]
        mat_ground = bpy.data.materials.new("Ground Material")
        mat_ground.use_nodes = True
        nodes_ground = mat_ground.node_tree.nodes
        nodes_ground["Principled BSDF"].inputs[0].default_value = [0.096283, 0.051237, 0.001711, 1]

        objFloorPlane.data.materials.append(mat_floor)
        obj.data.materials.append(mat_ground)

        file_path = ASSETS_PATH
        inner_path = 'Object'
        bpy.ops.wm.append(
            filepath=os.path.join(file_path, inner_path, 'Grass'),
            directory=os.path.join(file_path, inner_path),
            filename='Grass'
        )
        objGrass = bpy.data.objects['Grass']
        for coll in obj.users_collection:
            # Unlink the object
            coll.objects.unlink(objGrass)
        objFloorPlane.modifiers.new("grassShrubParticles", type='PARTICLE_SYSTEM')

        partGrass = objFloorPlane.particle_systems[0]
        partGrass.seed = random.randrange(1,101)
        settingsGrass = partGrass.settings
        settingsGrass.particle_size = 2
        settingsGrass.size_random = 0.2
        settingsGrass.count = PROP_NUMBER_GRASS
        settingsGrass.type = 'HAIR'
        settingsGrass.render_type = 'OBJECT'
        settingsGrass.use_rotations = True
        settingsGrass.rotation_mode = 'OB_Z'
        settingsGrass.phase_factor_random = 2

        settingsGrass.instance_object = objGrass

    def createStreet(_verts, _width, _height, _iteration):
        curveData = bpy.data.curves.new('streetCurve' + str(_iteration), type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        # map coords to spline
        polyline = curveData.splines.new('POLY')
        polypoints = []
        for coord in _verts:
            x,y,z = coord
            if x > 0 and x <= _width and y < 0 and y >= -_height:
                polypoints.append((x,y,z,1))
        polyline.points.add(len(polypoints) - 1)
        for i, coords in enumerate(polypoints):
            polyline.points[i].co = coords

        # only create streets if it has more than 2 vert in bounds
        if len(polyline.points) > 2:
            
            bpy.ops.wm.append(
                filepath=os.path.join(ASSETS_PATH, 'Object', 'StreetPart'),
                directory=os.path.join(ASSETS_PATH, 'Object'),
                filename='StreetPart'
            )
            street_collection = bpy.data.collections.get("Streets")
            
            obj = bpy.data.objects['StreetPart']
            obj.name = 'StreetPart' + str(_iteration)

            for coll in obj.users_collection:
                # Unlink the object
                coll.objects.unlink(obj)
            street_collection.objects.link(obj)

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

            wagonLoc = random.randrange(1, len(polyline.points)-1)
            x,y,z,a = polyline.points[wagonLoc].co
            objWagon.location.x = x
            objWagon.location.y = y
            objWagon.location.z = 0.8
            objWagon.rotation_euler[2] = radians(random.randrange(0, 361))


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

    def checkDayAndNight(_objWindows):
        dayNightSet = PROP_NIGHTTIME
        #Check if user set checkbox for the day or night time
        if(dayNightSet==False):
            #set window material 
            mat = bpy.data.materials.get('Fenster')
            _objWindows.data.materials.append(mat)
            
            #change the color of the sun to night
            sonne = bpy.data.lights.get('Sonne')
            sonne.color = (1,0.828,0.676)

            #change world background-color
            bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.163,0.135,0.110,1)
            
        elif(dayNightSet==True):
            #set window material 
            mat = bpy.data.materials.get('Licht_Fenster')
            _objWindows.data.materials.append(mat)

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

        
    def createEpoxy(_length, _width):
        setEpoxy = PROP_EPOXY
        if(setEpoxy==False):
            print("Epoxy Version wurde nicht ausgewählt. Das Modell wird ohne Epoxy-Erweiterung erstellt.")
        elif(setEpoxy==True):
            print("Das Model wurde in ein Epoxit-Harz-Modell umgewandelt.")
            
            #create epoxy material
            material = bpy.data.materials.new(name='Acryl')
            material.use_nodes=True
            mat = bpy.data.materials['Acryl']

            #remove link from Principled BSDF
            try: 
                mat.node_tree.nodes['Principled BSDF'].outputs['BSDF'].links[0]
            except:
                pass
            else:
                link = mat.node_tree.nodes['Principled BSDF'].outputs['BSDF'].links[0]
                mat.node_tree.links.remove(link)

            #add the right settings for Principled BSDF
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            bsdf.inputs[9].default_value = 0.0
            bsdf.inputs[17].default_value = 1.0
            bsdf.location = (0,0)

            #add Mix Shader & connect with Material Output
            mixed_Node = mat.node_tree.nodes.new('ShaderNodeMixShader')
            mixed_Node.location = (800,-300)
            shaderOutput = mat.node_tree.nodes.get('Material Output')
            shaderOutput.location = (1000,0)
            mat.node_tree.links.new(mixed_Node.outputs[0], shaderOutput.inputs[0] )

            #connect Principled BSDF with Mix Shader
            mat.node_tree.links.new(bsdf.outputs[0], mixed_Node.inputs[2] )

            #add Transparent BSDF & connect with Mix Shader
            transparent_Node = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
            transparent_Node.location = (0,100)
            mat.node_tree.links.new(transparent_Node.outputs[0], mixed_Node.inputs[1] )

            #add Frensel
            fresnel_Node = mat.node_tree.nodes.new('ShaderNodeFresnel')
            fresnel_Node.location = (0,230)

            #add Color Ramp
            colorRamp_Node = mat.node_tree.nodes.new('ShaderNodeValToRGB') 
            colorRamp_Node.location = (200,300)

            # conect Frensel with Color Ramp & Color Ramp with Mix Shader
            mat.node_tree.links.new(fresnel_Node.outputs[0], colorRamp_Node.inputs[0] )
            mat.node_tree.links.new(colorRamp_Node.outputs[0], mixed_Node.inputs[0] )

            #set diffrent settings 
            mat.use_screen_refraction = True
            mat.blend_method = ("HASHED")
            mat.shadow_method = ("HASHED")
            bpy.data.scenes["Scene"].eevee.use_ssr = True
            bpy.data.scenes["Scene"].eevee.use_ssr_refraction = True
            
            #add cube and apply epoxy material 
            bpy.ops.mesh.primitive_cube_add(size=1)
            objCube = bpy.data.objects['Cube']
            objCube.name = "GlasCube"
            objCube.data.materials.append(mat)

            #move and sccale the cube to the right size
            objCube.location = (_length / 2, - (_width / 2), 40)
            objCube.scale[0] = _length
            objCube.scale[1] = _width
            objCube.scale[2] = 90

        
    def createMap(_mapLength, _mapWidth, _latSouth, _latNorth, _longWest, _longEast, _buildings, _forests, _streets):
        lat_calc = (_mapLength) / (_latNorth - _latSouth)
        long_calc = (_mapWidth) / -((_longWest - _longEast))
        a = 0
        a_forest = 0
        a_streets = 0
        CityTransformator.createFloor(_mapLength + 100, _mapWidth + 100)
        CityTransformator.createEpoxy(_mapLength + 100, _mapWidth + 100)

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
                forest_verts.append((x_forest + 50, - (y_forest + 50), 0))

            faces = [[i for i in range(len(forest_verts)-1)]]

            mesh = bpy.data.meshes.new("forest" + str(a_forest))
            mesh.from_pydata(vertices=forest_verts, edges=[], faces=faces)
            mesh.update()

            obj = bpy.data.objects.new("forest" + str(a_forest), mesh)
            forest_collection.objects.link(obj)

            a_forest += 1
        if len(BUILDINGS) > PROP_NUMBER_HOUSES:
            while a < PROP_NUMBER_HOUSES:
                alat = float(_buildings[a]["lat"]) - _latSouth
                along = float(_buildings[a]["lng"]) - _longWest
                x = lat_calc * alat
                y = long_calc * along
                CityTransformator.createHouse(x + 50, - (y + 50), a)
                a += 1
        else:
            bpy.data.scenes["Scene"].prop_data.houses_count = len(BUILDINGS)
            while a < len(BUILDINGS):
                alat = float(_buildings[a]["lat"]) - _latSouth
                along = float(_buildings[a]["lng"]) - _longWest
                x = lat_calc * alat
                y = long_calc * along
                CityTransformator.createHouse(x + 50, - (y + 50), a)
                a += 1

        while a_streets < len(_streets):
            street_verts = []

            for street in _streets[a_streets]:
                alat_street = float(street["lat"]) - _latSouth
                along_street = float(street["lng"]) - _longWest
                x_street = lat_calc * alat_street
                y_street = long_calc * along_street
                street_verts.append((x_street + 50, - (y_street + 50), 0))

            CityTransformator.createStreet(street_verts, _mapLength + 100, _mapWidth + 100, a_streets)
            
            a_streets += 1

        CityTransformator.createForest(_mapLength + 100, _mapWidth + 100)

def main():
    global LAT_SOUTH, LAT_NORTH, LON_WEST, LON_EAST, BUILDINGS, FORESTS, STREETS
    handler = BuildingListHandler()
    LAT_SOUTH = handler.map_bounds["minlat"]
    LAT_NORTH = handler.map_bounds["maxlat"]
    LON_WEST = handler.map_bounds["minlon"]
    LON_EAST = handler.map_bounds["maxlon"]

    handler.apply_file(OSM_PATH)

    BUILDINGS = handler.buildings
    FORESTS = handler.forests
    STREETS = handler.streets

    bpy.ops.object.select_all(action='SELECT') # selektiert alle Objekte
    bpy.ops.object.delete(use_global=False, confirm=False) # löscht selektierte objekte
    bpy.ops.outliner.orphans_purge() # löscht überbleibende Meshdaten etc.
    for col in bpy.data.collections:
        bpy.data.collections.remove(col)

class StartCityTransformator(bpy.types.Operator):
    bl_idname = "city.transform"
    bl_label = "City Transform Operator"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        main()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(StartCityTransformator)
    bpy.utils.register_class(PanelProps)
    bpy.utils.register_class(TRANSFORMATOR_PT_panel)
    bpy.utils.register_class(executeAction)
    bpy.types.Scene.prop_data = bpy.props.PointerProperty(type=PanelProps)

def unregister():
    bpy.utils.unregister_class(StartCityTransformator)
    bpy.utils.unregister_class(PanelProps)
    bpy.utils.unregister_class(TRANSFORMATOR_PT_panel)
    bpy.utils.unregister_class(executeAction)
    del bpy.types.Scene.prop_data


if __name__ == '__main__':
    register()
