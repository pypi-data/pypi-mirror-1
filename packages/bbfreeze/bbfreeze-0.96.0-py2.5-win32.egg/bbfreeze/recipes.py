import sys
import os

def isRealModule(m):
    from modulegraph.modulegraph import BadModule, MissingModule, ExcludedModule
    if m is None or isinstance(m, (BadModule, MissingModule, ExcludedModule)):
        return False
    else:
        return True

def find_all_packages(name, skip=lambda x: False):
    def recipe(mf):
        m = mf.findNode(name)
        if not isRealModule(m):
            return None

        from bbfreeze.freezer import ZipModule
        if isinstance(m, ZipModule):
            return None

        import setuptools
        packages = setuptools.find_packages(os.path.dirname(m.filename))

        for pkg in packages:
            pkgname = '%s.%s' % (name, pkg)
            if not skip(pkgname):
                mf.import_hook(pkgname, m, ['*'])
        return True
    recipe.__name__ = "recipe_"+name
    return recipe

recipe_flup = find_all_packages('flup')
recipe_django = find_all_packages('django')
recipe_py = find_all_packages("py", skip=lambda x: x.startswith("py.test.tkinter"))
recipe_email = find_all_packages("email")
recipe_IPython = find_all_packages("IPython")

def recipe_django_core_management(mf):
    m = mf.findNode('django.core.management')
    if not isRealModule(m):
        return None
    refs = ["IPython"]
    for ref in refs:
        mf.removeReference(m, ref)
    return True
    
    
def recipe_pydoc(mf):
    m = mf.findNode('pydoc')
    if not isRealModule(m):
        return None
    
    refs = [
        'Tkinter', 'tty', 'BaseHTTPServer', 'mimetools', 'select',
        'threading', 'ic', 'getopt',
    ]
    if sys.platform != 'win32':
        refs.append('nturl2path')
    for ref in refs:
        mf.removeReference(m, ref)
    return True

def recipe_docutils(mf):
    m = mf.findNode('docutils')
    if not isRealModule(m):
        return None

    for pkg in [
            'languages', 'parsers', 'readers', 'writers',
            'parsers.rst.directives', 'parsers.rst.languages']:
        try:
            mf.import_hook('docutils.' + pkg, m, ['*'])
        except SyntaxError: # in docutils/writers/newlatex2e.py
            pass
    return True

def recipe_pythoncom(mf):
    m = mf.findNode("pythoncom")
    if not isRealModule(m):
        return None
    import pythoncom
    from bbfreeze.freezer import SharedLibrary
    n=mf.createNode(SharedLibrary, os.path.basename(pythoncom.__file__))
    n.filename = pythoncom.__file__
    mf.createReference(m, n)
    
    mf.import_hook('pywintypes', m, ['*'])

    return True

def recipe_pywintypes(mf):
    m = mf.findNode("pywintypes")
    if not isRealModule(m):
        return None
    import pywintypes
    from bbfreeze.freezer import SharedLibrary
    n=mf.createNode(SharedLibrary, os.path.basename(pywintypes.__file__))
    n.filename = pywintypes.__file__
    mf.createReference(m, n)
    return True


def recipe_py_magic_greenlet(mf):
    m = mf.findNode('py')
    if not isRealModule(m):
        return None

    pydir = os.path.dirname(m.filename)
    gdir = os.path.join(pydir, "c-extension", "greenlet")
    mf.path.append(gdir)
    mf.import_hook("greenlet", m, ['*'])



    gr = mf.findNode('py.magic.greenlet')
    if gr is None or gr.filename is None:
        return None

    gr.code = compile("""
__path__ = []    
import sys
mod = sys.modules[__name__]
from greenlet import greenlet
sys.modules[__name__] = mod
del mod
""", "py/magic/greenlet.py", "exec")
    
    return True

def recipe_time(mf):
    m = mf.findNode('time')
    
    # time is a BuiltinModule on win32, therefor m.filename is None
    if m is None: # or m.filename is None:
        return None
    
    mf.import_hook('_strptime', m, ['*'])
    return True

    
def NOT_USING_recipe_pkg_resources(mf):
    m = mf.findNode('pkg_resources')
    if not isRealModule(m):
        return None

    print "WARNING: replacing pkg_resources module with dummy implementation"
    


    m.code = compile("""
def require(*args, **kwargs):
    return
def declare_namespace(name):
    pass

""", "pkg_resources.py", "exec")
    
    return True


