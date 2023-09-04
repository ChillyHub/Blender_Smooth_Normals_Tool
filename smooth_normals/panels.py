import bpy
from bpy.types import Context

class SmoothNormalsPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_smooth_normals'
    bl_label = 'Smooth Normals Tool'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Smooth Normals'

    def draw(self, context: Context):
        layout = self.layout
        layout.operator('smooth_normals.smooth_normals_operator')
    