# -*- coding: utf-8 -*-
# Copyright (c) 2020-2023 Salvador E. Tropea
# Copyright (c) 2020-2023 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
""" Miscellaneous definitions """

import re
import os
from contextlib import contextmanager


# Error levels
DONT_STOP = -1        # Keep going
INTERNAL_ERROR = 1    # Unhandled exceptions
WRONG_ARGUMENTS = 2   # This is what argsparse uses
UNSUPPORTED_OPTION = 3
MISSING_TOOL = 4
DRC_ERROR = 5
EXIT_BAD_ARGS = 6
EXIT_BAD_CONFIG = 7
NO_PCB_FILE = 8
NO_SCH_FILE = 9
ERC_ERROR = 10
BOM_ERROR = 11
PDF_SCH_PRINT = 12
PDF_PCB_PRINT = 13
PLOT_ERROR = 14
NO_YAML_MODULE = 15
NO_PCBNEW_MODULE = 16
CORRUPTED_PCB = 17
KICAD2STEP_ERR = 18
WONT_OVERWRITE = 19
PCBDRAW_ERR = 20
SVG_SCH_PRINT = 21
CORRUPTED_SCH = 22
WRONG_INSTALL = 23
RENDER_3D_ERR = 24
FAILED_EXECUTE = 25
KICOST_ERROR = 26
MISSING_WKS = 27
MISSING_FILES = 28
DIFF_TOO_BIG = 29
NETLIST_DIFF = 30
PS_SCH_PRINT = 31
DXF_SCH_PRINT = 32
HPGL_SCH_PRINT = 33
CORRUPTED_PRO = 34
BLENDER_ERROR = 35
WARN_AS_ERROR = 36
error_level_to_name = ['NONE',
                       'INTERNAL_ERROR',
                       'WRONG_ARGUMENTS',
                       'UNSUPPORTED_OPTION',
                       'MISSING_TOOL',
                       'DRC_ERROR',
                       'EXIT_BAD_ARGS',
                       'EXIT_BAD_CONFIG',
                       'NO_PCB_FILE',
                       'NO_SCH_FILE',
                       'ERC_ERROR',
                       'BOM_ERROR',
                       'PDF_SCH_PRINT',
                       'PDF_PCB_PRINT',
                       'PLOT_ERROR',
                       'NO_YAML_MODULE',
                       'NO_PCBNEW_MODULE',
                       'CORRUPTED_PCB',
                       'KICAD2STEP_ERR',
                       'WONT_OVERWRITE',
                       'PCBDRAW_ERR',
                       'SVG_SCH_PRINT',
                       'CORRUPTED_SCH',
                       'WRONG_INSTALL',
                       'RENDER_3D_ERR',
                       'FAILED_EXECUTE',
                       'KICOST_ERROR',
                       'MISSING_WKS',
                       'MISSING_FILES',
                       'DIFF_TOO_BIG',
                       'NETLIST_DIFF',
                       'PS_SCH_PRINT',
                       'DXF_SCH_PRINT',
                       'HPGL_SCH_PRINT',
                       'CORRUPTED_PRO',
                       'BLENDER_ERROR',
                       'WARN_AS_ERROR'
                       ]
KICOST_SUBMODULE = '../submodules/KiCost/src/kicost'
EXAMPLE_CFG = 'example_template.kibot.yaml'
AUTO_SCALE = 0
KICAD_VERSION_5_99 = 50990000
KICAD_VERSION_6_0_0 = 60000000
KICAD_VERSION_6_0_2 = 60000020
KICAD_VERSION_7_0_1 = 70000010
KICAD_VERSION_7_0_1_1 = 70000011
TRY_INSTALL_CHECK = 'Try running the installation checker: kibot-check'

