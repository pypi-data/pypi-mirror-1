import pkg_resources, glob, os

VERSION = '1.3.1'

INITIALIZED = False
PACKED = False #True
XHTML = False
SUBMODULES = []
PATHS = []
DRAGANDDROP = False

def init(register_static_directory, version=None, packed=None, xhtml=None, draganddrop=None):
    """
    Initializes the MochiKit resources.

The parameter register_static_directory is somewhat hackish: because this init
is called during initialization of turbogears.widgets itself, register_static_directory
isn't importable. So we need to pass it as argument.
    """
    global INITIALIZED, PACKED, XHTML, PATHS, VERSION, DRAGANDDROP
    if not INITIALIZED:
        if version is not None:
            VERSION = version
        if packed is not None:
            PACKED = packed
        if xhtml is not None:
            XHTML = xhtml
        if draganddrop is not None:
            DRAGANDDROP = draganddrop
        import turbogears.config
        INITIALIZED = True
        PACKED = turbogears.config.get('tg_mochikit.packed', PACKED)
        VERSION = turbogears.config.get('tg_mochikit.version', VERSION)
        XHTML = turbogears.config.get('tg_mochikit.xhtml', XHTML)
        DRAGANDDROP = turbogears.config.get('tg_mochikit.draganddrop', DRAGANDDROP)

        js_dir = pkg_resources.resource_filename("tgmochikit",
                                                 "static/javascript/%s" % VERSION)

        path = os.path.join(js_dir, "unpacked", "*.js")
        for name in glob.glob(path):
            module = os.path.basename(name)
            if not "__" in name and not "MochiKit" in module:
                SUBMODULES.append(module)
        register_static_directory("tgmochikit", js_dir)

        if PACKED:
            PATHS = ["packed/MochiKit/MochiKit.js"]
        else:
            res = ["unpacked/MochiKit.js"]
            if XHTML:
                for submodule in SUBMODULES:
                    res.append("unpacked/%s" % submodule)
            PATHS = res
        if DRAGANDDROP:
            PATHS.append("unpacked/DragAndDrop.js")
def get_paths():
    return PATHS