def recipe_matplotlib(mf):
    m = mf.findNode('matplotlib')
    if not isRealModule(m):
        return
    import matplotlib

    if 0:  # do not copy matplotlibdata. assume matplotlib is installed as egg
        dp = matplotlib.get_data_path()
        assert dp
        mf.copyTree(dp, "matplotlibdata", m)

    mf.import_hook("matplotlib.numerix.random_array", m)
    backend_name =  'backend_'+matplotlib.get_backend().lower()
    print "recipe_matplotlib: using the %s matplotlib backend" % (backend_name,)
    mf.import_hook('matplotlib.backends.'+backend_name, m)
    return True
    
    
def recipe_tkinter(mf):
    m = mf.findNode('_tkinter')
    if m is None or m.filename is None:
        return None

    if sys.platform=='win32':
        import Tkinter
        tcldir = os.environ.get("TCL_LIBRARY")
        if tcldir:
            mf.copyTree(tcldir, "lib-tcl", m)
        else:
            print "WARNING: recipe_tkinter: TCL_LIBRARY not set. cannot find lib-tcl"
            
        tkdir = os.environ.get("TK_LIBRARY")
        if tkdir:
            mf.copyTree(tkdir, "lib-tk", m)
        else:
            print "WARNING: recipe_tkinter: TK_LIBRARY not set. cannot find lib-tk"
            
        
    else:
        import _tkinter
        from bbfreeze import getdeps

        deps = getdeps.getDependencies(_tkinter.__file__)
        for x in deps:
            if os.path.basename(x).startswith("libtk"):
                tkdir = os.path.join(os.path.dirname(x), "tk%s" % _tkinter.TK_VERSION)
                if os.path.isdir(tkdir):
                    mf.copyTree(tkdir, "lib-tk", m)

        for x in deps:
            if os.path.basename(x).startswith("libtcl"):
                tcldir = os.path.join(os.path.dirname(x), "tcl%s" % _tkinter.TCL_VERSION)
                if os.path.isdir(tcldir):
                    mf.copyTree(tcldir, "lib-tcl", m)

    return True

def recipe_gtk_and_friends(mf):
    retval = False
    from bbfreeze.freezer import SharedLibrary
    from modulegraph.modulegraph import ExcludedModule
    for x in list(mf.flatten()):
        if not isinstance(x, SharedLibrary):
            continue

        prefixes = ["libpango", "libpangocairo", "libpangoft", "libgtk", "libgdk", "libglib", "libgmodule", "libgobject", "libgthread"]

        for p in prefixes:        
            if x.identifier.startswith(p):
                print "SKIPPING:", x
                x.__class__ = ExcludedModule
                retval = True                
                break
            
    return retval

def recipe_cElementTree25(mf):
    m = mf.findNode("_elementtree")
    
    if not isRealModule(m):
        return None

    mf.import_hook("pyexpat", m, "*")
    mf.import_hook("xml.etree.ElementTree")
    
    
    return True

def recipe_cElementTree(mf):
    m = mf.findNode("cElementTree")
    
    if not isRealModule(m):
        return None

    #mf.import_hook("pyexpat", m, "*")
    mf.import_hook("elementtree.ElementTree")
    
    
    return True

def recipe_mercurial(mf):
    m = mf.findNode("mercurial")
    if not isRealModule(m):
        return None
    mf.import_hook("hgext", m, "*")
    mf.import_hook("hgext.convert", m, "*")
    t = os.path.join(os.path.dirname(m.filename), "templates")
    mf.copyTree(t, "templates", m)
    return True

def recipe_kinterbasdb(mf):
    m = mf.findNode("kinterbasdb")
    if not isRealModule(m):
        return
    mods="""typeconv_23plus_lowmem
typeconv_23plus
typeconv_24plus
typeconv_backcompat
typeconv_datetime_mx
typeconv_datetime_naked
typeconv_datetime_stdlib
typeconv_fixed_decimal
typeconv_fixed_fixedpoint
typeconv_fixed_stdlib
typeconv_naked
typeconv_text_unicode""".split()
    for x in mods:
        mf.import_hook("kinterbasdb."+x, m)
    return True