# Internal filter names
IFILT_MECHANICAL = '_mechanical'
IFILT_KICOST_RENAME = '_kicost_rename'
IFILT_KICOST_DNP = '_kicost_dnp'
# KiCad 5 GUI values for the attribute
UI_THT = 0       # 1 for KiCad 6
UI_SMD = 1       # 2 for KiCad 6
UI_VIRTUAL = 2   # 12 for KiCad 6
# KiCad 6 module attributes from class_module.h
MOD_THROUGH_HOLE = 1
MOD_SMD = 2
MOD_EXCLUDE_FROM_POS_FILES = 4
MOD_EXCLUDE_FROM_BOM = 8
MOD_BOARD_ONLY = 16  # Footprint has no corresponding symbol
MOD_JUST_ADDED = 32  # The footprint was added by the netlist update
MOD_ALLOW_SOLDERMASK_BRIDGES = 64
MOD_ALLOW_MISSING_COURTYARD = 128
# This is what a virtual component gets when loaded by KiCad 6
MOD_VIRTUAL = MOD_EXCLUDE_FROM_POS_FILES | MOD_EXCLUDE_FROM_BOM
# VIATYPE, not exported by KiCad
VIATYPE_THROUGH = 3
VIATYPE_BLIND_BURIED = 2
VIATYPE_MICROVIA = 1

# Supported values for "do not fit"
DNF = {
    "dnf",
    "dnl",
    "dnp",
    "do not fit",
    "do not place",
    "do not load",
    "nofit",
    "nostuff",
    "noplace",
    "noload",
    "not fitted",
    "not loaded",
    "not placed",
    "no stuff",
}
# String matches for marking a component as "do not change" or "fixed"
DNC = {
    "dnc",
    "do not change",
    "no change",
    "fixed",
}
# KiCost distributors
DISTRIBUTORS = ['arrow', 'digikey', 'farnell', 'lcsc', 'mouser', 'newark', 'rs', 'tme']
DISTRIBUTORS_F = [d+'#' for d in DISTRIBUTORS]
DISTRIBUTORS_STUBS = ['part#', '#', 'p#', 'pn', 'vendor#', 'vp#', 'vpn', 'num']
DISTRIBUTORS_STUBS_SEPS = '_- '
# ISO ISO4217 currency codes
# Not all, but the ones we get from the European Central Bank (march 2021)
ISO_CURRENCIES = {'EUR', 'USD', 'JPY', 'BGN', 'CZK', 'DKK', 'GBP', 'HUF', 'PLN', 'RON', 'SEK', 'CHF', 'ISK', 'NOK', 'HRK',
                  'RUB', 'TRY', 'AUD', 'BRL', 'CAD', 'CNY', 'HKD', 'IDR', 'ILS', 'INR', 'KRW', 'MXN', 'MYR', 'NZD', 'PHP',
                  'SGD', 'THB', 'ZAR'}

