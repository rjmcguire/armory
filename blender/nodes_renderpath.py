import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import armutils
import make_renderer

class CGPipelineTree(NodeTree):
    '''Render path nodes'''
    bl_idname = 'CGPipelineTreeType'
    bl_label = 'Render Path Node Tree'
    bl_icon = 'SCENE'

class CGPipelineTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CGPipelineTreeType'

# Prebuilt
class QuadPassNode(Node, CGPipelineTreeNode):
    '''Full-screen quad pass node'''
    bl_idname = 'QuadPassNodeType'
    bl_label = 'Quad Pass'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketString', "Shader Context")
        self.inputs.new('NodeSocketShader', "Bind 1")
        self.inputs.new('NodeSocketString', "Constant")
        self.inputs.new('NodeSocketShader', "Bind 2")
        self.inputs.new('NodeSocketString', "Constant")
        self.inputs.new('NodeSocketShader', "Bind 3")
        self.inputs.new('NodeSocketString', "Constant")

        self.outputs.new('NodeSocketShader', "Stage")

class SSAOPassNode(Node, CGPipelineTreeNode):
    '''Screen-space ambient occlusion node'''
    bl_idname = 'SSAOPassNodeType'
    bl_label = 'SSAO'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class SSAOReprojectPassNode(Node, CGPipelineTreeNode):
    '''Screen-space ambient occlusion reprojection node'''
    bl_idname = 'SSAOReprojectPassNodeType'
    bl_label = 'SSAO Reproject'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Last")
        self.inputs.new('NodeSocketShader', "Depth")
        self.inputs.new('NodeSocketShader', "Normals")
        self.inputs.new('NodeSocketShader', "Velocity")

        self.outputs.new('NodeSocketShader', "Stage")

class ApplySSAOPassNode(Node, CGPipelineTreeNode):
    '''Apply screen-space ambient occlusion node'''
    bl_idname = 'ApplySSAOPassNodeType'
    bl_label = 'Apply SSAO'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "B")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class SSRPassNode(Node, CGPipelineTreeNode):
    '''Screen-space reflections node'''
    bl_idname = 'SSRPassNodeType'
    bl_label = 'SSR'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "B")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class BloomPassNode(Node, CGPipelineTreeNode):
    '''Bloom node'''
    bl_idname = 'BloomPassNodeType'
    bl_label = 'Bloom'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "B")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class MotionBlurPassNode(Node, CGPipelineTreeNode):
    '''Motion blur node'''
    bl_idname = 'MotionBlurPassNodeType'
    bl_label = 'Motion Blur'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class MotionBlurVelocityPassNode(Node, CGPipelineTreeNode):
    '''Motion blur using velocity node'''
    bl_idname = 'MotionBlurVelocityPassNodeType'
    bl_label = 'Motion Blur Velocity'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBuffer0")
        self.inputs.new('NodeSocketShader', "Velocity")

        self.outputs.new('NodeSocketShader', "Stage")

class CopyPassNode(Node, CGPipelineTreeNode):
    '''Copy to render target node'''
    bl_idname = 'CopyPassNodeType'
    bl_label = 'Copy'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class BlendPassNode(Node, CGPipelineTreeNode):
    '''Blend to target node'''
    bl_idname = 'BlendPassNodeType'
    bl_label = 'Blend'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class CombinePassNode(Node, CGPipelineTreeNode):
    '''Add two render targets node'''
    bl_idname = 'CombinePassNodeType'
    bl_label = 'Combine'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "B")

        self.outputs.new('NodeSocketShader', "Stage")

class BlurBasicPassNode(Node, CGPipelineTreeNode):
    '''Blur node'''
    bl_idname = 'BlurBasicPassNodeType'
    bl_label = 'Blur Basic'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "In/Out")
        self.inputs.new('NodeSocketShader', "Temp")

        self.outputs.new('NodeSocketShader', "Stage")

class DebugNormalsPassNode(Node, CGPipelineTreeNode):
    '''View normals node'''
    bl_idname = 'DebugNormalsPassNodeType'
    bl_label = 'Debug Normals'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class FXAAPassNode(Node, CGPipelineTreeNode):
    '''FXAA anti-aliasing node'''
    bl_idname = 'FXAAPassNodeType'
    bl_label = 'FXAA'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class SMAAPassNode(Node, CGPipelineTreeNode):
    '''Subpixel morphological anti-aliasing node'''
    bl_idname = 'SMAAPassNodeType'
    bl_label = 'SMAA'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Edges Target")
        self.inputs.new('NodeSocketShader', "Blend Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "Velocity")

        self.outputs.new('NodeSocketShader', "Stage")

class TAAPassNode(Node, CGPipelineTreeNode):
    '''Temporal anti-aliasing node'''
    bl_idname = 'TAAPassNodeType'
    bl_label = 'TAA'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "Last Color")
        self.inputs.new('NodeSocketShader', "Velocity")

        self.outputs.new('NodeSocketShader', "Stage")

