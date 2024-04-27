import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator
from . import Temporal
from bpy_extras.io_utils import ExportHelper
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
import os


bl_info = {
    "name": "Temporal Denoising",
    "author": "Merasmus44",
    "blender": (4,0,2),
    "category": "Render",
    "description": "Temporal Denoising.",
}






class TemporalDenoiseOperator(bpy.types.Operator):
    """Set the proper viewlayer and render settings for temporal denoising. Do this before anything else, and after you finished converting to video."""
    bl_idname = "render.temporal_denoise"
    bl_label = "Set Viewlayer Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene
        view_layer = context.view_layer
        RenderEngine = scene.render.engine
        if RenderEngine != "CYCLES":
            #print("Temporal Denoising only works with cycles at the moment.")
            return {'CANCELLED'}
        # Enable vector passes and denoising data
        scene.cycles.use_denoising = False# we want to denoise with our denoiser
        view_layer.use_pass_vector = True
        view_layer.cycles.denoising_store_passes = True
        view_layer.use_pass_combined = True
        
       
        view_layer.use_pass_normal = True

      

        # Set output file format to OpenEXR Multilayer
        scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'



        return {'FINISHED'}




class SetOpenEXRMultilayerOperator(bpy.types.Operator):
    """Render your animation and run temporal denoise on it"""
    bl_idname = "render.set_openexr_multilayer"
    bl_label = "Set Output to OpenEXR Multilayer"

    def execute(self, context):
        scene.cycles.use_denoising = False # make sure it doesn't denoise for us
        context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER' # make sure the output is correct, if you didn't already run the initialization steps
        bpy.ops.render.render(animation=True)
        context.scene.render.select_output_directory()
        return {'FINISHED'}








class SetupCompositorOperator(bpy.types.Operator):
    """Setup the compositor and sequencer, then render the video. Make sure you denoise with temporal denoising first or this won't work. This will output the video into the directory specified in the Output tab, so you should probably change that directory."""
    bl_idname = "render.setup_compositor"
    bl_label = "Setup Compositor"




    def get_image_files(self, image_folder_path, image_extension=".exr"):
        image_files = list()
        for file_name in os.listdir(image_folder_path):
            if file_name.endswith(image_extension):
                image_files.append(file_name)
        image_files.sort()


        return image_files


    def import_image_sequence_into_compositor(self, image_folder_path, fps):
        image_files = self.get_image_files(image_folder_path)

        file_info = list()
        for image_name in image_files:
            file_info.append({"name": image_name})

        bpy.ops.image.open(directory=image_folder_path, files=file_info)


        image_data_name = image_files[0]
        image_sequence = bpy.data.images[image_data_name]
        duration = len(image_files)
        return image_sequence, duration



    def execute(self, context):
        scene = context.scene

        # Enable compositing
        scene.use_nodes = True
        tree = scene.node_tree


        scene.render.image_settings.file_format = 'FFMPEG' #make sure we are outputting a video

        # Delete the render layers node
        for node in tree.nodes:
            if node.type == 'R_LAYERS':
                tree.nodes.remove(node)

        # Add an image node connected to the composite node
        image_node = tree.nodes.new(type='CompositorNodeImage')
        image_node.location = 0, 0
        
        composite_node = None
        for node in tree.nodes:
            if node.type == 'COMPOSITE':
                composite_node = node
                break

        # If a Composite node doesn't exist, create one
        if not composite_node:
            composite_node = tree.nodes.new(type='CompositorNodeComposite')
            

        folder_path = bpy.path.abspath(scene.DenoisedOutput)

        if not os.path.exists(folder_path):
            folder_path = folder_path.replace(folder_path.split("\\")[-1], "")

        image_sequence, duration = self.import_image_sequence_into_compositor(folder_path,scene.render.fps)

        image_node.image = image_sequence
        image_node.frame_duration = duration

        tree.links.new(image_node.outputs[0], composite_node.inputs[0])

        # Add a Scene Strip to the VSE
        scene.sequence_editor_create()
        bpy.ops.render.render(animation=True)


        return {'FINISHED'}





class TemporalDenoisingPanel(bpy.types.Panel):
    bl_label = "Temporal Denoising"
    bl_idname = "RENDER_PT_temporal_denoising"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {"DEFAULT_CLOSED"}


    


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        

        layout.operator("render.temporal_denoise", text="Set Viewlayer Settings")
        layout.operator("render.set_openexr_multilayer", text="Render and Denoise")
        row = layout.row()
        row.operator("render.select_output_directory", text="Denoise only (after manual render)")
        row = layout.row()
        row.prop(scene, 'conserve_noisy_files', text="Conserve Noisy Files")
        row = layout.row() 
        layout.operator("render.setup_compositor", text="Setup and Render")
        


    

class SelectOutputDirectoryOperator(Operator, ExportHelper):
    """Select the output directory and start denoising files from the input directory (input directory is the output directory in the render output tab)"""
    bl_idname = "render.select_output_directory"
    bl_label = "Select Output Directory"
    bl_options = {'REGISTER'}

    filename_ext = ""

    def execute(self, context):
        scene = bpy.context.scene
        RenderEngine = scene.render.engine
        if RenderEngine != "CYCLES":
            print("Temporal Denoising only works with cycles at the moment.")
            return {'CANCELLED'}
        # Get the output directory
        output_directory = scene.render.filepath
        conserve_noisy_files = scene.conserve_noisy_files


        print("Denoising...")
        bpy.types.Scene.DenoisedOutput = self.filepath
        wm = bpy.context.window_manager
        return Temporal.DoTemporal(output_directory,self.filepath,wm,conserve_noisy_files)#wm


classes = (
    TemporalDenoiseOperator,
    SetOpenEXRMultilayerOperator,
    TemporalDenoisingPanel,
    SelectOutputDirectoryOperator,
    SetupCompositorOperator
)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.conserve_noisy_files = bpy.props.BoolProperty(
        name="Conserve Noisy Files",
        description="Whether to keep the noisy render files. The noisy files take up a very large amount of space, so disabling this option will delete each noisy image after it has been denoised",
        default=True
    )
    


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    


if __name__ == "__main__":
    register()
