# Virtual-Endoscopy-Generator
The template project sits halfway between a template project and a plugin -- It registers with Blender's plugin system so that it can be triggered through the menus, but it cannot be used as a standalone utility on an empty project file. The Blender scene contains materials, lighting, and camera parameters, and the Python script is intended only to automate the mesh processing that need to be done after sample data is imported. The key purpose of the script is to generate the camera path from the streamline data, and process it into a ready to render project.

The blend file consists of a single file, because all auxillary data is packed, including textures and Python files.

### More documentation is coming soon...

## Setup
- Install Blender version >= 5.1
- Export mesh data from VTK to GLTF format
- Export streamline data in a comma separated text file. 

Refer to the 'sample' folder for examples of how the input files should be formatted. The Python script may need to be modified for more flexibility with input formats.

## Step by Step
- Open *Virtual-Endoscopy-Generator.blend* in Blender.
- If a security warning pops up, select "Allow Execution" to permit the script to run.
    - Otherwise, you may trigger the script from the File -> Import menu, or pressing play in the Python editor window. 
- Select the GLTF file, and push *Import*.
    - The script provides 3 checkboxes for options, and in most cases you will want all of them checked.
    - Unchecking 'import streamline' will skip the next step.
- Select the streamline and push *Import*. At this point, the script will begin processing.
    - If the script generates an error, it will appear in the Blender system console.
- Save the modified Blender project to a new file.
- Start rendering a new animation by pressing Ctrl + F12.

## Extending & Modifying The Project

*todo*

## Credit
Samples provided by Guilherme Garcia. 

Blender project and script by Chris Larkee.
