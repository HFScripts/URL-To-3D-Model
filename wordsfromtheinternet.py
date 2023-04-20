bl_info = {
    "name": "Title from URL",
    "blender": (2, 93, 0),
    "category": "Object",
}

import bpy
import requests
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
from collections import Counter
import itertools
import math
import re
from urllib.parse import urlparse, urlunparse

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
        # Define a function to calculate the Euclidean distance between two colors
        def color_distance(color1, color2):
            r1, g1, b1 = color1
            r2, g2, b2 = color2
            return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)
    
        # Get the website URL from user input
        url = self.url
    
        # Your provided code to get the most_common_colors
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    
        favicon_url = None
        for tag in soup.find_all('link'):
            if 'icon' in tag.get('rel') or 'shortcut icon' in tag.get('rel'):
                favicon_url = tag.get('href')
                break
    
        if not favicon_url:
            favicon_url = url.rstrip('/') + '/favicon.ico'
    
        try:
            favicon_response = requests.get(favicon_url)
            favicon_data = BytesIO(favicon_response.content)
            favicon_image = Image.open(favicon_data)
    
        except requests.exceptions.RequestException:
            parsed_url = urlparse(url)
            path = favicon_url
            if path.startswith('/'):
                path = path[1:]
            new_favicon_url = urlunparse((parsed_url.scheme, parsed_url.netloc, path, '', '', ''))
            try:
                favicon_response = requests.get(new_favicon_url)
                favicon_data = BytesIO(favicon_response.content)
                favicon_image = Image.open(favicon_data)
                favicon_url = new_favicon_url
            except requests.exceptions.RequestException:
                self.report({'ERROR'}, "Could not retrieve the favicon from " + favicon_url)
                return {'CANCELLED'}
    
        colors = favicon_image.getdata()
        colors = [(color[0], color[1], color[2]) for color in colors]
        unique_colors = list(set(colors))
    
        color_counts = Counter(colors)
    
        close_color_pairs = set()
        for color1, color2 in itertools.combinations(unique_colors, 2):
            if color_distance(color1, color2) < 50:
                close_color_pairs.add(frozenset([color1, color2]))
    
        most_common_colors = []
        for color, count in color_counts.most_common():
            if not any(frozenset([color, common_color]) in close_color_pairs for common_color in most_common_colors):
                most_common_colors.append(color)
                if len(most_common_colors) == 3:
                    break
    
        # Retrieve the HTML content of the website
        response = requests.get(self.url)
        html_content = response.content
    
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
    
        # Extract the title of the website from the HTML if it exists
        if soup.title is not None:
            title = soup.title.string
    
            # Split the title into words
            words = re.findall(r'\w+', title)
    
            # Create a new Blender scene
            bpy.ops.scene.new(type='NEW')
    
            for i, word in enumerate(words):
                # Create a text object for each word
                bpy.ops.object.text_add()
                obj = bpy.context.object
            
                # Set the location of the object along the X-axis to add space between words
                obj.location.x = 4 * i # Adjust the multiplier (2.5 here) to increase or decrease the spacing between words
            
                # Set the text of the object to the current word
                obj.data.body = word            
                # Apply color from most_common_colors to every second word
                if i % 2 == 1 and most_common_colors:
                    color_index = (i // 2) % len(most_common_colors)
                    color = [c / 255 for c in most_common_colors[color_index]]
                    material = bpy.data.materials.new(name="WordColor")
                    material.use_nodes = False
                    material.diffuse_color = color + [1]
                    obj.data.materials.append(material)
            
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
