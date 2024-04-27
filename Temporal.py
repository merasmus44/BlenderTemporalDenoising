import bpy
import os 
import glob


def DoTemporal(inputdir, outputdir, wm, conserve):
    wm.progress_begin(0, 100)
    os.chdir(inputdir) 
    myfiles=(glob.glob("*.exr"))
    current = 1
    wm.progress_update(0)
    for file in myfiles:
       print(str(inputdir) + str(file) + " to " + str(outputdir) + str(file))
       bpy.ops.cycles.denoise_animation(input_filepath=(str(inputdir) + str(file)), output_filepath=(str(outputdir) + str(file)))
       if not conserve:
           os.remove(file)
       wm.progress_update((current/len(myfiles))*100)
       current += 1
    wm.progress_end()
    return {'FINISHED'}

