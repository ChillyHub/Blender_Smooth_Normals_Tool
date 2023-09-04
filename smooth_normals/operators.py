import bpy
from bpy.types import Context
from typing import *

from mathutils import *
import math

class SmoothNormalsOperator(bpy.types.Operator):
    bl_idname = 'smooth_normals.smooth_normals_operator'
    bl_label = 'Smooth Normals'

    def execute(self, context: Context) -> Set[str] | Set[int]:
        objects = context.selected_objects

        for object in objects:
            Utils.do_smooth_normals(object.data)
        
        return {'FINISHED'}
    
    
class VertexNormals:
    index : int = None
    normal : Vector = None
    weight : float = None

    def __init__(self, index : int, normal : Vector, weight : float) -> None:
        self.index = index
        self.normal = normal
        self.weight = weight
    
class Utils:
    @staticmethod
    def do_smooth_normals(mesh : bpy.types.Mesh) -> None:
        if (mesh):
            mesh.calc_normals_split()
            mesh.calc_tangents()

            vertices_group : Dict[Tuple, List[VertexNormals]] = {}
            pack_normals : List[Vector] = [None] * len(mesh.loops)
            smooth_mormals : List[Vector] = [None] * len(mesh.loops)

            vertex_normals : List[Vector] = [None] * len(mesh.loops)
            vertex_tangents : List[Vector] = [None] * len(mesh.loops)
            vertex_bitangents : List[Vector] = [None] * len(mesh.loops)

            # Iterate polygons and group by vertices position
            for poly in mesh.polygons:
                # Calc vertex weight (by angle)
                indices = []
                positions = []
                normals = []
                weights = []
                for index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                    m_vertex_index = mesh.loops[index].vertex_index
                    l_vertex_index = mesh.loops[Utils.left_index(index, poly.loop_start, poly.loop_total)].vertex_index
                    r_vertex_index = mesh.loops[Utils.right_index(index, poly.loop_start, poly.loop_total)].vertex_index

                    m_position = mesh.vertices[m_vertex_index].co.copy()
                    l_position = mesh.vertices[l_vertex_index].co
                    r_position = mesh.vertices[r_vertex_index].co

                    m_position.freeze()

                    v1 = l_position - m_position
                    v2 = r_position - m_position

                    normal = mesh.loops[index].normal
                    tangent = mesh.loops[index].tangent
                    bitangent = mesh.loops[index].bitangent
                    angle = Utils.calc_angle(v1, v2)

                    indices.append(index)
                    positions.append(m_position)
                    normals.append(normal)
                    weights.append(angle)

                    vertex_normals[index] = normal
                    vertex_tangents[index] = tangent
                    vertex_bitangents[index] = bitangent

                # Group
                for i in range(len(positions)):
                    if positions[i] not in vertices_group:
                        vertices_group[positions[i]] = []
                    tmp = VertexNormals(indices[i], normals[i], weights[i])
                    vertices_group[positions[i]].append(tmp)

            # Calculate smooth normals
            for key, value in vertices_group.items():
                smooth_mormal = Vector()
                smooth_weight_total = 0.0
                for v in value:
                    smooth_weight_total += v.weight

                smooth_weight_total = 1.0 / smooth_weight_total

                for v in value:
                    smooth_mormal += v.normal * v.weight * smooth_weight_total

                Vector.normalize(smooth_mormal)
                for v in value:
                    smooth_mormals[v.index] = smooth_mormal

            # Turn smooth normals from Object to Tangent space
            for index in range(0, len(mesh.loops)):
                normal_OS = vertex_normals[index].copy()
                tangent_OS = vertex_tangents[index].copy()
                bitangent_OS = vertex_bitangents[index].copy()
                normal_OS.resize_4d()
                tangent_OS.resize_4d()
                bitangent_OS.resize_4d()
                # tangent_OS.w = 0.0

                tbn = Matrix.Identity(4)
                tbn[0] = Vector.normalized(tangent_OS)
                tbn[1] = Vector.normalized(bitangent_OS)
                tbn[2] = Vector.normalized(normal_OS)

                smooth_normal_TS = tbn @ smooth_mormals[index]
                pack_normals[index] = Utils.pack_normal_oct_quad_encode(smooth_normal_TS.normalized())


            # Write pack normals in uv
            Utils.write_pack_normals_to_uv2(mesh, pack_normals)

    @staticmethod
    def write_pack_normals_to_uv2(mesh : bpy.types.Mesh, pack_normals):
        origin_uv_layer = mesh.uv_layers.active
        uv_index = mesh.uv_layers.find('UV2')
        if uv_index == -1:
            mesh.uv_layers.new(name='UV2', do_init=False)
            uv_index = mesh.uv_layers.find('UV2')

        mesh.uv_layers.active = mesh.uv_layers[uv_index]
        uvs = mesh.uv_layers.active.data
        for i in range(len(uvs)):
            uvs[i].uv = pack_normals[i]
        mesh.uv_layers.active = origin_uv_layer

    @staticmethod
    def pack_normal_oct_quad_encode(n : Vector):
        n_dot_1 = abs(n.x) + abs(n.y) + abs(n.z)
        n /= max(n_dot_1, 1e-6)
        tx = Utils.clamp01(-n.z)
        t = Vector((tx, tx))
        res = Vector((n.x, n.y))
        return res + (t if res.x >= 0 and res.y >= 0.0 else -t)

    @staticmethod
    def clamp01(n):
        return 0 if n < 0 else (1 if n > 1 else n)

    @staticmethod
    def left_index(index, start, total):
        return index if index > start else start + total - 1

    @staticmethod
    def right_index(index, start, total):
        return index if index < start + total - 1 else start

    @staticmethod
    def calc_angle(v1 : Vector, v2 : Vector):
        v1.normalize()
        v2.normalize()
        return math.acos(Vector.dot(v1, v2))

