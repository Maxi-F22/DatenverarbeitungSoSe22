import osmium as o
import sys
import shapely.wkb as wkblib

import bpy
import typing
import math

wkbfab = o.geom.WKBFactory()

class BuildingListHandler(o.SimpleHandler):

    buildings = []

    def area(self, a):
        if 'building' in a.tags:
            wkb = wkbfab.create_multipolygon(a)
            poly = wkblib.loads(wkb, hex=True)
            centroid = poly.representative_point()
            # self.print_building(a.tags, centroid.x, centroid.y)
            self.buildings.append({"lat": centroid.y, "lng": centroid.x})

    def print_building(self, tags, lon, lat):
        name = tags.get('name', '')
        print("%f %f %-15s %s" % (lon, lat, tags['building'], name))

class tower():
    tower_radius: float = 3
    tower_height: float = 8
    roof_height: float = 2.5
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




def main(osmfile):

    handler = BuildingListHandler()

    handler.apply_file(osmfile)

    buildings = handler.buildings

    bpy.ops.object.select_all(action='SELECT') # selektiert alle Objekte
    bpy.ops.object.delete(use_global=False, confirm=False) # löscht selektierte objekte
    bpy.ops.outliner.orphans_purge() # löscht überbleibende Meshdaten etc.

    t = tower()

    for index, building in enumerate(buildings):
        if (index < 1):
            latitude = building["lat"]
            longitude = building["lng"]

            latitude_merc = o.geom.lonlat_to_mercator(o.geom.Coordinates(latitude, longitude)).x
            longitude_merc = o.geom.lonlat_to_mercator(o.geom.Coordinates(latitude, longitude)).y

            print(latitude_merc)
            print(longitude_merc)
            #t.generate_tower(latitude, longitude)

if __name__ == '__main__':
    # main("./Assets/furtwangen.osm")
    main("C:/Users/maxif/Downloads/furtwangen.osm")