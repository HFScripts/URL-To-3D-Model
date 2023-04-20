bl_info = {
    "name": "Text from URL",
    "blender": (2, 93, 0),
    "category": "Object",
}

import bpy
import requests
from bs4 import BeautifulSoup
import random


class TEXT_OT_text_from_url(bpy.types.Operator):
    bl_idname = "object.text_from_url"
    bl_label = "Text from URL"
    bl_options = {'REGISTER', 'UNDO'}

    url: bpy.props.StringProperty(
        name="URL",
        description="Enter the URL of the text",
        default="",
    )

    def execute(self, context):

        # Retrieve the HTML content of the website
        response = requests.get(self.url)
        html_content = response.content
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract the text from the HTML
        text = soup.get_text()
        
        # Split the text into individual words
        words = text.split()
        
        # Create a new Blender scene
        bpy.ops.scene.new(type='NEW')
        
        # Create the parent object
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        parent_obj = bpy.context.object
        parent_obj.name = "Word"
        
        # Create a glass material
        glass_material = bpy.data.materials.new(name="Glass")
        glass_material.use_nodes = True
        glass_bsdf = glass_material.node_tree.nodes["Principled BSDF"]
        glass_bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
        glass_bsdf.inputs["Transmission"].default_value = 0.9
        glass_bsdf.inputs["Roughness"].default_value = 0.1
        
        # Create a grass material
        grass_material = bpy.data.materials.new(name="Grass")
        grass_material.use_nodes = True
        grass_bsdf = grass_material.node_tree.nodes["Principled BSDF"]
        grass_bsdf.inputs["Base Color"].default_value = (0.1, 0.6, 0.2, 1)
        grass_bsdf.inputs["Roughness"].default_value = 0.3
        
        # Loop through each word and create a separate 3D text object for each one
        letter_location = 0
        for i, word in enumerate(words):
            for j, letter in enumerate(word):
                # Create a new text object
                bpy.ops.object.text_add(location=(letter_location, 0, 0))
                obj = bpy.context.object
        
                # Set the text of the object to the current letter
                obj.data.body = letter
        
                # Add thickness to the text object by adjusting the extrude property
                obj.data.extrude = 0.2
        
                # Rotate the text object around the X-axis by 90 degrees (1.5708 radians)
                obj.rotation_euler[0] = 1.5708
        
                # Add some bevel and extrusion to give the text some depth
                bpy.ops.object.modifier_add(type='BEVEL')
                bpy.ops.object.modifier_add(type='SOLIDIFY')
        
                # Randomly assign glass or grass material to the text object
                obj.data.materials.clear()
                random_material = random.choice([glass_material, grass_material])
                obj.data.materials.append(random_material)
                
                # Set the parent of the letter object to the 'Word' object
                obj.parent = parent_obj
        
                # Calculate the width of the letter and increment the location
                bpy.context.view_layer.update()  # Make sure the dimensions are updated
                letter_width = obj.dimensions.x
                letter_location += letter_width + 0.1  # Adding 0.1 for some space between letters
            
            # Add space between words
            letter_location += 0.5
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class TEXT_PT_text_from_url(bpy.types.Panel):
    bl_label = "Text from URL"
    bl_idname = "TEXT_PT_text_from_url"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.text_from_url")


def menu_func(self, context):
    self.layout.operator(TEXT_OT_text_from_url.bl_idname)


def register():
    bpy.utils.register_class(TEXT_OT_text_from_url)
    bpy.utils.register_class(TEXT_PT_text_from_url)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_class(TEXT_OT_text_from_url)
    bpy.utils.unregister_class(TEXT_PT_text_from_url)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()
