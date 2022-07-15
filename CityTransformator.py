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

# Path to the Assets
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

    # create the options panel
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

    # set the options variables and build the city
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

    # get osm data, filtered by tags
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
    # start the city transform
    def start(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False, confirm=False)
        bpy.ops.outliner.orphans_purge()
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
                object_name = 'WindowDownOne'
    
                bpy.ops.wm.append(
                    filepath=os.path.join(file_path, inner_path, object_name),
                    directory=os.path.join(file_path, inner_path),
                    filename=object_name
                )
                #rename the object 
                obj = bpy.data.objects['downOne']
                obj.name = 'downOne' + str(_iteration)
                obj_windows = bpy.data.objects['WindowDownOne']
                obj_windows.name = 'WindowDownOne' + str(_iteration)

                #set the right window material for the choosen Time
                CityTransformator.checkDayAndNight(obj_windows)
                #add random rotation and the right position. 
                obj.rotation_euler[2] = radians(SELECT_ROT)
                obj.location[0] = _coordX
                obj.location[1] = _coordY
                for coll in obj_windows.users_collection:
                    # Unlink the object
                    coll.objects.unlink(obj_windows)
                collection.objects.link(obj_windows)
                for coll in obj.users_collection:
                    # Unlink the object
                    coll.objects.unlink(obj)
                collection.objects.link(obj)      
            case 2:
                file_path = ASSETS_PATH
                inner_path = 'Object'
                object_name = 'WindowDownTwo'
    
                bpy.ops.wm.append(
                    filepath=os.path.join(file_path, inner_path, object_name),
                    directory=os.path.join(file_path, inner_path),
                    filename=object_name
                )
                obj = bpy.data.objects['downTwo']
                obj.name = 'downTwo' + str(_iteration)
                obj_windows = bpy.data.objects['WindowDownTwo']
                obj_windows.name = 'WindowDownTwo' + str(_iteration)

                CityTransformator.checkDayAndNight(obj_windows)
                obj.rotation_euler[2] = radians(SELECT_ROT)
                obj.location[0] = _coordX
                obj.location[1] = _coordY
                for coll in obj_windows.users_collection:
                    # Unlink the object
                    coll.objects.unlink(obj_windows)
                collection.objects.link(obj_windows)
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
                object_name = 'WindowMid'
    
                bpy.ops.wm.append(
                    filepath=os.path.join(file_path, inner_path, object_name),
                    directory=os.path.join(file_path, inner_path),
                    filename=object_name
                )
                obj = bpy.data.objects['mid']
                obj.name = 'mid' + str(_iteration)
                obj_windows = bpy.data.objects['WindowMid']
                obj_windows.name = 'WindowMid' + str(_iteration)

                CityTransformator.checkDayAndNight(obj_windows)
                obj.rotation_euler[2] = radians(SELECT_ROT)
                obj.location[0] = _coordX
                obj.location[1] = _coordY
                for coll in obj_windows.users_collection:
                    # Unlink the object
                    coll.objects.unlink(obj_windows)
                collection.objects.link(obj_windows)
                for coll in obj.users_collection:
                    # Unlink the object
                    coll.objects.unlink(obj)
                collection.objects.link(obj)
            case 2:
                file_path = ASSETS_PATH
                inner_path = 'Object'
                object_name = 'WindowMidBalk'
    
                bpy.ops.wm.append(
                    filepath=os.path.join(file_path, inner_path, object_name),
                    directory=os.path.join(file_path, inner_path),
                    filename=object_name
                )
                obj = bpy.data.objects['midbalk']
                obj.name = 'midbalk' + str(_iteration)
                obj_windows = bpy.data.objects['WindowMidBalk']
                obj_windows.name = 'WindowMidBalk' + str(_iteration)

                CityTransformator.checkDayAndNight(obj_windows)
                obj.rotation_euler[2] = radians(SELECT_ROT)
                obj.location[0] = _coordX
                obj.location[1] = _coordY
                for coll in obj_windows.users_collection:
                    # Unlink the object
                    coll.objects.unlink(obj_windows)
                collection.objects.link(obj_windows)
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
        # create cube for cutting of the forest mesh outside of bounds
        bpy.ops.mesh.primitive_cube_add(size=1, location=(_length / 2, -(_width / 2), 45), scale=(_length - 10, _width - 10, 100))
        obj = bpy.data.objects['Cube']
        obj.name = "BoundingBox"
        cube_obj = bpy.data.objects['BoundingBox']
        file_path = ASSETS_PATH
        inner_path = 'Object'
        # add the tree assets
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
            # join all forest meshes into one
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
                # add particle modifier
                forest_obj = bpy.data.objects["forest0"]
                forest_obj.modifiers.new("forestTreeOneParticles", type='PARTICLE_SYSTEM')
                forest_obj.modifiers.new("forestTreeTwoParticles", type='PARTICLE_SYSTEM')
                forest_obj.modifiers.new("forestTreeThreeParticles", type='PARTICLE_SYSTEM')
                forest_obj.show_instancer_for_render = False
                forest_obj.show_instancer_for_viewport = False

                for i in range(3):
                    part_tree = forest_obj.particle_systems[i]
                    part_tree.seed = random.randrange(1,101)
                    settings_tree = part_tree.settings
                    settings_tree.particle_size = 0.3
                    settings_tree.size_random = 0.1
                    settings_tree.count = PROP_NUMBER_TREES
                    settings_tree.type = 'HAIR'
                    settings_tree.render_type = 'OBJECT'
                    settings_tree.use_rotations = True
                    settings_tree.rotation_mode = 'OB_Z'
                    settings_tree.phase_factor_random = 2
                    settings_tree.distribution = 'RAND'
                    if i == 0:
                        settings_tree.instance_object = bpy.data.objects["TreeOne"]
                    elif i == 1:
                        settings_tree.instance_object = bpy.data.objects["TreeTwo"]
                    elif i == 2:
                        settings_tree.instance_object = bpy.data.objects["TreeThree"]
                
                # add boolean modifier and apply to cut of forests out of bounds
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
        # add plane that everything sits on
        bpy.ops.mesh.primitive_plane_add(size=1)
        obj_floorplane = bpy.data.objects['Plane']
        obj_floorplane.name = "FloorPlane"
        obj_floorplane.scale = (_length, _width, 1)
        obj_floorplane.location = (_length / 2, - (_width / 2), 0)

        # add cube below the floor
        bpy.ops.mesh.primitive_cube_add(size=1, location=(_length / 2, -(_width / 2), -2.5), scale=(_length, _width, 5))
        obj = bpy.data.objects['Cube']
        obj.name = "Floor"

        # add materials
        mat_floor = bpy.data.materials.new("Floor Material")
        mat_floor.use_nodes = True
        nodes_floor = mat_floor.node_tree.nodes
        nodes_floor["Principled BSDF"].inputs[0].default_value = [0.01498, 0.238117, 0.015376, 1]
        mat_ground = bpy.data.materials.new("Ground Material")
        mat_ground.use_nodes = True
        nodes_ground = mat_ground.node_tree.nodes
        nodes_ground["Principled BSDF"].inputs[0].default_value = [0.096283, 0.051237, 0.001711, 1]

        obj_floorplane.data.materials.append(mat_floor)
        obj.data.materials.append(mat_ground)

        # add grass and set particle modifier on plane
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
        obj_floorplane.modifiers.new("grassShrubParticles", type='PARTICLE_SYSTEM')

        part_grass = obj_floorplane.particle_systems[0]
        part_grass.seed = random.randrange(1,101)
        settings_grass = part_grass.settings
        settings_grass.particle_size = 2
        settings_grass.size_random = 0.2
        settings_grass.count = PROP_NUMBER_GRASS
        settings_grass.type = 'HAIR'
        settings_grass.render_type = 'OBJECT'
        settings_grass.use_rotations = True
        settings_grass.rotation_mode = 'OB_Z'
        settings_grass.phase_factor_random = 2

        settings_grass.instance_object = objGrass

    def createStreet(_verts, _width, _height, _iteration):
        # create curve from coords
        curve_data = bpy.data.curves.new('streetCurve' + str(_iteration), type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.resolution_u = 2
        # map coords to spline
        polyline = curve_data.splines.new('POLY')
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
            # add street part
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
            curve_obj = bpy.data.objects.new('street' + str(_iteration), curve_data)
            curve_data.bevel_depth = 0.01

            # add modifiers to align and multiply StreetPart to Street
            obj.modifiers.new('StreetPartArray' + str(_iteration), type='ARRAY')
            obj.modifiers['StreetPartArray' + str(_iteration)].fit_type = 'FIT_CURVE'
            obj.modifiers['StreetPartArray' + str(_iteration)].curve = curve_obj
            obj.modifiers.new('StreetPartCurve' + str(_iteration), type='CURVE')
            obj.modifiers['StreetPartCurve' + str(_iteration)].object = curve_obj

            # attach to collection
            street_collection.objects.link(curve_obj)

            # create vehicles on streets
            bpy.ops.wm.append(
                filepath=os.path.join(ASSETS_PATH, 'Object', 'Wagen'),
                directory=os.path.join(ASSETS_PATH, 'Object'),
                filename='Wagen'
            )
                
            obj_wagon = bpy.data.objects['Wagen']
            obj_wagon.name = 'Wagon' + str(_iteration)
            for coll in obj_wagon.users_collection:
                # Unlink the object
                coll.objects.unlink(obj_wagon)

            street_collection.objects.link(obj_wagon)

            wagon_loc = random.randrange(1, len(polyline.points)-1)
            x,y,z,a = polyline.points[wagon_loc].co
            obj_wagon.location.x = x
            obj_wagon.location.y = y
            obj_wagon.location.z = 0.8
            obj_wagon.rotation_euler[2] = radians(random.randrange(0, 361))


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
        emission_node = mat.node_tree.nodes.new('ShaderNodeEmission')
        emission_node.location = (0,320)

        #Add right values to the shader
        emission_node.inputs[0].default_value = (1.0,0.534,0.029,1.0)
        emission_node.inputs[1].default_value = 4.0
        
        #Conect nodes
        shader_output = mat.node_tree.nodes.get('Material Output')
        mat.node_tree.links.new(emission_node.outputs[0], shader_output.inputs[0] )
        
        #Configure scene settings 
        eevee_obj = bpy.data.scenes['Scene'].eevee
        eevee_obj.use_bloom = True
        eevee_obj.bloom_color = (1.0,0.425,0.006)
        eevee_obj.bloom_intensity = 0.5

    def checkDayAndNight(_objWindows):
        day_night_set = PROP_NIGHTTIME
        #Check if user set checkbox for the day or night time
        if(day_night_set==False):
            #set window material 
            mat = bpy.data.materials.get('Fenster')
            _objWindows.data.materials.append(mat)
            
            #change the color of the sun to night
            sonne = bpy.data.lights.get('Sonne')
            sonne.color = (1,0.828,0.676)

            #change world background-color
            bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.163,0.135,0.110,1)
            
        elif(day_night_set==True):
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
        set_epoxy = PROP_EPOXY
        if(set_epoxy==False):
            print("Epoxy Version wurde nicht ausgewählt. Das Modell wird ohne Epoxy-Erweiterung erstellt.")
        elif(set_epoxy==True):
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
            mixed_node = mat.node_tree.nodes.new('ShaderNodeMixShader')
            mixed_node.location = (800,-300)
            shader_output = mat.node_tree.nodes.get('Material Output')
            shader_output.location = (1000,0)
            mat.node_tree.links.new(mixed_node.outputs[0], shader_output.inputs[0] )

            #connect Principled BSDF with Mix Shader
            mat.node_tree.links.new(bsdf.outputs[0], mixed_node.inputs[2] )

            #add Transparent BSDF & connect with Mix Shader
            transparent_node = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
            transparent_node.location = (0,100)
            mat.node_tree.links.new(transparent_node.outputs[0], mixed_node.inputs[1] )

            #add Frensel
            fresnel_node = mat.node_tree.nodes.new('ShaderNodeFresnel')
            fresnel_node.location = (0,230)

            #add Color Ramp
            colorramp_node = mat.node_tree.nodes.new('ShaderNodeValToRGB') 
            colorramp_node.location = (200,300)

            # conect Frensel with Color Ramp & Color Ramp with Mix Shader
            mat.node_tree.links.new(fresnel_node.outputs[0], colorramp_node.inputs[0] )
            mat.node_tree.links.new(colorramp_node.outputs[0], mixed_node.inputs[0] )

            #set diffrent settings 
            mat.use_screen_refraction = True
            mat.blend_method = ("HASHED")
            mat.shadow_method = ("HASHED")
            bpy.data.scenes["Scene"].eevee.use_ssr = True
            bpy.data.scenes["Scene"].eevee.use_ssr_refraction = True
            
            #add cube and apply epoxy material 
            bpy.ops.mesh.primitive_cube_add(size=1)
            obj_cube = bpy.data.objects['Cube']
            obj_cube.name = "GlasCube"
            obj_cube.data.materials.append(mat)

            #move and sccale the cube to the right size
            obj_cube.location = (_length / 2, - (_width / 2), 40)
            obj_cube.scale[0] = _length
            obj_cube.scale[1] = _width
            obj_cube.scale[2] = 90

        
    def createMap(_mapLength, _mapWidth, _latSouth, _latNorth, _longWest, _longEast, _buildings, _forests, _streets):
        # calculate blender coords
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

        # create forests, buildings and streets based on calculated coords
        while a_forest < len(_forests):
            forest_verts = []
            for forest_border in _forests[a_forest]["coords"]:
                alat_forest = float(forest_border["lat"]) - _latSouth
                along_forest = float(forest_border["lng"]) - _longWest
                x_forest = lat_calc * alat_forest
                y_forest = long_calc * along_forest
                forest_verts.append((x_forest + 50, - (y_forest + 50), 0))

            # create new meshes based on outer bounds coords of forest
            faces = [[i for i in range(len(forest_verts)-1)]]

            mesh = bpy.data.meshes.new("forest" + str(a_forest))
            mesh.from_pydata(vertices=forest_verts, edges=[], faces=faces)
            mesh.update()

            obj = bpy.data.objects.new("forest" + str(a_forest), mesh)
            forest_collection.objects.link(obj)

            a_forest += 1

        # if the user has selected a value for house count that is greater than the number of houses, set house count to that value and create all available houses
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
    # read the osm data and set the variables
    global LAT_SOUTH, LAT_NORTH, LON_WEST, LON_EAST, BUILDINGS, FORESTS, STREETS
    handler = BuildingListHandler()

    handler.apply_file(OSM_PATH)

    LAT_SOUTH = handler.map_bounds["minlat"]
    LAT_NORTH = handler.map_bounds["maxlat"]
    LON_WEST = handler.map_bounds["minlon"]
    LON_EAST = handler.map_bounds["maxlon"]

    BUILDINGS = handler.buildings
    FORESTS = handler.forests
    STREETS = handler.streets

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    bpy.ops.outliner.orphans_purge()
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
