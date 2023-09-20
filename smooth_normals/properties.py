import sys
import bpy

class SmoothNormalPropertyies(bpy.types.PropertyGroup):
    write_channel: bpy.props.EnumProperty(
        name = 'Write Channel',
        items = {
            ('0', 'UV2', ''),
            ('1', 'Tangent', '')
        }
    )