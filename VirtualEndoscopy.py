bl_info = {
    # required
    'name': 'Virtual Endoscopy',
    'blender': (5, 1, 0),
    'category': 'Object',
    # optional
    'version': (0, 0, 3 ),
    'author': 'Chris Larkee',
    'description': 'Import a medical model and prepare it for rendering, automatically',
}


import bpy

#the functional code

def read_endomesh(context, filepath, meshOptions):
    if meshOptions["propClear"]:
        #Delete everything that's in the "Data" collection.
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_same_collection(collection="Data")
        bpy.ops.object.delete(use_global=False)
        bpy.ops.outliner.orphans_purge()
    
    #importNewData(filename):
    #ask for the location of the model, import it
    bpy.ops.import_scene.gltf(filepath=filepath, loglevel=50, merge_vertices=True, import_shading='SMOOTH')
    
    #move the imported mesh into the 'data' collection
    bpy.ops.object.select_pattern(pattern="mesh*", extend=False)
    bpy.ops.object.parent_clear(type='CLEAR')
    collectionID = bpy.data.collections['Data'].session_uid
    bpy.ops.object.move_to_collection(collection_uid=collectionID)
    
    #delete the extra lights and such
    bpy.ops.object.select_pattern(pattern="*Node", extend=False)
    bpy.ops.object.delete(use_global=False)
    bpy.ops.outliner.orphans_purge()
    
    if meshOptions["propCleanup"]:
        #select the main mesh
        obj = bpy.data.collections['Data'].objects['mesh0']    
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        #correct the transform
        #bpy.ops.transform.resize(value=(100, 100, 100), orient_type='GLOBAL')
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        #assign the material
        mat = bpy.data.materials['Meat']
        obj.material_slots[0].material = mat

        #enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.cube_project(cube_size=5, clip_to_bounds=True, scale_to_bounds=True)    
        bpy.ops.mesh.faces_shade_smooth()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

    if meshOptions["propStreamline"]:
        bpy.ops.import_endo.endostream('INVOKE_DEFAULT')

    return {'FINISHED'}
    
def read_endostream(context, filepath, meshOptions):
    print(filepath)
    #open the data file
    data = open(filepath, "r").read()

    #loop through the data, formatting it for Blender.
    verts, edges = [], []
    lines = data.split('\n')
    for x in range(1, len(lines)):
        coords = lines[x].split(',')
        if len(coords) >= 3:
            #translate to Y-up coordinate system
            v = (float(coords[0]) * 100.0, float(coords[2]) * -100.0, float(coords[1]) * 100.0)
            verts.append(v)
            if meshOptions["pointsAreContiguous"]:
                edges.append((x-1, x))
                
    if meshOptions["pointsAreContiguous"]:
        edges = edges[:-1]
            
    #create the mesh
    new_mesh = bpy.data.meshes.new('m_streamline')
    new_mesh.from_pydata(verts, edges, [])
    new_mesh.update()
    new_object = bpy.data.objects.new('streamline', new_mesh)
    bpy.data.collections[0].objects.link(new_object)

    #evenly distribute the verts
    bpy.context.view_layer.objects.active = new_object
    new_object.select_set(True)
    if meshOptions["cleanupNeeded"]:
        bpy.ops.object.modifier_add(type='WELD')
        bpy.context.object.modifiers["Weld"].merge_threshold = 0.05
        bpy.ops.object.modifier_apply(modifier="Weld", report=True)
        #bpy.ops.object.mode_set(mode='EDIT')
        #bpy.ops.mesh.select_all(action='SELECT')
        #bpy.ops.mesh.select_nth(skip=1, nth=3)
        #bpy.ops.mesh.dissolve_verts()

    #fix ordering and connect the verts into a line
    if meshOptions["pointsAreContiguous"] == False:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(2, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(True, True, True)})
        bpy.ops.object.vertex_group_assign_new()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bridge_edge_loops()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.outliner.orphans_purge()

    #convert to curve
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.convert(target='CURVE')
    bpy.data.curves[0].splines[0].use_smooth = True
    bpy.data.curves[0].twist_mode = 'Z_UP'
    bpy.data.curves[0].twist_smooth = 20
    bpy.data.curves[0].resolution_u = 20
    
    #attach the camera to the curve and set up animation parameters
    cam = bpy.data.objects["Camera"]
    cam.select_set(True)
    bpy.context.view_layer.objects.active = cam
    cam.constraints[0].target = bpy.data.objects['streamline']
    bpy.ops.constraint.followpath_path_animate(constraint="Follow Path", owner='OBJECT')
    bpy.data.curves[0].path_duration = 1000
    look = bpy.data.objects["Lookahead"]
    look.constraints[0].target = bpy.data.objects['streamline']
    bpy.ops.object.select_all(action='DESELECT')
    
    #set the output names
    outname = filepath.split("\\")[-2].zfill(2)
    if ("LEFT" in filepath):
        outname += "L"
    else:
        outname += "R"

    bpy.data.scenes[0].render.filepath = "//renders\\" + outname + "\\img_"
    bpy.data.node_groups[0].nodes['exr'].directory = "//renders\\" + outname + "\\"

    
    return {'FINISHED'}
    

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

class ImportEndoMesh(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_endo.endomesh"  # important since its how bpy.ops.import_endo.endomesh is constructed
    bl_label = "Import Endoscopy Project"

    # ImportHelper mixin class uses this
    filename_ext = "*.gltf;*.glb"

    filter_glob: StringProperty(
        default="*.gltf;*.glb",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    propClear: BoolProperty(
        name="Clear Old Data",
        description="Erase pre-existing objects in the 'data' collection.",
        default=True,
    )
    
    propCleanup: BoolProperty(
        name="Auto Cleanup",
        description="",
        default=True,
    )
    
    propStreamline: BoolProperty(
        name="Import Streamline",
        description="Include a second dialog to specify a streamline to import.",
        default=True,
    )

    def execute(self, context):
        meshOptions = {
            "propClear": self.propClear,
            "propCleanup": self.propCleanup,
            "propStreamline": self.propStreamline        
        }
        return read_endomesh(context, self.filepath, meshOptions)
    
class ImportEndoStream(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_endo.endostream"  # important since its how bpy.ops.import_endo.endomesh is constructed
    bl_label = "Import Endoscopy Streamline"

    # ImportHelper mixin class uses this
    filename_ext = "*.txt"

    filter_glob: StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    pointsAreContiguous: BoolProperty(
        name="Points Are Contiguous",
        description="...",
        default=True,
    )
    
    cleanupNeeded: BoolProperty(
        name="Cleanup Needed",
        description="Use modifiers to evenly space points.",
        default=True,
    )


    def execute(self, context):
        streamOptions = {
            "pointsAreContiguous": self.pointsAreContiguous,
            "cleanupNeeded": self.cleanupNeeded
        }
        return read_endostream(context, self.filepath, streamOptions)


# Only needed if you want to add into a dynamic menu.
def menu_func_import(self, context):
    self.layout.operator(ImportEndoMesh.bl_idname, text="Import Endoscopy Project")


# Register and add to the "file selector" menu (required to use F3 search "Import Endoscopy Project" for quick access).
def register():
    bpy.utils.register_class(ImportEndoMesh)
    bpy.utils.register_class(ImportEndoStream)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    try:
        bpy.utils.unregister_class(ImportEndoMesh)
        bpy.utils.unregister_class(ImportEndoStream)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    except:
        pass


if __name__ == "__main__":
    unregister()
    register()

    # test call
    bpy.ops.import_endo.endomesh('INVOKE_DEFAULT')