class SSSPassNode(Node, CGPipelineTreeNode):
    '''Subsurface scattering node'''
    bl_idname = 'SSSPassNodeType'
    bl_label = 'SSS'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target In")
        self.inputs.new('NodeSocketShader', "Target Out")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class WaterPassNode(Node, CGPipelineTreeNode):
    '''Ocean node'''
    bl_idname = 'WaterPassNodeType'
    bl_label = 'Water'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBufferD")

        self.outputs.new('NodeSocketShader', "Stage")

class DeferredLightPassNode(Node, CGPipelineTreeNode):
    '''Deferred light node'''
    bl_idname = 'DeferredLightPassNodeType'
    bl_label = 'Deferred Light'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "GBuffer")
        self.inputs.new('NodeSocketShader', "Shadow Map")

        self.outputs.new('NodeSocketShader', "Stage")

class DeferredIndirectPassNode(Node, CGPipelineTreeNode):
    '''Deferred indirect lighting node'''
    bl_idname = 'DeferredIndirectPassNodeType'
    bl_label = 'Deferred Indirect'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "GBuffer")
        self.inputs.new('NodeSocketShader', "SSAO")
        # Testing voxels
        # self.inputs.new('NodeSocketShader', "Voxels")

        self.outputs.new('NodeSocketShader', "Stage")

class VolumetricLightPassNode(Node, CGPipelineTreeNode):
    '''Volumetric light node'''
    bl_idname = 'VolumetricLightPassNodeType'
    bl_label = 'Volumetric Light'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "B")
        self.inputs.new('NodeSocketShader', "Normals")
        self.inputs.new('NodeSocketShader', "Depth")
        self.inputs.new('NodeSocketShader', "Shadow Map")

        self.outputs.new('NodeSocketShader', "Stage")

class TranslucentResolvePassNode(Node, CGPipelineTreeNode):
    '''Translucent resolve node'''
    bl_idname = 'TranslucentResolvePassNodeType'
    bl_label = 'Translucent Resolve'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Translucent GBuffer")

        self.outputs.new('NodeSocketShader', "Stage")

# Render path
class DrawMeshesNode(Node, CGPipelineTreeNode):
    '''Draw meshes of specified context node'''
    bl_idname = 'DrawMeshesNodeType'
    bl_label = 'Draw Meshes'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Context")
        self.inputs.new('NodeSocketString', "Order")
        self.inputs[2].default_value = 'front_to_back'

        self.outputs.new('NodeSocketShader', "Stage")
        
class DrawDecalsNode(Node, CGPipelineTreeNode):
    '''Draw decals node'''
    bl_idname = 'DrawDecalsNodeType'
    bl_label = 'Draw Decals'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Context")

        self.outputs.new('NodeSocketShader', "Stage")
        
class ClearTargetNode(Node, CGPipelineTreeNode):
    '''Clear current target node'''
    bl_idname = 'ClearTargetNodeType'
    bl_label = 'Clear Target'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketBool', "Color")
        self.inputs.new('NodeSocketColor', "Value")
        self.inputs.new('NodeSocketBool', "Depth")
        self.inputs.new('NodeSocketFloat', "Value")
        self.inputs[4].default_value = 1.0
        self.inputs.new('NodeSocketBool', "Stencil")
        self.inputs.new('NodeSocketInt', "Value")

        self.outputs.new('NodeSocketShader', "Stage")

class GenerateMipmapsNode(Node, CGPipelineTreeNode):
    '''Generate mipmaps node'''
    bl_idname = 'GenerateMipmapsNodeType'
    bl_label = 'Generate Mipmaps'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")

        self.outputs.new('NodeSocketShader', "Stage")

class BeginNode(Node, CGPipelineTreeNode):
    '''Start render path node'''
    bl_idname = 'BeginNodeType'
    bl_label = 'Begin'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "ID")
        self.inputs.new('NodeSocketBool', "HDR Space")
        self.inputs[1].default_value = True
        self.outputs.new('NodeSocketShader', "Stage")
    
