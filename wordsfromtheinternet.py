bl_info = {
    "name": "Title from URL",
    "blender": (2, 93, 0),
    "category": "Object",
}

import bpy
import requests
from bs4 import BeautifulSoup


class TEXT_OT_title_from_url(bpy.types.Operator):
    bl_idname = "object.title_from_url"
    bl_label = "Title from URL"
    bl_options = {'REGISTER', 'UNDO'}

    url: bpy.props.StringProperty(
        name="URL",
        description="Enter the URL of the website",
        default="",
    )

    def execute(self, context):
        
        # Retrieve the HTML content of the website
        response = requests.get(self.url)
        html_content = response.content
            
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
            
        # Extract the title of the website from the HTML if it exists
        if soup.title is not None:
            title = soup.title.string
            
            # Create a new Blender scene
            bpy.ops.scene.new(type='NEW')
            
            # Create a text object
            bpy.ops.object.text_add()
            obj = bpy.context.object
            
            # Set the text of the object to the website title
            obj.data.body = title
            
            # Add thickness to the text object by adjusting the extrude property
            obj.data.extrude = 0.2
            
            # Rotate the text object around the X-axis by 90 degrees (1.5708 radians)
            obj.rotation_euler[0] = 1.5708
            
            # Add some bevel and extrusion to give the text some depth
            bpy.ops.object.modifier_add(type='BEVEL')
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            
            # Convert the text object to a mesh
            bpy.ops.object.convert(target='MESH')
    
            # Add a displace modifier
            bpy.ops.object.modifier_add(type='DISPLACE')
            displace_modifier = obj.modifiers['Displace']
            displace_modifier.direction = 'NORMAL'
            displace_modifier.strength = 0
            displace_modifier.mid_level = 0.5
            
            # Create a texture for the displace modifier
            displace_texture = bpy.data.textures.new(name="DisplaceTexture", type='CLOUDS')
            displace_texture.noise_scale = 0.5
            displace_modifier.texture = displace_texture
            
            # Add keyframes for the strength property
            obj.keyframe_insert(data_path="modifiers[\"Displace\"].strength", frame=1)
            obj.modifiers['Displace'].strength = 1.0
            obj.keyframe_insert(data_path="modifiers[\"Displace\"].strength", frame=50)
            obj.modifiers['Displace'].strength = 0.0
            obj.keyframe_insert(data_path="modifiers[\"Displace\"].strength", frame=100)

            
            return {'FINISHED'}
            
        else:
            self.report({'ERROR'}, "Website does not have a title tag")
            return {'CANCELLED'}
    

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class TEXT_PT_title_from_url(bpy.types.Panel):
    bl_label = "Title from URL"
    bl_idname = "TEXT_PT_title_from_url"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.title_from_url")


def menu_func(self, context):
    self.layout.operator(TEXT_OT_title_from_url.bl_idname)


def register():
    bpy.utils.register_class(TEXT_OT_title_from_url)
    bpy.utils.register_class(TEXT_PT_title_from_url)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_class(TEXT_OT_title_from_url)
    bpy.utils.unregister_class(TEXT_PT_title_from_url)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()
