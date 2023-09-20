import sys
import bpy
from bpy.types import Context
from smooth_normals.properties import *

class SmoothNormalsPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_smooth_normals'
    bl_label = 'Smooth Normals Tool'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Smooth Normals'

    def draw(self, context: Context):
        layout = self.layout
        scene = context.scene

        properties : SmoothNormalPropertyies = scene.smoothNormalPropertyies
        layout.prop(properties, 'write_channel')
        layout.operator('smooth_normals.smooth_normals_operator')
    