class SetTargetNode(Node, CGPipelineTreeNode):
    '''Set render target node'''
    bl_idname = 'SetTargetNodeType'
    bl_label = 'Set Target'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")

        self.outputs.new('NodeSocketShader', "Stage")

class SetViewportNode(Node, CGPipelineTreeNode):
    '''Set viewport size node'''
    bl_idname = 'SetViewportNodeType'
    bl_label = 'Set Viewport'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketInt', "Width")
        self.inputs.new('NodeSocketInt', "Height")

        self.outputs.new('NodeSocketShader', "Stage")

class TargetNode(Node, CGPipelineTreeNode):
    '''Create new render target node'''
    bl_idname = 'TargetNodeType'
    bl_label = 'Target'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "ID")
        self.inputs.new('NodeSocketInt', "Width")
        self.inputs.new('NodeSocketInt', "Height")
        self.inputs.new('NodeSocketShader', "Depth Buffer")
        self.inputs.new('NodeSocketString', "Format")
        self.inputs.new('NodeSocketBool', "Ping Pong")

        self.outputs.new('NodeSocketShader', "Target")

class ShadowMapNode(Node, CGPipelineTreeNode):
    '''Create new shadow map target node'''
    bl_idname = 'ShadowMapNodeType'
    bl_label = 'Shadow Map'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "ID")
        self.inputs.new('NodeSocketInt', "Width")
        self.inputs.new('NodeSocketInt', "Height")
        self.inputs.new('NodeSocketString', "Format")

        self.outputs.new('NodeSocketShader', "Target")

class ImageNode(Node, CGPipelineTreeNode):
    '''Create new image node'''
    bl_idname = 'ImageNodeType'
    bl_label = 'Image'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "ID")
        self.inputs.new('NodeSocketInt', "Width")
        self.inputs.new('NodeSocketInt', "Height")
        self.inputs.new('NodeSocketString', "Format")

        self.outputs.new('NodeSocketShader', "Target")

class Image3DNode(Node, CGPipelineTreeNode):
    '''Create new 3D image node'''
    bl_idname = 'Image3DNodeType'
    bl_label = 'Image 3D'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "ID")
        self.inputs.new('NodeSocketInt', "Width")
        self.inputs.new('NodeSocketInt', "Height")
        self.inputs.new('NodeSocketInt', "Depth")
        self.inputs.new('NodeSocketString', "Format")

        self.outputs.new('NodeSocketShader', "Target")

class TargetArrayNode(Node, CGPipelineTreeNode):
    '''Create target array node'''
    bl_idname = 'TargetArrayNodeType'
    bl_label = 'Target Array'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketInt', "Instances")

        self.outputs.new('NodeSocketShader', "Targets")

class DepthBufferNode(Node, CGPipelineTreeNode):
    '''Create depth buffer node'''
    bl_idname = 'DepthBufferNodeType'
    bl_label = 'Depth Buffer'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "ID")
        self.inputs.new('NodeSocketBool', "Stencil")
        
        self.outputs.new('NodeSocketShader', "Target")

class GBufferNode(Node, CGPipelineTreeNode):
    '''Create gbuffer node'''
    bl_idname = 'GBufferNodeType'
    bl_label = 'GBuffer'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Target 0")
        self.inputs.new('NodeSocketShader', "Target 1")
        self.inputs.new('NodeSocketShader', "Target 2")
        self.inputs.new('NodeSocketShader', "Target 3")
        self.inputs.new('NodeSocketShader', "Target 4")

        self.outputs.new('NodeSocketShader', "Targets")
    
class FramebufferNode(Node, CGPipelineTreeNode):
    '''Reference framebuffer node'''
    bl_idname = 'FramebufferNodeType'
    bl_label = 'Framebuffer'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "Target")

class BindTargetNode(Node, CGPipelineTreeNode):
    '''Bind render target node'''
    bl_idname = 'BindTargetNodeType'
    bl_label = 'Bind Target'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketString', "Constant")

        self.outputs.new('NodeSocketShader', "Stage")

class DrawMaterialQuadNode(Node, CGPipelineTreeNode):
    '''Draw full-screen quad using material node'''
    bl_idname = 'DrawMaterialQuadNodeType'
    bl_label = 'Draw Material Quad'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Material Context")

        self.outputs.new('NodeSocketShader', "Stage")
        
class DrawQuadNode(Node, CGPipelineTreeNode):
    '''Draw full-screen quad using shader node'''
    bl_idname = 'DrawQuadNodeType'
    bl_label = 'Draw Quad'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Shader Context")

        self.outputs.new('NodeSocketShader', "Stage")

