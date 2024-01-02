# -*- coding: utf-8 -*-
# Copyright (c) 2023 Salvador E. Tropea
# Copyright (c) 2023 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
"""
Dependencies:
  - from: Blender
    role: mandatory
    version: 3.4.0
  - from: ImageMagick
    role: Automatically crop images
"""
import json
import os
import re
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory
from .error import KiPlotConfigurationError
from .kiplot import get_output_targets, run_output, run_command, register_xmp_import, config_output, configure_and_run
from .gs import GS
from .misc import MISSING_TOOL, BLENDER_ERROR
from .optionable import Optionable, BaseOptions
from .out_base_3d import Base3D, Base3DOptionsWithHL
from .registrable import RegOutput
from .macros import macros, document, output_class  # noqa: F401
from . import log

logger = log.get_logger()
bb = None
RE_FILE_ID = re.compile(r"\%\d*d")


def get_board_size():
    global bb
    if bb is None:
        bb = GS.board.ComputeBoundingBox(True)
    width = GS.to_mm(bb.GetWidth())/1000.0
    height = GS.to_mm(bb.GetHeight())/1000.0
    size = max(width, height)
    return width, height, size


class PCB2BlenderOptions(Optionable):
    """ How the PCB3D is imported """
    def __init__(self):
        super().__init__()
        with document:
            self.components = True
            """ Import the components """
            self.cut_boards = True
            """ Separate the sub-PCBs in separated 3D models """
            self.texture_dpi = 1016.0
            """ [508-2032] Texture density in dots per inch """
            self.center = True
            """ Center the PCB at the coordinates origin """
            self.enhance_materials = True
            """ Create good looking materials """
            self.merge_materials = True
            """ Reuse materials """
            self.solder_joints = "SMART"
            """ [NONE,SMART,ALL] The plug-in can add nice looking solder joints.
                This option controls if we add it for none, all or only for THT/SMD pads with solder paste """
            self.stack_boards = True
            """ Move the sub-PCBs to their relative position """
        self._unknown_is_error = True


class BlenderOutputOptions(Optionable):
    """ What is generated """
    def __init__(self):
        super().__init__()
        with document:
            self.type = 'render'
            """ *[fbx,obj,x3d,gltf,stl,ply,blender,render] The format for the output.
                The `render` type will generate a PNG image of the render result.
                `fbx` is Kaydara's Filmbox, 'obj' is the Wavefront, 'x3d' is the new ISO/IEC standard
                that replaced VRML, `gltf` is the standardized GL format, `stl` is the 3D printing
                format, 'ply' is Polygon File Format (Stanford).
                Note that some formats includes the light and camera and others are just the 3D model
                (i.e. STL and PLY) """
            self.output = GS.def_global_output
            """ Name for the generated file (%i='3D_blender_$VIEW' %x=VARIABLE).
                The extension is selected from the type """
            self.dir = ''
            """ Subdirectory for this output """
        self._unknown_is_error = True


class BlenderObjOptions(Optionable):
    """ A light/camera in the scene. """
    def __init__(self):
        super().__init__()
        with document:
            self.name = ""
            """ Name for the """
            self.pos_x = 0
            """ [number|string] X position [m]. You can use `width`, `height` and `size` for PCB dimensions """
            self.pos_y = 0
            """ [number|string] Y position [m]. You can use `width`, `height` and `size` for PCB dimensions """
            self.pos_z = 0
            """ [number|string] Z position [m]. You can use `width`, `height` and `size` for PCB dimensions """
        self._unknown_is_error = True

    def solve(self, member):
        val = getattr(self, member)
        if not isinstance(val, str):
            return float(val)
        try:
            res = eval(val, {}, {'width': self._width, 'height': self._width, 'size': self._size})
        except Exception as e:
            raise KiPlotConfigurationError('wrong `{}`: `{}`\nPython says: `{}`'.format(member, val, str(e)))
        return res

    def config(self, parent):
        super().config(parent)
        self._width, self._height, self._size = get_board_size()
        self.pos_x = self.solve('pos_x')
        self.pos_y = self.solve('pos_y')
        self.pos_z = self.solve('pos_z')


