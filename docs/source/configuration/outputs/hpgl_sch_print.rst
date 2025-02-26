.. Automatically generated by KiBot, please don't edit this file

.. index::
   pair: HPGL Schematic Print (Hewlett & Packard Graphics Language); hpgl_sch_print

HPGL Schematic Print (Hewlett & Packard Graphics Language)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exports the schematic to the most common plotter format.
This output is what you get from the 'File/Plot' menu in eeschema. |br|
If you use custom fonts and/or colors please consult the `resources_dir` global variable. |br|

Type: ``hpgl_sch_print``

Category: **Schematic/docs**

Parameters:

-  **comment** :index:`: <pair: output - hpgl_sch_print; comment>` [string=''] A comment for documentation purposes. It helps to identify the output.
-  **dir** :index:`: <pair: output - hpgl_sch_print; dir>` [string='./'] Output directory for the generated files.
   If it starts with `+` the rest is concatenated to the default dir.
-  **name** :index:`: <pair: output - hpgl_sch_print; name>` [string=''] Used to identify this particular output definition.
   Avoid using `_` as first character. These names are reserved for KiBot.
-  **options** :index:`: <pair: output - hpgl_sch_print; options>` [dict] Options for the `hpgl_sch_print` output.

   -  Valid keys:

      -  **frame** :index:`: <pair: output - hpgl_sch_print - options; frame>` [boolean=true] Include the frame and title block.
      -  ``all_pages`` :index:`: <pair: output - hpgl_sch_print - options; all_pages>` [boolean=true] Generate with all hierarchical sheets.
      -  ``background_color`` :index:`: <pair: output - hpgl_sch_print - options; background_color>` [boolean=false] Use the background color from the `color_theme` (KiCad 6).
      -  ``color_theme`` :index:`: <pair: output - hpgl_sch_print - options; color_theme>` [string=''] Color theme used, this must exist in the KiCad config (KiCad 6).
      -  ``dnf_filter`` :index:`: <pair: output - hpgl_sch_print - options; dnf_filter>` [string|list(string)='_none'] Name of the filter to mark components as not fitted.
         A short-cut to use for simple cases where a variant is an overkill.

      -  ``monochrome`` :index:`: <pair: output - hpgl_sch_print - options; monochrome>` [boolean=false] Generate a monochromatic output.
      -  ``origin`` :index:`: <pair: output - hpgl_sch_print - options; origin>` [string='bottom_left'] [bottom_left,centered,page_fit,content_fit] Origin and scale.
      -  ``output`` :index:`: <pair: output - hpgl_sch_print - options; output>` [string='%f-%i%I%v.%x'] Filename for the output HPGL (%i=schematic, %x=plt). Affected by global options.
      -  ``pen_size`` :index:`: <pair: output - hpgl_sch_print - options; pen_size>` [number=0.4826] Pen size (diameter) [mm].
      -  ``pre_transform`` :index:`: <pair: output - hpgl_sch_print - options; pre_transform>` [string|list(string)='_none'] Name of the filter to transform fields before applying other filters.
         A short-cut to use for simple cases where a variant is an overkill.

      -  ``title`` :index:`: <pair: output - hpgl_sch_print - options; title>` [string=''] Text used to replace the sheet title. %VALUE expansions are allowed.
         If it starts with `+` the text is concatenated.
      -  ``variant`` :index:`: <pair: output - hpgl_sch_print - options; variant>` [string=''] Board variant to apply.
         Not fitted components are crossed.

-  **type** :index:`: <pair: output - hpgl_sch_print; type>` 'hpgl_sch_print'
-  ``category`` :index:`: <pair: output - hpgl_sch_print; category>` [string|list(string)=''] The category for this output. If not specified an internally defined category is used.
   Categories looks like file system paths, i.e. **PCB/fabrication/gerber**.
   The categories are currently used for `navigate_results`.

-  ``disable_run_by_default`` :index:`: <pair: output - hpgl_sch_print; disable_run_by_default>` [string|boolean] Use it to disable the `run_by_default` status of other output.
   Useful when this output extends another and you don't want to generate the original.
   Use the boolean true value to disable the output you are extending.
-  ``extends`` :index:`: <pair: output - hpgl_sch_print; extends>` [string=''] Copy the `options` section from the indicated output.
   Used to inherit options from another output of the same type.
-  ``groups`` :index:`: <pair: output - hpgl_sch_print; groups>` [string|list(string)=''] One or more groups to add this output. In order to catch typos
   we recommend to add outputs only to existing groups. You can create an empty group if
   needed.

-  ``output_id`` :index:`: <pair: output - hpgl_sch_print; output_id>` [string=''] Text to use for the %I expansion content. To differentiate variations of this output.
-  ``priority`` :index:`: <pair: output - hpgl_sch_print; priority>` [number=50] [0,100] Priority for this output. High priority outputs are created first.
   Internally we use 10 for low priority, 90 for high priority and 50 for most outputs.
-  ``run_by_default`` :index:`: <pair: output - hpgl_sch_print; run_by_default>` [boolean=true] When enabled this output will be created when no specific outputs are requested.