class CallFunctionNode(Node, CGPipelineTreeNode):
    '''Call Haxe function node'''
    bl_idname = 'CallFunctionNodeType'
    bl_label = 'Call Function'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Function")

        self.outputs.new('NodeSocketShader', "Stage")
    
class BranchFunctionNode(Node, CGPipelineTreeNode):
    '''Branch on Haxe function result node'''
    bl_idname = 'BranchFunctionNodeType'
    bl_label = 'Branch Function'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Function")

        self.outputs.new('NodeSocketShader', "True")
        self.outputs.new('NodeSocketShader', "False")
        
class MergeStagesNode(Node, CGPipelineTreeNode):
    '''Join stages node'''
    bl_idname = 'MergeStagesNodeType'
    bl_label = 'Merge Stages'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Stage")

        self.outputs.new('NodeSocketShader', "Stage")

class LoopStagesNode(Node, CGPipelineTreeNode):
    '''Loop nested stages node'''
    bl_idname = 'LoopStagesNodeType'
    bl_label = 'Loop Stages'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketInt', "From")
        self.inputs.new('NodeSocketInt', "To")

        self.outputs.new('NodeSocketShader', "Complete")
        self.outputs.new('NodeSocketShader', "Loop")
        
class LoopLampsNode(Node, CGPipelineTreeNode):
    '''Loop nested stages node'''
    bl_idname = 'LoopLampsNodeType'
    bl_label = 'Loop Lamps'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")

        self.outputs.new('NodeSocketShader', "Complete")
        self.outputs.new('NodeSocketShader', "Loop")

class DrawStereoNode(Node, CGPipelineTreeNode):
    '''Draw nested stages twice node'''
    bl_idname = 'DrawStereoNodeType'
    bl_label = 'Draw Stereo'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")

        self.outputs.new('NodeSocketShader', "Complete")
        self.outputs.new('NodeSocketShader', "Per Eye")

class DrawWorldNode(Node, CGPipelineTreeNode):
    '''Draw world skydome node'''
    bl_idname = 'DrawWorldNodeType'
    bl_label = 'Draw World'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        # self.inputs.new('NodeSocketShader', "Depth")

        self.outputs.new('NodeSocketShader', "Stage")

class DrawCompositorNode(Node, CGPipelineTreeNode):
    '''Draw compositor node'''
    bl_idname = 'DrawCompositorNodeType'
    bl_label = 'Draw Compositor'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "Depth")
        self.inputs.new('NodeSocketShader', "Normals")

        self.outputs.new('NodeSocketShader', "Stage")

class DrawCompositorWithFXAANode(Node, CGPipelineTreeNode):
    '''Draw compositor with FXAA included node'''
    bl_idname = 'DrawCompositorWithFXAANodeType'
    bl_label = 'Draw Compositor + FXAA'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "Depth")
        self.inputs.new('NodeSocketShader', "Normals")

        self.outputs.new('NodeSocketShader', "Stage")

class DrawGreasePencilNode(Node, CGPipelineTreeNode):
    '''Draw grease pencil node'''
    bl_idname = 'DrawGreasePencilNodeType'
    bl_label = 'Draw Grease Pencil'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Context")

        self.outputs.new('NodeSocketShader', "Stage")

# Constant nodes
class ScreenNode(Node, CGPipelineTreeNode):
    '''Reference screen dimensions node'''
    bl_idname = 'ScreenNodeType'
    bl_label = 'Screen'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.outputs.new('NodeSocketInt', "Width")
        self.outputs.new('NodeSocketInt', "Height")
        self.inputs.new('NodeSocketFloat', "Scale")
        self.inputs[0].default_value = 1.0

class BackgroundColorNode(Node, CGPipelineTreeNode):
    '''Reference world background color node'''
    bl_idname = 'BackgroundColorNodeType'
    bl_label = 'Background Color'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.outputs.new('NodeSocketInt', "Color")
   
class LampCount(Node, CGPipelineTreeNode):
    '''Reference number of visible lamps in scene node'''
    bl_idname = 'LampCountNodeType'
    bl_label = 'Lamp Count'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.outputs.new('NodeSocketInt', "Count")

### Node Categories ###
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class MyCommandNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'

class MyTargetNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'

class MyPassNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'
        
class MyConstantNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'

class MyLogicNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'

