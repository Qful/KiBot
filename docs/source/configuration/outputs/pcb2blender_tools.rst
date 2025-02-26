.. Automatically generated by KiBot, please don't edit this file

.. index::
   pair: PCB2Blender Tools; pcb2blender_tools

PCB2Blender Tools
~~~~~~~~~~~~~~~~~

A bunch of tools used to generate PCB3D files used to export PCBs to Blender.
Blender is the most important free software 3D render package. |br|
This output needs KiCad 6 or newer. |br|
The PCB3D file format is used by the PCB2Blender project (https://github.com/30350n/pcb2blender)
to import KiCad PCBs in Blender. |br|
You need to install a Blender plug-in to load PCB3D files. |br|
The tools in this output are used by internal templates used to generate PCB3D files. |br|

Type: ``pcb2blender_tools``

Category: **PCB/3D/Auxiliar**

Parameters:

-  **comment** :index:`: <pair: output - pcb2blender_tools; comment>` [string=''] A comment for documentation purposes. It helps to identify the output.
-  **dir** :index:`: <pair: output - pcb2blender_tools; dir>` [string='./'] Output directory for the generated files.
   If it starts with `+` the rest is concatenated to the default dir.
-  **name** :index:`: <pair: output - pcb2blender_tools; name>` [string=''] Used to identify this particular output definition.
   Avoid using `_` as first character. These names are reserved for KiBot.
-  **options** :index:`: <pair: output - pcb2blender_tools; options>` [dict] Options for the `pcb2blender_tools` output.

   -  Valid keys:

      -  **output** :index:`: <pair: output - pcb2blender_tools - options; output>` [string='%f-%i%I%v.%x'] Filename for the output (%i=pcb2blender, %x=pcb3d). Affected by global options.
      -  **show_components** :index:`: <pair: output - pcb2blender_tools - options; show_components>` [list(string)|string=all] [none,all] List of components to include in the pads list,
         can be also a string for `none` or `all`. The default is `all`.

      -  ``board_bounds_create`` :index:`: <pair: output - pcb2blender_tools - options; board_bounds_create>` [boolean=true] Create the file that informs the size of the used PCB area.
         This is the bounding box reported by KiCad for the PCB edge with 1 mm of margin.
      -  ``board_bounds_dir`` :index:`: <pair: output - pcb2blender_tools - options; board_bounds_dir>` [string='layers'] Sub-directory where the bounds file is stored.
      -  ``board_bounds_file`` :index:`: <pair: output - pcb2blender_tools - options; board_bounds_file>` [string='bounds'] Name of the bounds file.
      -  ``dnf_filter`` :index:`: <pair: output - pcb2blender_tools - options; dnf_filter>` [string|list(string)='_none'] Name of the filter to mark components as not fitted.
         A short-cut to use for simple cases where a variant is an overkill.

      -  ``pads_info_create`` :index:`: <pair: output - pcb2blender_tools - options; pads_info_create>` [boolean=true] Create the files containing the PCB pads information.
      -  ``pads_info_dir`` :index:`: <pair: output - pcb2blender_tools - options; pads_info_dir>` [string='pads'] Sub-directory where the pads info files are stored.
      -  ``pre_transform`` :index:`: <pair: output - pcb2blender_tools - options; pre_transform>` [string|list(string)='_none'] Name of the filter to transform fields before applying other filters.
         A short-cut to use for simple cases where a variant is an overkill.

      -  ``stackup_create`` :index:`: <pair: output - pcb2blender_tools - options; stackup_create>` [boolean=false] Create a file containing the board stackup.
      -  ``stackup_dir`` :index:`: <pair: output - pcb2blender_tools - options; stackup_dir>` [string='.'] Directory for the stackup file. Use 'layers' for 2.7+.
      -  ``stackup_file`` :index:`: <pair: output - pcb2blender_tools - options; stackup_file>` [string='board.yaml'] Name for the stackup file. Use 'stackup' for 2.7+.
      -  ``stackup_format`` :index:`: <pair: output - pcb2blender_tools - options; stackup_format>` [string='JSON'] [JSON,BIN] Format for the stackup file. Use 'BIN' for 2.7+.
      -  ``sub_boards_bounds_file`` :index:`: <pair: output - pcb2blender_tools - options; sub_boards_bounds_file>` [string='bounds'] File name for the sub-PCBs bounds.
      -  ``sub_boards_create`` :index:`: <pair: output - pcb2blender_tools - options; sub_boards_create>` [boolean=true] Extract sub-PCBs and their Z axis position.
      -  ``sub_boards_dir`` :index:`: <pair: output - pcb2blender_tools - options; sub_boards_dir>` [string='boards'] Directory for the boards definitions.
      -  ``sub_boards_stacked_prefix`` :index:`: <pair: output - pcb2blender_tools - options; sub_boards_stacked_prefix>` [string='stacked\_'] Prefix used for the stack files.
      -  ``variant`` :index:`: <pair: output - pcb2blender_tools - options; variant>` [string=''] Board variant to apply.

-  **type** :index:`: <pair: output - pcb2blender_tools; type>` 'pcb2blender_tools'
-  ``category`` :index:`: <pair: output - pcb2blender_tools; category>` [string|list(string)=''] The category for this output. If not specified an internally defined category is used.
   Categories looks like file system paths, i.e. **PCB/fabrication/gerber**.
   The categories are currently used for `navigate_results`.

-  ``disable_run_by_default`` :index:`: <pair: output - pcb2blender_tools; disable_run_by_default>` [string|boolean] Use it to disable the `run_by_default` status of other output.
   Useful when this output extends another and you don't want to generate the original.
   Use the boolean true value to disable the output you are extending.
-  ``extends`` :index:`: <pair: output - pcb2blender_tools; extends>` [string=''] Copy the `options` section from the indicated output.
   Used to inherit options from another output of the same type.
-  ``groups`` :index:`: <pair: output - pcb2blender_tools; groups>` [string|list(string)=''] One or more groups to add this output. In order to catch typos
   we recommend to add outputs only to existing groups. You can create an empty group if
   needed.

-  ``output_id`` :index:`: <pair: output - pcb2blender_tools; output_id>` [string=''] Text to use for the %I expansion content. To differentiate variations of this output.
-  ``priority`` :index:`: <pair: output - pcb2blender_tools; priority>` [number=50] [0,100] Priority for this output. High priority outputs are created first.
   Internally we use 10 for low priority, 90 for high priority and 50 for most outputs.
-  ``run_by_default`` :index:`: <pair: output - pcb2blender_tools; run_by_default>` [boolean=true] When enabled this output will be created when no specific outputs are requested.