class BlenderLightOptions(BlenderObjOptions):
    """ A light in the scene. """
    def __init__(self):
        super().__init__()
        with document:
            self.type = "POINT"
            """ [POINT,SUN,SPOT,HEMI,AREA] Type of light. SUN lights will illuminate more evenly """
            self.energy = 0
            """ How powerful is the light. Using 0 for POINT and SUN KiBot will try to use something useful """
        self.add_to_doc('name', ' light', with_nl=False)

    def adjust(self):
        self._width, self._height, self._size = get_board_size()
        if not self.get_user_defined('pos_x') and not self.get_user_defined('pos_y') and not self.get_user_defined('pos_z'):
            self.pos_x = -self._size*3.33
            self.pos_y = self._size*3.33
            self.pos_z = self._size*5.0
        if self.energy == 0:
            if self.type == "POINT":
                # 10 W is the default, works for 5 cm board, we make it grow cudratically
                self.energy = 10.0*((self._size/0.05)**2)
            elif self.type == "SUN":
                # This is power by area
                self.energy = 2

    def config(self, parent):
        super().config(parent)
        self.adjust()


class BlenderCameraOptions(BlenderObjOptions):
    """ A camera in the scene. """
    CAM_TYPE = {'perspective': 'PERSP', 'orthographic': 'ORTHO', 'panoramic': 'PANO'}

    def __init__(self):
        super().__init__()
        with document:
            self.type = "perspective"
            """ [perspective,orthographic,panoramic] Type of camera """
            self.clip_start = -1
            """ Minimum distance for objects to the camera. Any object closer than this distance won't be visible.
                Only positive values have effect. A negative value has a special meaning.
                For a camera with defined position, a negative value means to use Blender defaults (i.e. 0.1 m).
                For cameras without position KiBot will ask Blender to compute its position and the use a clip
                distance that is 1/10th of the Z distance """
        self.add_to_doc('name', ' camera', with_nl=False)

    def config(self, parent):
        super().config(parent)
        self._type = self.CAM_TYPE[self.type]


class BlenderRenderOptions(Optionable):
    """ Render parameters """
    def __init__(self):
        super().__init__()
        with document:
            self.samples = 10
            """ *How many samples we create. Each sample is a raytracing render.
                Use 1 for a raw preview, 10 for a draft and 100 or more for the final render """
            self.resolution_x = 1280
            """ Width of the image """
            self.width = None
            """ {resolution_x} """
            self.resolution_y = 720
            """ Height of the image """
            self.height = None
            """ {resolution_y} """
            self.transparent_background = False
            """ *Make the background transparent """
            self.background1 = "#66667F"
            """ First color for the background gradient """
            self.background2 = "#CCCCE5"
            """ Second color for the background gradient """
            self.auto_crop = False
            """ When enabled the image will be post-processed to remove the empty space around the image.
                In this mode the `background2` is changed to be the same as `background1` """
        self._unknown_is_error = True


class BlenderPointOfViewOptions(Optionable):
    """ Point of View parameters """
    _views = {'top': 'z', 'bottom': 'Z', 'front': 'y', 'rear': 'Y', 'right': 'x', 'left': 'X'}
    _rviews = {v: k for k, v in _views.items()}

    def __init__(self):
        super().__init__()
        with document:
            self.rotate_x = 0
            """ Angle to rotate the board in the X axis, positive is clockwise [degrees] """
            self.rotate_y = 0
            """ Angle to rotate the board in the Y axis, positive is clockwise [degrees] """
            self.rotate_z = 0
            """ Angle to rotate the board in the Z axis, positive is clockwise [degrees] """
            self.view = 'top'
            """ *[top,bottom,front,rear,right,left,z,Z,y,Y,x,X] Point of view.
                Compatible with `render_3d` """
            self.file_id = ''
            """ String to diferentiate the name of this point of view.
                When empty we use the `default_file_id` or the `view` """
            self.steps = 1
            """ [1-1000] Generate this amount of steps using the rotation angles as increments.
                Use a value of 1 (default) to interpret the angles as absolute.
                Used for animations. You should define the `default_file_id` to something like
                '_%03d' to get the animation frames """
        self._unknown_is_error = True

    def config(self, parent):
        super().config(parent)
        # View point
        view = self._views.get(self.view, None)
        if view is not None:
            self.view = view

    def get_view(self):
        return self._rviews.get(self.view, 'no_view')

    def increment(self, inc):
        self.rotate_x += inc.rotate_x
        self.rotate_y += inc.rotate_y
        self.rotate_z += inc.rotate_z


