import osmium as o
import sys
import shapely.wkb as wkblib

import bpy
import typing
import math

wkbfab = o.geom.WKBFactory()

class BuildingListHandler(o.SimpleHandler):

    buildings = []

    buildings_count = 0

    def area(self, a):
        if 'building' in a.tags:
            wkb = wkbfab.create_multipolygon(a)
            poly = wkblib.loads(wkb, hex=True)
            centroid = poly.representative_point()
            # self.print_building(a.tags, centroid.x, centroid.y)
            self.buildings.append({"lat": centroid.y, "lng": centroid.x})
            self.buildings_count += 1

    def print_building(self, tags, lon, lat):
        name = tags.get('name', '')
        print("%f %f %-15s %s" % (lon, lat, tags['building'], name))

class tower():
    tower_radius: float = 2
    tower_height: float = 5
    roof_height: float = 1.5
    roof_overhang: float = 0.5

    wall_thickness: float = 0.5

    PI2 = math.pi * 2

    def create_roof_material(self) -> bpy.types.Material:
        mat_roof: bpy.types.Material = bpy.data.materials.new("Roof Material")
        mat_roof.use_nodes = True
        nodes_roof: typing.List[bpy.types.Node] = mat_roof.node_tree.nodes
        nodes_roof["Principled BSDF"].inputs[0].default_value = [0.1, 0, 0, 1.000000]

        return mat_roof

    def create_tower_material(self) -> bpy.types.Material:
        mat_tower: bpy.types.Material = bpy.data.materials.new("Tower Material")

        mat_tower.use_nodes = True

        nodes_tower: typing.List[bpy.types.Node] = mat_tower.node_tree.nodes
        node_bricks: bpy.types.Node = nodes_tower.new("ShaderNodeTexBrick")
        node_coords: bpy.types.Node = nodes_tower.new("ShaderNodeTexCoord")

        node_bricks.inputs[1].default_value = (0.1,0.1,0.1,0.1)
        node_bricks.inputs[4].default_value = 10
        
        mat_tower.node_tree.links.new(node_bricks.outputs[0], nodes_tower["Principled BSDF"].inputs[0])
        mat_tower.node_tree.links.new(node_coords.outputs[2], node_bricks.inputs[0])
        
        return mat_tower

    def generate_tower(self, lat, lng):
        bpy.ops.mesh.primitive_cylinder_add(
            location=(lat, lng, self.tower_height / 2), 
            depth=self.tower_height, 
            radius=self.tower_radius)
        
        tower_base = bpy.context.object
        
        bpy.context.object.data.materials.append(self.create_tower_material())

        bpy.ops.mesh.primitive_cone_add(
            depth=self.roof_height,
            location=(lat, lng, self.tower_height + self.roof_height / 2),
            radius1=self.tower_radius + self.roof_overhang
            )

        bpy.context.object.data.materials.append(self.create_roof_material())

        modifier_solidify = tower_base.modifiers.new("Wall Thickness", "SOLIDIFY")
        modifier_solidify.thickness = self.wall_thickness


def map(maplength, mapwidth, lat_south, lat_north, long_west, long_east, list):
    t = tower()
    lat_calc = (maplength) / (lat_north - lat_south)
    print(lat_calc)
    long_calc = (mapwidth) / -((long_west - long_east))
    print(long_calc)
    a = 0
    while a < len(list):
        alat = float(list[a]["lat"])-lat_south
        along = float(list[a]["lng"]) - long_west
        x = lat_calc * alat
        y = long_calc * along
        # bpy.ops.mesh.primitive_uv_sphere_add(size=0.02, location=(x,y,z))
        t.generate_tower(x, -y)
        a += 1


def main(osmfile):
    ml = 150
    lats = 48.0489500
    latn = 48.0520900
    mw = 300
    lonw = 7.7151600
    lone = 7.7235800

    handler = BuildingListHandler()

    handler.apply_file(osmfile)

    print(handler.buildings_count)

    buildings = handler.buildings

    bpy.ops.object.select_all(action='SELECT') # selektiert alle Objekte
    bpy.ops.object.delete(use_global=False, confirm=False) # löscht selektierte objekte
    bpy.ops.outliner.orphans_purge() # löscht überbleibende Meshdaten etc.

    # bpy.ops.import_scene.obj( filepath = "D:/Dateien/Uni/Unterricht/5. Semester/DaVinMedPro/Code/DatenverarbeitungSoSe22/Assets/Haus_one.obj" )
    
    map(ml, mw, lats, latn, lonw, lone, buildings)

if __name__ == '__main__':
    main("D:/Dateien/Uni/Unterricht/5. Semester/DaVinMedPro/Code/DatenverarbeitungSoSe22/Assets/gottenheim.osm")