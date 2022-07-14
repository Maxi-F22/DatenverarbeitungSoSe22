import bpy
from math import radians
import bmesh

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


def createEpoxyMap():
    setEpoxy = False
    if(setEpoxy==False):
        print("Epoxy version wurde nicht ausgewähl. Das Modell wird ohne Epoxy-Erweiterung erstellt.")
    elif(setEpoxy==True):
        print("Das Model wurde in ein Epoxy-Modell wurde in ein Epoxy-Harz modell umgewandelt.")
        #extrude ground 
        #all faces 
        
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
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.selected_objects[0]
        cube.name = "GlasCube"
        cubeMat = bpy.data.objects["GlasCube"]
        cubeMat.data.materials.append(mat)

        #move and sccale the cube to the right size
        cubeMat.location = (200, -400, 0)
        cubeMat.scale[0] = 200
        cubeMat.scale[1] = 400
        cubeMat.scale[2] = 81


        
        
    
   