class PCB3DExportOptions(Base3DOptionsWithHL):
    """ Options to generate the PCB3D file """
    def __init__(self):
        super().__init__()
        with document:
            self.output = GS.def_global_output
            """ Name for the generated PCB3D file (%i='blender_export' %x='pcb3d') """
            self.version = '2.7'
            """ [2.1,2.1_haschtl,2.7] Variant of the format used """
            self.solder_paste_for_populated = True
            """ Add solder paste only for the populated components.
                Populated components are the ones listed in `show_components` """
        self._expand_id = 'blender_export'
        self._expand_ext = 'pcb3d'
        self._unknown_is_error = True

    def get_output_name(self, out_dir):
        p = self._parent
        cur_id = p._expand_id
        cur_ext = p._expand_ext
        p._expand_id = self._expand_id
        p._expand_ext = self._expand_ext
        out_name = p._parent.expand_filename(out_dir, self.output)
        p._expand_id = cur_id
        p._expand_ext = cur_ext
        return out_name

    def setup_renderer(self, components, active_components, bottom, name):
        super().setup_renderer(components, active_components)
        self._pov.view = 'Z' if bottom else 'z'
        # Expand the name using .PNG
        cur_ext = self._expand_ext
        self._expand_ext = 'png'
        o_name = self.expand_filename_both(name, is_sch=False)
        self._expand_ext = cur_ext
        self._out.output = o_name
        return o_name

    def save_renderer_options(self):
        """ Save the current renderer settings """
        p = self._parent
        # We are an option inside another option
        self._parent = self._parent._parent
        super().save_renderer_options()
        self._parent = p
        self.old_show_all_components = self._show_all_components
        self.old_view = self._pov.view
        self.old_output = self._out.output

    def restore_renderer_options(self):
        """ Restore the renderer settings """
        p = self._parent
        self._parent = self._parent._parent
        super().restore_renderer_options()
        self._parent = p
        self._show_all_components = self.old_show_all_components
        self._pov.view = self.old_view
        self._out.output = self.old_output


