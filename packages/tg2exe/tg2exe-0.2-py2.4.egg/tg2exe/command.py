import os
import sys
import pkg_resources
import shutil
import glob
import py_compile
import modulefinder
try:
    import win32api
except:
    print "win32api not installed"
import traceback
from StringIO import StringIO

def get_exc_info():
    """Print the usual traceback information, followed by a listing of
    all the local variables in each frame.

    """

    tb = sys.exc_info()[2]
    while 1:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()

    exc_str = traceback.format_exc()
    exc_str += '\nLocals by frame, innermost last:'
    for frame in stack:
        exc_str += "\nFrame %s in %s at line %s" %(frame.f_code.co_name,frame.f_code.co_filename,frame.f_lineno)
        for key, value in frame.f_locals.items():
            exc_str += "\n\t%20s = " % key
            # We have to be careful not to cause a new error in our error
            # printer! Calling str() on an unknown object could cause an
            # error we don't want.
            try:
                exc_str += str(value)
            except:
                exc_str += '<ERROR WHILE PRINTING VALUE>'
    return exc_str

def favour_pyc_over_py(arg, dirname, fnames):
    """
    compile .py to .pyc, 
    then if .pyc is exist, remove .py
    """
    for f in fnames:
        if os.path.splitext(f)[1] == '.py':
            pyc = f + 'c'
            full_py = os.path.join(dirname, f)
            full_pyc = os.path.join(dirname, pyc)
            py_compile.compile(full_py, full_pyc)
            if os.path.exists(full_pyc):
                print 'Removing source file %s in %s' % (f, dirname)
                os.remove(full_py)