W_VARCFG = '(W001) '
W_VARPCB = '(W002) '
W_PYCACHE = '(W003) '
W_FIELDCONF = '(W004) '
W_NOHOME = '(W005) '
W_NOUSER = '(W006) '
W_BADSYS = '(W007) '
W_NOCONFIG = '(W008) '
W_NOKIENV = '(W009) '
W_NOLIBS = '(W010) '
W_NODEFSYMLIB = '(W011) '
W_UNKGLOBAL = '(W012) '
W_PCBNOSCH = '(W013) '
W_NONEEDSKIP = '(W014) '
W_UNKOPS = '(W015) '
W_AMBLIST = '(W016) '
W_UNRETOOL = '(W017) '
W_USESVG2 = '(W018) '
W_USEIMAGICK = '(W019) '
W_BADVAL1 = '(W020) '
W_BADVAL2 = '(W021) '
W_BADVAL3 = '(W022) '
W_BADPOLI = '(W023) '
W_POLICOORDS = '(W024) '
W_BADSQUARE = '(W025) '
W_BADCIRCLE = '(W026) '
W_BADARC = '(W027) '
W_BADTEXT = '(W028) '
W_BADPIN = '(W029) '
W_BADCOMP = '(W030) '
W_BADDRAW = '(W031) '
W_UNKDCM = '(W032) '
W_UNKAR = '(W033) '
W_ARNOPATH = '(W034) '
W_ARNOREF = '(W035) '
W_MISCFLD = '(W036) '
W_EXTRASPC = '(W037) '
W_NOLIB = '(W038) '
W_INCPOS = '(W039) '
W_NOANNO = '(W040) '
W_MISSLIB = '(W041) '
W_MISSDCM = '(W042) '
W_MISSCMP = '(W043) '
W_VARSCH = '(W044) '
W_WRONGPASTE = '(W045) '
W_MISFLDNAME = '(W046) '
W_MISS3D = '(W047) '
W_FAILDL = '(W048) '
W_NOLAYER = '(W049) '
W_EMPTYZIP = '(W050) '
W_WRONGCHAR = '(W051) '
W_NOKIVER = '(W052) '
W_EXTNAME = '(W053) '
W_TIMEOUT = '(W054) '
W_MUSTBEINT = '(W055) '
W_NOOUTPUTS = '(W056) '
W_NOTASCII = '(W057) '
W_KIAUTO = '(W058) '
W_NUMSUBPARTS = '(W059) '
W_PARTMULT = '(W060) '
W_EMPTYREN = '(W061) '
W_BADFIELD = '(W062) '
W_UNKDIST = '(W063) '
W_UNKCUR = '(W064) '
W_NONETLIST = '(W065) '
W_NOKICOST = '(W066) '
W_UNKOUT = '(W067) '
W_NOFILTERS = '(W068) '
W_NOVARIANTS = '(W069) '
W_NOENDLIB = '(W070) '
W_NEEDSPCB = '(W071) '
W_NOGLOBALS = '(W072) '
W_EMPTREP = '(W073) '
W_BADCHARS = '(W074) '
W_DATEFORMAT = '(W075) '
W_UNKFLD = '(W076) '
W_ALRDOWN = '(W077) '
W_KICOSTFLD = '(W078) '
W_MIXVARIANT = '(W079) '
W_NOTPDF = '(W080) '
W_NOREF = '(W081) '
W_UNKVAR = '(W082) '
W_WRONGEXT = '(W083) '
W_COLORTHEME = '(W084) '
W_WRONGCOLOR = '(W085) '
W_WKSVERSION = '(W086) '
W_WRONGOAR = '(W087) '
W_ECCLASST = '(W088) '
W_PDMASKFAIL = '(W089) '
W_MISSTOOL = '(W090) '
W_NOTYET = '(W091) '
W_NOMATCH = '(W092) '
W_DOWNTOOL = '(W093) '
W_NOPREFLIGHTS = '(W094) '
W_NOPART = '(W095) '
W_MAXDEPTH = '(W096) '
W_3DRESVER = '(W097) '
W_DOWN3D = '(W098) '
W_MISSREF = '(W099) '
W_COPYOVER = '(W100) '
W_PARITY = '(W101) '
W_MISSFPINFO = '(W102) '
W_PCBDRAW = '(W103) '
W_NOCRTYD = '(W104) '
W_PANELEMPTY = '(W105) '
W_ONWIN = '(W106) '
W_AUTONONE = '(W106) '
W_AUTOPROB = '(W107) '
W_MORERES = '(W108) '
W_NOGROUPS = '(W109) '
W_UNKPCB3DTXT = '(W110) '
W_NOPCB3DBR = '(W111) '
W_NOPCB3DTL = '(W112) '
W_BADPCB3DTXT = '(W113) '
W_UNKPCB3DNAME = '(W114) '
W_BADPCB3DSTK = '(W115) '
W_EEDA3D = '(W116) '
W_MICROVIAS = '(W117) '
W_BLINDVIAS = '(W118) '
W_LIBTVERSION = '(W119) '
W_LIBTUNK = '(W120) '
W_DRC7BUG = '(W121) '
W_BADTOL = '(W122) '
W_BADRES = '(W123) '
W_RESVALISSUE = '(W124) '
W_RES3DNAME = '(W125) '
W_ESCINV = '(W126) '
W_BADVAL4 = '(W127) '
W_ENVEXIST = '(W128) '
W_FLDCOLLISION = '(W129) '
W_NEWGROUP = '(W130) '
W_NOTINBOM = '(W131) '
W_MISSDIR = '(W132) '
W_EXTRAINVAL = '(W133) '
W_BADANGLE = '(W134) '
W_VALMISMATCH = '(W135) '
W_BADOFFSET = '(W136) '
W_BUG16418 = '(W137) '
W_NOTHCMP = '(W138) '
W_KEEPTMP = '(W139) '
W_EXTRADOCS = '(W140) '
# Somehow arbitrary, the colors are real, but can be different
PCB_MAT_COLORS = {'fr1': "937042", 'fr2': "949d70", 'fr3': "adacb4", 'fr4': "332B16", 'fr5': "6cc290"}
PCB_FINISH_COLORS = {'hal': "8b898c", 'hasl': "8b898c", 'imag': "8b898c", 'enig': "cfb96e", 'enepig': "cfb96e",
                     'none': "d39751", 'hal snpb': "8b898c", 'hal lead-free': "8b898c", 'hard gold': "cfb96e",
                     'immersion silver': "8b898c", 'immersion ag': "8b898c", 'imau': "cfb96e", 'immersion gold': "cfb96e",
                     'immersion au': "cfb96e", 'immersion tin': "8b898c", 'immersion nickel': "cfb96e", 'osp': "d39751",
                     'ht_osp': "d39751"}