class Blender_ExportOptions(BaseOptions):
    def __init__(self):
        with document:
            self.pcb3d = PCB3DExportOptions
            """ *[string|dict] Options to export the PCB to Blender.
                You can also specify the name of the output that generates the PCB3D file.
                See the `PCB2Blender_2_1`, `PCB2Blender_2_7` and `PCB2Blender_2_1_haschtl` templates """
            self.pcb_import = PCB2BlenderOptions
            """ Options to configure how Blender imports the PCB.
                The default values are good for most cases """
            self.outputs = BlenderOutputOptions
            """ [dict|list(dict)] Outputs to generate in the same run """
            self.light = BlenderLightOptions
            """ [dict|list(dict)] Options for the light/s """
            self.add_default_light = True
            """ Add a default light when none specified.
                The default light is located at (-size*3.33, size*3.33, size*5) where size is max(width, height) of the PCB """
            self.camera = BlenderCameraOptions
            """ [dict] Options for the camera.
                If none specified KiBot will create a suitable camera.
                If no position is specified for the camera KiBot will look for a suitable position """
            self.fixed_auto_camera = False
            """ When using the automatically generated camera and multiple points of view this option computes the camera
                position just once. Suitable for videos """
            self.auto_camera_z_axis_factor = 1.1
            """ Value to multiply the Z axis coordinate after computing the automatically generated camera.
                Used to avoid collision of the camera and the object """
            self.default_file_id = ''
            """ Default value for the `file_id` in the `point_of_view` options.
                Use something like '_%03d' for animations """
            self.render_options = BlenderRenderOptions
            """ *[dict] Controls how the render is done for the `render` output type """
            self.point_of_view = BlenderPointOfViewOptions
            """ *[dict|list(dict)] How the object is viewed by the camera """
        super().__init__()
        self._expand_id = '3D_blender'
        self._unknown_is_error = True

    def config(self, parent):
        super().config(parent)
        # Check we at least have a name for the source output
        if isinstance(self.pcb3d, str) and not self.pcb3d:
            raise KiPlotConfigurationError('You must specify the name of the output that'
                                           ' generates the PCB3D file or its options')
        if isinstance(self.pcb3d, type):
            self.pcb3d = PCB3DExportOptions()
            self.pcb3d.config(self)
        # Do we have outputs?
        if isinstance(self.outputs, type):
            self.outputs = []
        elif isinstance(self.outputs, BlenderOutputOptions):
            # One, make a list
            self.outputs = [self.outputs]
        # Ensure we have import options
        if isinstance(self.pcb_import, type):
            self.pcb_import = PCB2BlenderOptions()
        # Ensure we have a light
        if isinstance(self.light, type):
            # None
            if self.add_default_light:
                # Create one
                light = BlenderLightOptions()
                light.name = 'kibot_light'
                light.adjust()
                self.light = [light]
            else:
                # The dark ...
                self.light = []
        elif isinstance(self.light, BlenderLightOptions):
            # Ensure a list
            self.light = [self.light]
        # Check light names
        light_names = set()
        for li in self.light:
            name = li.name if li.name else 'kibot_light'
            if name in light_names:
                id = 2
                while name+'_'+str(id) in light_names:
                    id += 1
                name = name+'_'+str(id)
            li.name = name
        # If no camera let the script create one
        if isinstance(self.camera, type):
            self.camera = None
        elif not self.camera.name:
            self.camera.name = 'kibot_camera'
        # Ensure we have some render options
        if isinstance(self.render_options, type):
            self.render_options = BlenderRenderOptions()
        # Point of View, make sure we have a list and at least 1 element
        if isinstance(self.point_of_view, type):
            self.point_of_view = [BlenderPointOfViewOptions()]
        elif isinstance(self.point_of_view, BlenderPointOfViewOptions):
            self.point_of_view = [self.point_of_view]

    def get_output_filename(self, o, output_dir, pov, order):
        if o.type == 'render':
            self._expand_ext = 'png'
        elif o.type == 'blender':
            self._expand_ext = 'blend'
        else:
            self._expand_ext = o.type
        cur_id = self._expand_id
        file_id = pov.file_id
        if not file_id:
            file_id = self.default_file_id or ('_'+pov.get_view())
        m = RE_FILE_ID.search(file_id)
        if m:
            res = m.group(0)
            val = res % order
            file_id = file_id.replace(res, val)
        self._expand_id += file_id
        name = self._parent.expand_filename(os.path.join(output_dir, o.dir), o.output)
        self._expand_id = cur_id
        return name

    def get_targets(self, out_dir):
        files = []
        if isinstance(self.pcb3d, PCB3DExportOptions):
            files.append(self.pcb3d.get_output_name(out_dir))
        order = 1
        for pov in self.point_of_view:
            for _ in range(pov.steps):
                for o in self.outputs:
                    files.append(self.get_output_filename(o, out_dir, pov, order))
        return files

    def create_vrml(self, dest_dir):
        tree = {'name': '_temporal_vrml_for_pcb3d',
                'type': 'vrml',
                'comment': 'Internally created for the PCB3D',
                'dir': dest_dir,
                'options': {'output': 'pcb.wrl',
                            'dir_models': 'components',
                            'use_pcb_center_as_ref': False,
                            'model_units': 'meters'}}
        out = RegOutput.get_class_for('vrml')()
        out.set_tree(tree)
        config_output(out)
        out.options.copy_options(self.pcb3d)
        logger.debug(' - Creating VRML ...')
        out.options.run(os.path.join(dest_dir, 'pcb.wrl'))

    def create_layers(self, dest_dir):
        out_dir = os.path.join(dest_dir, 'layers')
        tree = {'name': '_temporal_svgs_layers',
                'type': 'svg',
                'comment': 'Internally created for the PCB3D',
                'dir': out_dir,
                'options': {'output': '%i.%x',
                            'margin': 1,
                            'limit_viewbox': True,
                            'svg_precision': 6,
                            'drill_marks': 'none'},
                'layers': ['F.Cu', 'B.Cu', 'F.Paste', 'B.Paste', 'F.Mask', 'B.Mask',
                           {'layer': 'F.SilkS', 'suffix': 'F_SilkS'},
                           {'layer': 'B.SilkS', 'suffix': 'B_SilkS'}]}
        configure_and_run(tree, out_dir, ' - Creating SVG for layers ...')

    def create_pads(self, dest_dir):
        options = {'stackup_create': False}
        if self.pcb3d.version == '2.1_haschtl':
            options['stackup_create'] = True
        elif self.pcb3d.version == '2.7':
            options['stackup_create'] = True
            options['stackup_file'] = 'stackup'
            options['stackup_dir'] = 'layers'
            options['stackup_format'] = 'BIN'
        tree = {'name': '_temporal_pcb3d_tools',
                'type': 'pcb2blender_tools',
                'comment': 'Internally created for the PCB3D',
                'dir': dest_dir,
                'options': options}
        if self.pcb3d.solder_paste_for_populated:
            sc = 'all'
            if not self.pcb3d._show_all_components:
                sc = 'none' if not self.pcb3d.show_components else self.pcb3d._show_components_raw
            tree['options']['show_components'] = sc
        configure_and_run(tree, dest_dir, ' - Creating Pads and boundary ...')

    def create_pcb3d(self, data_dir):
        out_dir = self._parent.output_dir
        # Compute the name for the PCB3D
        out_name = self.pcb3d.get_output_name(out_dir)
        tree = {'name': '_temporal_compress_pcb3d',
                'type': 'compress',
                'comment': 'Internally created for the PCB3D',
                'dir': out_dir,
                'options': {'output': out_name,
                            'format': 'ZIP',
                            'files': [{'source': os.path.join(data_dir, 'boards'),
                                       'dest': '/'},
                                      {'source': os.path.join(data_dir, 'boards/*'),
                                       'dest': 'boards'},
                                      {'source': os.path.join(data_dir, 'components'),
                                       'dest': '/'},
                                      {'source': os.path.join(data_dir, 'components/*'),
                                       'dest': 'components'},
                                      {'source': os.path.join(data_dir, 'layers'),
                                       'dest': '/'},
                                      {'source': os.path.join(data_dir, 'layers/*'),
                                       'dest': 'layers'},
                                      {'source': os.path.join(data_dir, 'pads'),
                                       'dest': '/'},
                                      {'source': os.path.join(data_dir, 'pads/*'),
                                       'dest': 'pads'},
                                      {'source': os.path.join(data_dir, 'pcb.wrl'),
                                       'dest': '/'},
                                      ]}}
        configure_and_run(tree, out_dir, ' - Creating the PCB3D ...')
        return out_name

    def solve_pcb3d(self):
        if isinstance(self.pcb3d, str):
            # An output creates it
            pcb3d_targets, _, pcb3d_out = get_output_targets(self.pcb3d, self._parent)
            pcb3d_file = pcb3d_targets[0]
            logger.debug('- From file '+pcb3d_file)
            if not pcb3d_out._done:
                logger.debug('-  Running '+self.pcb3d)
                run_output(pcb3d_out)
            self._pcb3d = PCB3DExportOptions()
            self._pcb3d.output = pcb3d_file
            # Needed by ensure tool
            self._pcb3d._parent = self._parent
        else:
            # We create it
            with TemporaryDirectory() as tmp_dir:
                # VRML
                self.create_vrml(tmp_dir)
                # SVG layers
                self.create_layers(tmp_dir)
                # Pads and bounds
                self.create_pads(tmp_dir)
                # Compress the files
                pcb3d_file = self.create_pcb3d(tmp_dir)
            self._pcb3d = self.pcb3d
            # Needed by ensure tool
            self.type = self._parent.type
        if not os.path.isfile(pcb3d_file):
            raise KiPlotConfigurationError('Missing '+pcb3d_file)
        return pcb3d_file

    def analyze_errors(self, msg):
        if 'Traceback ' in msg:
            logger.error('Error from Blender run:\n'+msg[msg.index('Traceback '):])
            sys.exit(BLENDER_ERROR)

    def run(self, output):
        if GS.ki5:
            logger.error("`blender_export` needs KiCad 6+")
            exit(MISSING_TOOL)
        pcb3d_file = self.solve_pcb3d()
        # If no outputs specified just finish
        # Can be used to export the PCB to Blender
        if not self.outputs:
            return
        # Make sure Blender is available
        command = self._pcb3d.ensure_tool('Blender')
        if self.render_options.auto_crop:
            # Avoid a gradient
            self.render_options.background2 = self.render_options.background1
            convert_command = self.ensure_tool('ImageMagick')
        # Create a JSON with the scene information
        with NamedTemporaryFile(mode='w', suffix='.json') as f:
            scene = {}
            if self.light:
                lights = [{'name': light.name,
                           'position': (light.pos_x, light.pos_y, light.pos_z),
                           'type': light.type,
                           'energy': light.energy} for light in self.light]
                scene['lights'] = lights
            if self.camera:
                ca = self.camera
                scene['camera'] = {'name': ca.name,
                                   'type': ca._type}
                if (hasattr(ca, '_pos_x_user_defined') or hasattr(ca, '_pos_y_user_defined') or
                   hasattr(ca, '_pos_z_user_defined')):
                    scene['camera']['position'] = (ca.pos_x, ca.pos_y, ca.pos_z)
                if ca.clip_start >= 0:
                    scene['camera']['clip_start'] = ca.clip_start
            scene['fixed_auto_camera'] = self.fixed_auto_camera
            scene['auto_camera_z_axis_factor'] = self.auto_camera_z_axis_factor
            ro = self.render_options
            scene['render'] = {'samples': ro.samples,
                               'resolution_x': ro.resolution_x,
                               'resolution_y': ro.resolution_y,
                               'transparent_background': ro.transparent_background,
                               'background1': ro.background1,
                               'background2': ro.background2}
            povs = []
            last_pov = BlenderPointOfViewOptions()
            for pov in self.point_of_view:
                if pov.steps > 1:
                    for _ in range(pov.steps):
                        last_pov.increment(pov)
                        povs.append({'rotate_x': -last_pov.rotate_x,
                                     'rotate_y': -last_pov.rotate_y,
                                     'rotate_z': -last_pov.rotate_z,
                                     'view': pov.view})
                else:
                    povs.append({'rotate_x': -pov.rotate_x,
                                 'rotate_y': -pov.rotate_y,
                                 'rotate_z': -pov.rotate_z,
                                 'view': pov.view})
                    last_pov = pov
            scene['point_of_view'] = povs
            text = json.dumps(scene, sort_keys=True, indent=2)
            logger.debug('Scene:\n'+text)
            f.write(text)
            f.flush()
            # Create the command line
            script = os.path.join(os.path.dirname(__file__), 'blender_scripts', 'blender_export.py')
            cmd = [command, '-b', '--factory-startup', '-P', script, '--']
            pi = self.pcb_import
            if not pi.components:
                cmd.append('--no_components')
            if not pi.cut_boards:
                cmd.append('--dont_cut_boards')
            if pi.texture_dpi != 1016.0:
                cmd.extend(['--texture_dpi', str(pi.texture_dpi)])
            if not pi.center:
                cmd.append('--dont_center')
            if not pi.enhance_materials:
                cmd.append('--dont_enhance_materials')
            if not pi.merge_materials:
                cmd.append('--dont_merge_materials')
            if pi.solder_joints != "SMART":
                cmd.extend(['--solder_joints', pi.solder_joints])
            if not pi.stack_boards:
                cmd.append('--dont_stack_boards')
            cmd.append('--format')
            for pov in self.point_of_view:
                for _ in range(pov.steps):
                    for o in self.outputs:
                        cmd.append(o.type)
            cmd.append('--output')
            names = set()
            order = 1
            for pov in self.point_of_view:
                for _ in range(pov.steps):
                    for o in self.outputs:
                        name = self.get_output_filename(o, self._parent.output_dir, pov, order)
                        if name in names:
                            raise KiPlotConfigurationError('Repeated name (use `file_id`): '+name)
                        cmd.append(name)
                        names.add(name)
                    order += 1
            cmd.extend(['--scene', f.name])
            cmd.append(pcb3d_file)
            # Execute the command
            self.analyze_errors(run_command(cmd))
        if self.render_options.auto_crop:
            for pov in self.point_of_view:
                for o in self.outputs:
                    if o.type != 'render':
                        continue
                    name = self.get_output_filename(o, self._parent.output_dir, pov)
                    run_command([convert_command, name, '-trim', '+repage', '-trim', '+repage', name])


