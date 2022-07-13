import bpy
from math import radians

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

    #change location and rotation
    sonne.location = (-39, -284, 40)
    sonne.rotation_euler[0]= radians(-19)
    sonne.rotation_euler[1]= radians(-43)
    sonne.rotation_euler[2]= radians(8)

def checkDayAndNight(objWindows):
    dayNightSet = False
    if(dayNightSet==False):
        #set window material 
        mat = bpy.data.materials.get('Fenster')
        objWindows.data.materials.append(mat)
        
        #change the color of the sun to night
        sonne = bpy.data.lights.get('Sonne')
        sonne.color = (0.124,0.097,1.0)

        #change world background-color
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.078,0.324,0.163,1)

    elif(dayNightSet==True):
        #set window material 
        mat = bpy.data.materials.get('Licht_Fenster')
        objWindows.data.materials.append(mat)

        #change the color of the sun to night
        sonne = bpy.data.lights.get('Sonne')
        sonne.color = (0.653,0.642,0.298)

        #change world background-color
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0,0,0,1)

         


    
   