class Packager(object):

    def __init__(self):
        self.distdir = 'dist'
        self.libdir = os.path.join(self.distdir, 'Lib')
        self.sitepackdir = os.path.join(self.libdir, 'site-packages')
        self.py_basedir = os.path.split(sys.executable)[0]
        self.py_libdir = os.path.join(self.py_basedir, 'lib')
        self.py_sitepackdir = os.path.join(self.py_libdir,'site-packages')
        self.unique_dependencies = set()

    def make_package(self, distname):
        """working procedure is defined here"""
        self.distname = distname
        try:
            self.prepare_dest()
            self.get_basic_stuff()
            #self.get_eggs('TurboGears')
            self.get_my_code_with_dependencies()
            self.copy_special_files()
            self.clean_redundancies()
        except:
            print get_exc_info()

    def prepare_dest(self):
        print 'Preparing distribution directory...'
        if os.path.exists(self.distdir):
            shutil.rmtree(self.distdir, ignore_errors=True)
        os.makedirs(self.sitepackdir)

    def get_basic_stuff(self):
        # copy python.exe, PythonService.exe
        shutil.copy(sys.executable, self.distdir)
        # copy necessary libraries
        pydll = win32api.GetModuleFileName(\
                                win32api.LoadLibrary('python24.dll'))
        crtdll = win32api.GetModuleFileName(\
                                win32api.LoadLibrary('msvcr71.dll'))
        pycomdll = win32api.GetModuleFileName(\
                                win32api.LoadLibrary('pythoncom24.dll'))
        pywintypesdll = win32api.GetModuleFileName(\
                                win32api.LoadLibrary('pywintypes24.dll'))
        w32_dest = os.path.join(self.sitepackdir, 'win32')
        os.makedirs(w32_dest)

        shutil.copy(pydll, self.distdir)
        shutil.copy(crtdll, self.distdir)
        shutil.copy(pycomdll, self.distdir)
        shutil.copy(pywintypesdll, self.distdir)
        shutil.copy(os.path.join(self.py_sitepackdir,'win32','PythonService.exe'),
                                w32_dest)
        shutil.copy(os.path.join(self.py_libdir, 'site.py'),
                                self.libdir)
        shutil.copytree(os.path.join(self.py_basedir, 'DLLs'),
                                os.path.join(self.distdir, 'DLLs'))

    def get_eggs(self, name):
        print 'Getting list of eggs...'
        eggs = pkg_resources.require(name)
        self.eggpacks = set()
        eggspth = open(os.path.join(self.sitepackdir, 'eggs.pth'), 'w')
        for egg in eggs:
            dest = os.path.join(self.sitepackdir,
                                os.path.basename(egg.location))
            if not os.path.exists(dest):
                print 'Copying egg: %s' % egg
                eggspth.write('%s\n' % os.path.basename(egg.location))
                self.eggpacks.update(egg.get_metadata_lines('top_level.txt'))
                if os.path.isdir(egg.location):
                    shutil.copytree(egg.location, dest)
                else:
                    shutil.copy(egg.location, dest)
        eggspth.close()

    def get_my_code_with_dependencies(self):
        self.get_py_with_deps('.',self.distdir,
                              ['setup.py',
                               'start-*.*'])
        vlwdest = os.path.join(self.distdir, self.distname)
        os.mkdir(vlwdest)
        self.get_py_with_deps(self.distname, vlwdest)

    def get_py_with_deps(self, src, dest, exclude_masks=[]):
        print 'Processing sources in %s...' % src
        pyfiles = glob.glob(os.path.join(src, '*.py'))
        print pyfiles
        
        """exclfiles = []
        for ex in exclude_masks:
            exclfiles.extend(glob.glob(os.path.join(src, ex)))"""
        for py in pyfiles:
            pyc = py + 'c'
            print 'Compiling %s...' % py
            py_compile.compile(py, pyc)
            shutil.copy(pyc, dest)
            self.get_dependencies(py)

    def get_dependencies(self, py):
        print 'Searching for dependencies of %s...' % py
        mf = modulefinder.ModuleFinder()
        mf.run_script(py)
        copied = 0
        for key in mf.modules.keys():
            m = mf.modules[key]
            if self.is_new_dependency(m):
                self.copy_module(m)
                copied = copied + 1
        print '*** %s out of %s were new, unique dependencies ***' \
              % (copied, len(mf.modules))

    def copy_module(self, module):
        if str(module.__file__).find('site-packages') != -1:
            destbase = self.sitepackdir
        elif str(module.__file__).find(self.py_libdir) != -1:
            destbase = self.libdir
        else:
            print 'Module %s is no good!' % module.__file__
            return

        if module.__path__:
            # It's a package. Copy the whole dir.
            dest = os.path.join(destbase,
                                *(module.__name__.split('.')))
            if os.path.exists(dest):
                shutil.rmtree(dest, ignore_errors=True)
            dest_parent = os.path.split(dest)[0]
            if not os.path.exists(dest_parent):
                os.makedirs(dest_parent)
            print 'Copying package %s...' % module.__name__
            shutil.copytree(module.__path__[0], dest)
        elif module.__file__:
            dest_parent = os.path.join(destbase,*(module.__name__.split('.')[:-1]))
            if not os.path.exists(dest_parent):
                os.makedirs(dest_parent)
            if not os.path.exists(os.path.join(dest_parent,os.path.basename(module.__file__))):
                print 'Copying module %s...' % module.__name__
                shutil.copy(module.__file__, dest_parent)

    def is_new_dependency(self, module):
        if module.__name__ in self.unique_dependencies: return False
        firstpart = module.__name__.split('.')[0]
        #if firstpart in self.eggpacks: return False
        self.unique_dependencies.add(module.__name__)
        return True

    def copy_special_files(self):
        specials = {'.': ['*.dll', 'prod.cfg', 'pgvl.tar', '*.js'],
                    self.distname+'\\config': ['*.py', '*.cfg'],
                    self.distname+'\\static\\css': ['*.css'],
                    self.distname+'\\static\\images': ['*.gif','*.png',
                                                        '*.jpg','*.ico'],
                    self.distname+'\\static\\javascript': ['*.js'],
                    self.distname+'\\templates': ['*.py', '*.html', '*.kid', '*.tmpl']}

        for key in specials.keys():
            dest = os.path.join(self.distdir, key)
            if not os.path.exists(dest):
                os.makedirs(dest)
            for  mask in specials[key]:
                files = glob.glob(os.path.join(key, mask))
                for f in files:
                    print 'Copying file %s into %s...' % (f, dest)
                    shutil.copy(f, dest)

    def clean_redundancies(self):
        os.path.walk(self.distdir, favour_pyc_over_py, None)

class MakexeCommand:
    """Make project to a Stand Alone Application
    #TODO: add .exe to start proj
    #TODO: add .exe to open browser
    #TODO: append the .ico for proj
    """

    desc = "Make the Stand Alone Application"

    def __init__(self,*args, **kwargs):
        pass

    def run(self):
        # auto detect package name
        from turbogears.util import get_package_name
        self.package_name = get_package_name()
        # the main script
        p = Packager()
        p.make_package(self.package_name)         