@output_class
class Blender_Export(Base3D):
    """ Blender Export
        Exports the PCB in various 3D file formats.
        Also renders the PCB with high-quality.
        Needs KiCad 6 or newer.
        This output is complex to setup and needs very big dependencies.
        Please be patient when using it.
        You need Blender with the pcb2blender plug-in installed.
        Visit: [pcb2blender](https://github.com/30350n/pcb2blender).
        You can just generate the exported PCB if no output is specified.
        You can also export the PCB and render it at the same time """
    def __init__(self):
        super().__init__()
        with document:
            self.options = Blender_ExportOptions
            """ *[dict] Options for the `blender_export` output """
        self._category = 'PCB/3D'

    def get_dependencies(self):
        files = BaseOutput.get_dependencies(self)  # noqa: F821
        if isinstance(self.options.pcb3d, str):
            files.append(self.options.pcb3d)
        else:
            files.extend(self.options.pcb3d.list_models())
        return files

    def get_renderer_options(self):
        """ Where are the options for this output when used as a 'renderer' """
        ops = self.options
        out = next(filter(lambda x: x.type == 'render', ops.outputs), None)
        res = None
        if out is not None:
            if isinstance(ops.pcb3d, str):
                # We can't configure it
                out = None
            else:
                res = ops.pcb3d
                res._pov = ops.point_of_view[0]
                res._out = out
        return res if out is not None else None

    def get_extension(self):
        # Used when we are a renderer
        return 'png'

    @staticmethod
    def get_conf_examples(name, layers):
        if not GS.check_tool(name, 'Blender') or GS.ki5:
            return None
        has_top = False
        has_bottom = False
        for la in layers:
            if la.is_top() or la.layer.startswith('F.'):
                has_top = True
            elif la.is_bottom() or la.layer.startswith('B.'):
                has_bottom = True
        if not has_top and not has_bottom:
            return None
        register_xmp_import('PCB2Blender_2_1')
        povs = []
        if has_top:
            povs.append({'view': 'top'})
            povs.append({'rotate_x': 30, 'rotate_z': -20, 'file_id': '_30deg'})
        if has_bottom:
            povs.append({'view': 'bottom'})
        gb = {}
        gb['name'] = 'basic_{}'.format(name)
        gb['comment'] = '3D view from top/30 deg/bottom (Blender)'
        gb['type'] = name
        gb['dir'] = '3D'
        gb['options'] = {'pcb3d': '_PCB2Blender_2_1',
                         'outputs': [{'type': 'render'}, {'type': 'blender'}],
                         'point_of_view': povs}
        return [gb]
