# Temporal Denoising Addon
This is an addon (for blender 4.1 or 4.0) that will allow you to use Blender's built in OptiX temporal denoiser. I wrote this for personal use so it might have some issues, just report them if you find any. 
## Pros
- temporal stability, something OIDN and other denoisers have some issues with.
- useful for animations with lights that would otherwise flicker between frames.
## Cons
- This can only be used in Cycles render engine.
- The noisy exr files can be very big (about 3G per 30 frames, very large).
- (medium) loss of detail. Allthough if you plan on uploading your animation compression will decrease detail anyway.
## Installation
- Go into edit>prefrences>addons
- Click install and choose the downloaded zip
- Enable the addon
- The control panel shows up in your render settings under "temporal denoising"
## Issues
- Low customizability
- The addon will overwrite your settings to enable some things for the engine.
- Existing compositor nodes might get messed up when it converts the denoised exr files into a video.
- Blender stops responding while doing any of the operations until the operation is finished.