SOLDER_COLORS = {'green': ("#285e3a", "#208b47"),
                 'black': ("#1d1918", "#2d2522"),
                 'blue': ("#1b1f44", "#00406a"),
                 'red': ("#812e2a", "#be352b"),
                 'white': ("#bdccc7", "#b7b7ad"),
                 'yellow': ("#73823d", "#f2a756"),
                 'purple': ("#30234a", "#451d70")}
SILK_COLORS = {'black': "0b1013", 'white': "d5dce4"}
# Some browser name to pretend
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'
# Text used to disable 3D models
DISABLE_3D_MODEL_TEXT = '_Disabled_by_KiBot'
RENDERERS = ['pcbdraw', 'render_3d', 'blender_export']
PCB_GENERATORS = ['pcb_variant', 'panelize']
KIKIT_UNIT_ALIASES = {'millimeters': 'mm', 'inches': 'inch', 'mils': 'mil'}
FONT_HELP_TEXT = '\n        If you use custom fonts and/or colors please consult the `resources_dir` global variable.'


# Known rotations for JLC
# Notes:
# - Rotations are CC (counter clock)
# - Most components has pin 1 at the top-right angle, while KiCad uses the top-left
#   This is why most of the ICs has a rotation of 270 (-90)
# - The same applies to things like SOT-23-3, so here you get 180.
# - Most polarized components has pin 1 on the positive pin, becoming it the right one.
#   On KiCad this is not the case, diodes follows it, but capacitors don't. So they get 180.
# - There are exceptions, like SOP-18 or SOP-4 which doesn't follow the JLC rules.
# - KiCad mirrors components on the bottom layer, but JLC doesn't. So you need to "un-mirror" them.
# - The JLC mechanism to interpret rotations changed with time
DEFAULT_ROTATIONS = [["^R_Array_Convex_", 90.0],
                     ["^R_Array_Concave_", 90.0],
                     # *SOT* seems to need 180
                     ["^SOT-143", 180.0],
                     ["^SOT-223", 180.0],
                     ["^SOT-23", 180.0],
                     ["^SOT-353", 180.0],
                     ["^SOT-363", 180.0],
                     ["^SOT-89", 180.0],
                     ["^D_SOT-23", 180.0],
                     ["^TSOT-23", 180.0],
                     # Polarized capacitors
                     ["^CP_EIA-", 180.0],
                     ["^CP_Elec_", 180.0],
                     ["^C_Elec_", 180.0],
                     # Most four side components needs -90 (270)
                     ["^QFN-", 270.0],
                     ["^(.*?_|V)?QFN-(16|20|24|28|40)(-|_|$)", 270.0],
                     ["^DFN-", 270.0],
                     ["^LQFP-", 270.0],
                     ["^TQFP-", 270.0],
                     # SMD DIL packages mostly needs -90 (270)
                     ["^SOP-(?!(18_|4_))", 270.0],  # SOP 18 and 4 excluded, wrong at JLCPCB
                     ["^MSOP-", 270.0],
                     ["^TSSOP-", 270.0],
                     ["^HTSSOP-", 270.0],
                     ["^SSOP-", 270.0],
                     ["^SOIC-", 270.0],
                     ["^SO-", 270.0],
                     ["^SOIC127P798X216-8N", 270.0],
                     ["^VSSOP-8_3.0x3.0mm_P0.65mm", 270.0],
                     ["^VSSOP-8_", 180.0],
                     ["^VSSOP-10_", 270.0],
                     ["^VSON-8_", 270.0],
                     ["^TSOP-6", 270.0],
                     ["^UDFN-10", 270.0],
                     ["^USON-10", 270.0],
                     ["^TDSON-8-1", 270.0],
                     # Misc.
                     ["^LED_WS2812B_PLCC4", 180.0],
                     ["^LED_WS2812B-2020_PLCC4_2.0x2.0mm", 90.0],
                     ["^Bosch_LGA-", 90.0],
                     ["^PowerPAK_SO-8_Single", 270.0],
                     ["^PUIAudio_SMT_0825_S_4_R*", 270.0],
                     ["^USB_C_Receptacle_HRO_TYPE-C-31-M-12*", 180.0],
                     ["^ESP32-W", 270.0],
                     ["^SW_DIP_SPSTx01_Slide_Copal_CHS-01B_W7.62mm_P1.27mm", -180.0],
                     ["^BatteryHolder_Keystone_1060_1x2032", -180.0],
                     ["^Relay_DPDT_Omron_G6K-2F-Y", 270.0],
                     ["^RP2040-QFN-56", 270.0],
                     ["^TO-277", 90.0],
                     ["^SW_SPST_B3", 90.0],
                     ["^Transformer_Ethernet_Pulse_HX0068ANL", 270.0],
                     ["^JST_GH_SM", 180.0],
                     ["^JST_PH_S", 180.0],
                     ["^Diodes_PowerDI3333-8", 270.0],
                     ["^Quectel_L80-R", 270.0],
                     ["^SC-74-6", 180.0],
                     [r"^PinHeader_2x05_P1\.27mm_Vertical", 90.0],
                     [r"^PinHeader_2x03_P1\.27mm_Vertical", 90.0],
                     ]