node_categories = [
    MyCommandNodeCategory("COMMANDNODES", "Command", items=[
        NodeItem("BeginNodeType"),
        NodeItem("DrawMeshesNodeType"),
        NodeItem("DrawDecalsNodeType"),
        NodeItem("ClearTargetNodeType"),
        NodeItem("GenerateMipmapsNodeType"),
        NodeItem("SetTargetNodeType"),
        NodeItem("SetViewportNodeType"),
        NodeItem("BindTargetNodeType"),
        NodeItem("DrawMaterialQuadNodeType"),
        NodeItem("DrawQuadNodeType"),
        NodeItem("DrawWorldNodeType"),
        NodeItem("DrawCompositorNodeType"),
        NodeItem("DrawCompositorWithFXAANodeType"),
        NodeItem("DrawGreasePencilNodeType"),
    ]),
    MyTargetNodeCategory("TARGETNODES", "Target", items=[
        NodeItem("TargetNodeType"),
        NodeItem("ShadowMapNodeType"),
        NodeItem("ImageNodeType"),
        NodeItem("Image3DNodeType"),
        NodeItem("TargetArrayNodeType"),
        NodeItem("DepthBufferNodeType"),
        NodeItem("GBufferNodeType"),
        NodeItem("FramebufferNodeType"),
    ]),
    MyPassNodeCategory("PREBUILTNODES", "Prebuilt", items=[
        NodeItem("QuadPassNodeType"),
        NodeItem("SSAOPassNodeType"),
        NodeItem("SSAOReprojectPassNodeType"),
        NodeItem("ApplySSAOPassNodeType"),
        NodeItem("SSRPassNodeType"),
        NodeItem("BloomPassNodeType"),
        NodeItem("MotionBlurPassNodeType"),
        NodeItem("MotionBlurVelocityPassNodeType"),
        NodeItem("CopyPassNodeType"),
        NodeItem("BlendPassNodeType"),
        NodeItem("CombinePassNodeType"),
        NodeItem("BlurBasicPassNodeType"),
        NodeItem("DebugNormalsPassNodeType"),
        NodeItem("FXAAPassNodeType"),
        NodeItem("SMAAPassNodeType"),
        NodeItem("TAAPassNodeType"),
        NodeItem("SSSPassNodeType"),
        NodeItem("WaterPassNodeType"),
        NodeItem("DeferredLightPassNodeType"),
        NodeItem("DeferredIndirectPassNodeType"),
        NodeItem("VolumetricLightPassNodeType"),
        NodeItem("TranslucentResolvePassNodeType"),
    ]),
    MyConstantNodeCategory("CONSTANTNODES", "Constant", items=[
        NodeItem("ScreenNodeType"),
        NodeItem("BackgroundColorNodeType"),
        NodeItem("LampCountNodeType"),
    ]),
    MyLogicNodeCategory("LOGICNODES", "Logic", items=[
        NodeItem("CallFunctionNodeType"),
        NodeItem("BranchFunctionNodeType"),
        NodeItem("MergeStagesNodeType"),
        NodeItem("LoopStagesNodeType"),
        NodeItem("LoopLampsNodeType"),
        NodeItem("DrawStereoNodeType"),
    ]),
]

# Handling node data
def reload_blend_data():
    if bpy.data.node_groups.get('Armory PBR') == None:
        load_library('Armory PBR')
    check_default()

def check_default():
    if bpy.data.node_groups.get('armory_default') == None and len(bpy.data.cameras) > 0:
        make_renderer.make_renderer(bpy.data.cameras[0])

def load_library(asset_name, rename=None):
    sdk_path = armutils.get_sdk_path()
    data_path = sdk_path + '/armory/blender/data/data.blend'
    data_names = [asset_name]

    # Remove old
    if rename != None and rename in bpy.data.node_groups and asset_name != 'Armory PBR':
        bpy.data.node_groups.remove(bpy.data.node_groups[rename], do_unlink=True)

    # Import
    data_refs = data_names.copy()
    with bpy.data.libraries.load(data_path, link=False) as (data_from, data_to):
        data_to.node_groups = data_refs

    for ref in data_refs:
        ref.use_fake_user = True
        if rename != None:
            ref.name = rename

def register():
    bpy.utils.register_module(__name__)
    try:
        nodeitems_utils.register_node_categories("CG_PIPELINE_NODES", node_categories)
        reload_blend_data()
    except:
        pass

def unregister():
    nodeitems_utils.unregister_node_categories("CG_PIPELINE_NODES")
    bpy.utils.unregister_module(__name__)