DEFAULT_ROT_FIELDS = ['JLCPCB Rotation Offset', 'JLCRotOffset']
DEFAULT_OFFSETS = [["^USB_C_Receptacle_XKB_U262-16XN-4BVC11", (0.0, -1.44)],
                   [r"^PinHeader_2x05_P1\.27mm_Vertical", (2.54, 0.635)],
                   [r"^PinHeader_2x03_P1\.27mm_Vertical", (1.27, 0.635)],
                   ]
DEFAULT_OFFSET_FIELDS = ['JLCPCB Position Offset', 'JLCPosOffset']


class Rect(object):
    """ What KiCad returns isn't a real wxWidget's wxRect.
        Here I add what I really need """
    def __init__(self):
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None

    def Union(self, wxRect):
        if self.x1 is None:
            self.x1 = wxRect.x
            self.y1 = wxRect.y
            self.x2 = wxRect.x+wxRect.width
            self.y2 = wxRect.y+wxRect.height
        else:
            self.x1 = min(self.x1, wxRect.x)
            self.y1 = min(self.y1, wxRect.y)
            self.x2 = max(self.x2, wxRect.x+wxRect.width)
            self.y2 = max(self.y2, wxRect.y+wxRect.height)


def name2make(name):
    return re.sub(r'[ \$\.\\\/]', '_', name)


@contextmanager
def hide_stderr():
    """ Low level stderr suppression, used to hide KiCad bugs. """
    newstderr = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(newstderr, 2)


def version_str2tuple(ver):
    return tuple(map(int, ver.split('.')))
