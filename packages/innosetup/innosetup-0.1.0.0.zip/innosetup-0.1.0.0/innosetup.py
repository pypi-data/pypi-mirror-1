"""distutils extension module - create an installer by InnoSetup.

Required
--------

* Python 2.5 or later

* py2exe

* pywin32 (win32all)

* InnoSetup


Features
--------

* You can use your customized InnoSetup Script.

* installer metadata over setup() metadata

* AppId(GUID) from setup() metadata

* bundle exe and com dll and dependent libs and resources

* bundle msvcr and mfc and their manifest

* bundle all installed InnoSetup's language

* create `windows` exe's shortcut

* register `com_server` and `service`

* check the Windows version with Python version

* fix a problem py2exe.mf misses some modules (ex. win32com.shell)


An example::

    from distutils.core import setup
    import py2exe, innosetup

    setup_iss = '''
    [Setup]
    Compression=lzma/ultra
    SolidCompression=yes
    '''

    # All options are same as py2exe options.
    setup(
        name='example',
        version='1.0.0.0',
        license='PSF or other',
        author='you',
        author_email='you@your.domain',
        description='description',
        url='http://www.your.domain/example', # generate AppId from this url
        options={
            'innosetup': { # not py2exe
                # options from py2exe
                'compressed': True,
                'optimize': 2,
                'bundle_files': 3,
                # user defined iss file path or iss string
                'inno_script': setup_iss,
                }
            },
        com_server=[
            {'modules': ['your_com_server_module'], 'create_exe': False},
            ],
        # and other metadata ...
        )


"""
import sys, os, subprocess, ctypes, uuid, _winreg, distutils.msvccompiler
from xml.etree import ElementTree
import win32api # for read pe32 resource
from py2exe.build_exe import py2exe
from py2exe import mf as modulefinder


def lines(s):
    result = []
    for i in s.splitlines():
        i = i.strip()
        if i: result.append(i)
    return result or ['', ]


def modname(handle):
    """get module filename from HMODULE"""
    b = ctypes.create_unicode_buffer('', 1024)
    ctypes.windll.kernel32.GetModuleFileNameW(handle, b, 1024)
    return b.value


def manifest(handle):
    """get the first manifest string from HMODULE"""
    RT_MANIFEST = 24
    for restype in (RT_MANIFEST, ): #win32api.EnumResourceTypes(handle)
        for name in win32api.EnumResourceNames(handle, restype):
            return win32api.LoadResource(handle, restype, name).decode('utf_8')


def findfiles(files, *required):

    def check(filename):
        filename = filename.lower()
        for i in required:
            i = i.lower()
            if i.startswith('.'):
                if os.path.splitext(filename)[1] != i:
                    return
            elif i.count('.') == 1:
                if os.path.basename(filename) != i:
                    return
            else:
                if i not in os.path.basename(filename):
                    return
        return True

    return [i for i in files if check(i)]


def AddPackagePath(dottedname):
    try:
        names = dottedname.split('.')
        for i in range(len(names)):
            modname = '.'.join(names[:i + 1])
            __import__(modname)
            for path in getattr(sys.modules[modname], '__path__', [])[1:]:
                modulefinder.AddPackagePath(modname, path)
    except ImportError:
        pass


class InnoScript(object):

    consts_map = dict(
        AppName='%(name)s',
        AppVerName='%(name)s %(version)s',
        AppVersion='%(version)s',
        VersionInfoVersion='%(version)s',
        AppCopyright='%(author)s',
        AppContact='%(author_email)s',
        AppComments='%(description)s',
        AppPublisher='%(author)s',
        AppPublisherURL='%(url)s',
        AppSupportURL='%(url)s',
        )
    metadata_map = dict(
        DefaultDirName='{pf}\\%(name)s',
        OutputBaseFilename='%(name)s-%(version)s',
        )
    metadata_map.update(consts_map)
    required_sections = (
        'Setup', 'Files', 'Run', 'UninstallRun', 'Languages', 'Icons', )
    bin_exts = ('.exe', '.dll', '.pyd', )

    def __init__(self, builder):
        self.builder = builder

    def parse_iss(self, s):
        firstline = ''
        sectionname = ''
        lines = []
        for line in s.splitlines():
            if line.startswith('[') and ']' in line:
                if lines: yield firstline, sectionname, lines
                firstline = line
                sectionname = line[1:line.index(']')].strip()
                lines = []
            else:
                lines.append(line)
        if lines: yield firstline, sectionname, lines

    def chop(self, filename, dirname=''):
        if not dirname:
            dirname = self.builder.dist_dir
        if not dirname[-1] in "\\/":
            dirname += "\\"
        if filename.startswith(dirname):
            filename = filename[len(dirname):]
        #else:
        #    filename = os.path.basename(filename)
        return filename

    @property
    def metadata(self):
        metadata = dict((k, v or '') for k, v in
                        self.builder.distribution.metadata.__dict__.items())
        return metadata

    @property
    def appid(self):
        m = self.metadata
        if m['url']:
            src = m['url']
        elif m['name'] and m['version'] and m['author_email']:
            src = 'mailto:%(author_email)s?subject=%(name)s-%(version).1s' % m
        elif m['name'] and m['author_email']:
            src = 'mailto:%(author_email)s?subject=%(name)s' % m
        else:
            return m['name']
        appid = uuid.uuid5(uuid.NAMESPACE_URL, src).urn.rsplit(':', 1)[1]
        return '{{%s}' % appid

    @property
    def iss_consts(self):
        metadata = self.metadata
        return dict((k, v % metadata) for k, v in self.consts_map.items())

    @property
    def iss_metadata(self):
        metadata = self.metadata
        return dict((k, v % metadata) for k, v in self.metadata_map.items())

    @property
    def innoexepath(self):
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT,
                r'InnoSetupScriptFile\shell\compile\command')
            result = _winreg.QueryValue(key, '')
        except EnvironmentError:
            return ''
        if result.startswith('"'):
            result = result[1:].split('"', 1)[0]
        else:
            result = result.split()[0]
        return result

    @property
    def msvcfiles(self):
        # msvcrXX
        vcver = '%.2d' % (distutils.msvccompiler.get_build_version() * 10, )
        assemblename = 'Microsoft.VC%s.CRT' % vcver
        msvcr = getattr(ctypes.windll, 'msvcr' + vcver)
        vcrname = modname(msvcr._handle)
        yield vcrname

        # bundled file
        manifestfile = os.path.join(os.path.dirname(vcrname),
                                    assemblename + '.manifest')
        if os.path.isfile(manifestfile):
            pass

        # SxS
        else:
            manifestfile = os.path.join(self.builder.dist_dir,
                                        assemblename + '.manifest')

            doc = ElementTree.fromstring(manifest(sys.dllhandle))
            for e in doc.getiterator('{urn:schemas-microsoft-com:asm.v1}'
                                     'assemblyIdentity'):
                if e.attrib['name'] == assemblename: break
            else:
                raise EnvironmentError('no msvcr manifets file found')

            dirname = os.path.join(os.path.dirname(os.path.dirname(vcrname)),
                                   'Manifests')
            src = os.path.join(dirname, findfiles(os.listdir(dirname),
                assemblename, e.attrib['version'],
                e.attrib['processorArchitecture'], '.manifest')[0])
            data = open(src, 'rb').read()
            open(manifestfile, 'wb').write(data)

        yield manifestfile

        # mfc files
        mfcname = 'mfc%s.dll' % vcver
        mfcfiles = findfiles(self.builder.other_depends, mfcname)
        if mfcfiles:
            dirname = os.path.dirname(mfcfiles[0])
            for i in findfiles(os.listdir(dirname), 'mfc'):
                yield os.path.join(dirname, i)

    def handle_iss(self, lines, fp):
        for line in lines:
            fp.write(line); fp.write('\n')

    def handle_iss_setup(self, lines, fp):
        metadata = self.metadata
        iss_metadata = self.iss_metadata
        iss_metadata['OutputDir'] = self.builder.dist_dir
        iss_metadata['AppId'] = self.appid

        if getattr(self.builder, 'service_exe_files') or \
           getattr(self.builder, 'comserver_files'):
            iss_metadata['PrivilegesRequired'] = 'admin'

        # Python 2.6 doesn't support Windows 9x and me.
        if sys.version_info > (2, 6):
            iss_metadata['MinVersion'] = '5.0,4.0'

        for line in lines:
            name = line.split('=', 1)[0].strip()
            if name in iss_metadata:
                del iss_metadata[name]
            fp.write(line); fp.write('\n')

        if 'AppId' in iss_metadata:
            print 'There is no "AppId" in "[Setup]" section.'
            print '"AppId" is automatically generated from metadata (%s),' % \
                iss_metadata['AppId']
            print 'not a random value.'

        for k in sorted(iss_metadata):
            fp.write('%s=%s\n' % (k, iss_metadata[k], ))

        fp.write('\n')

    def handle_iss_files(self, lines, fp):
        self.handle_iss(lines, fp)

        tmpl = 'Source: "%s"; DestDir: "{app}\\%s"; Flags: ignoreversion %s\n'
        unremovable = getattr(self.builder, 'comserver_files')
        comserver_dll_files = [self.chop(i) for i in
            findfiles(getattr(self.builder, 'comserver_files', []), '.dll')]

        files = []
        excludes = []

        files.extend(self.msvcfiles)
        files.extend(self.builder.lib_files) #include data_files
        files.extend(getattr(self.builder, 'console_exe_files', []))
        files.extend(getattr(self.builder, 'windows_exe_files', []))
        files.extend(getattr(self.builder, 'service_exe_files', []))
        files.extend(getattr(self.builder, 'comserver_files', []))

        # Python 2.6 doesn't support Windows 9x and me.
        if sys.version_info > (2, 6):
            excludes.extend(findfiles(files, 'w9xpopen.exe'))

        stored = set()
        for filename in files:
            if filename in excludes: continue
            filename = self.chop(filename)
            if filename in ''.join(lines): continue
            ext = os.path.splitext(filename)[1].lower()
            flags = ''
            if unremovable and ext in self.bin_exts:
                flags += ' uninsrestartdelete'
            if filename in comserver_dll_files:
                flags += ' regserver'
            if filename.startswith(self.builder.dist_dir):
                place = os.path.dirname(filename)
            else:
                place = ''
            if filename not in stored:
                fp.write(tmpl % (filename, place, flags, ))
                stored.add(filename)

        fp.write('\n')

    def _iter_bin_files(self, attrname, lines=[]):
        for filename in getattr(self.builder, attrname, []):
            filename = self.chop(filename)
            if filename in ''.join(lines): continue
            yield filename

    def handle_iss_run(self, lines, fp):
        self.handle_iss(lines, fp)

        for filename in self._iter_bin_files('comserver_files', lines):
            if filename.lower().endswith('.exe'):
                fp.write('Filename: "%s"; Parameters: "/register"; WorkingDir: "{app}"; Flags: runhidden; StatusMsg: "Registering %s...";\n' % (filename, os.path.basename(filename), ))

        for filename in self._iter_bin_files('service_exe_files', lines):
            fp.write('Filename: "%s"; Parameters: "-install -auto"; WorkingDir: "{app}"; Flags: runhidden; StatusMsg: "Registering %s...";\n' % (filename, os.path.basename(filename), ))

    def handle_iss_uninstallrun(self, lines, fp):
        self.handle_iss(lines, fp)

        for filename in self._iter_bin_files('comserver_files', lines):
            if filename.lower().endswith('.exe'):
                fp.write('Filename: "%s"; Parameters: "/unregister"; WorkingDir: "{app}"; Flags: runhidden; StatusMsg: "Unregistering %s...";\n' % (filename, os.path.basename(filename), ))

        for filename in self._iter_bin_files('service_exe_files', lines):
            fp.write('Filename: "%s"; Parameters: "-remove"; WorkingDir: "{app}"; Flags: runhidden; StatusMsg: "Unregistering %s...";\n' % (filename, os.path.basename(filename), ))

    def handle_iss_icons(self, lines, fp):
        self.handle_iss(lines, fp)
        for filename in self._iter_bin_files('windows_exe_files', lines):
            fp.write('Name: "{group}\\%s"; Filename: "{app}\\%s"\n' % (self.metadata['name'], filename, ))
        if getattr(self.builder, 'windows_exe_files'):
            fp.write('Name: "{group}\\Uninstall %s"; Filename: "{uninstallexe}"' % (self.metadata['name'], ))

    def handle_iss_languages(self, lines, fp):
        self.handle_iss(lines, fp)

        if lines:
            return

        innopath = os.path.dirname(self.innoexepath)
        for root, dirs, files in os.walk(innopath):
            for basename in files:
                if not basename.lower().endswith('.isl'): continue
                filename = self.chop(os.path.join(root, basename), innopath)
                fp.write('Name: "%s"; MessagesFile: "compiler:%s"\n' % (os.path.splitext(basename)[0], filename, ))

    def create(self):
        self.issfile = os.path.join(self.builder.dist_dir, 'distutils.iss')

        inno_script = os.path.join(os.path.dirname(self.builder.dist_dir),
                                   self.builder.inno_script)
        if os.path.isfile(inno_script):
            inno_script = open(inno_script).read()
        else:
            inno_script = self.builder.inno_script

        fp = open(self.issfile, 'w')
        fp.write('; This file is created by distutils InnoSetup extension.\n')

        consts = self.iss_consts
        consts.update({
            'PYTHON_VERION': '%d.%d' % sys.version_info[:2],
            'PYTHON_VER': '%d%d' % sys.version_info[:2],
            'PYTHON_DIR': sys.prefix,
            'PYTHON_DLL': modname(sys.dllhandle),
            })
        consts.update((k.upper(), v) for k, v in self.metadata.items())
        for k in sorted(consts):
            fp.write('#define %s "%s"\n' % (k, consts[k], ))
        fp.write('\n')

        sections = set()
        for firstline, name, lines in self.parse_iss(inno_script):
            if firstline:
                fp.write(firstline); fp.write('\n')
            handler = getattr(self, 'handle_iss_%s' % name.lower(),
                              self.handle_iss)
            handler(lines, fp)
            fp.write('\n')
            sections.add(name)

        for name in self.required_sections:
            if name not in sections:
                fp.write('[%s]\n' % name)
                handler = getattr(self, 'handle_iss_%s' % name.lower())
                handler([], fp)
                fp.write('\n')

    def compile(self):
        subprocess.call([self.innoexepath, '/cc', self.issfile])
        #TODO: calc hash (md5 and sha1) and write into file
        #appname-1.0.0.0.exe.md5
        #appname-1.0.0.0.exe.sha1



class innosetup(py2exe):

    user_options = py2exe.user_options + [
        ('inno-script=', None,
         'a path to InnoSetup script file or an InnoSetup script string'),
        ]

    def initialize_options(self):
        py2exe.initialize_options(self)
        self.inno_script = ''

    def run(self):
        py2exe.run(self)

        script = InnoScript(self)
        print "*** creating the inno setup script ***"
        script.create()
        print "*** compiling the inno setup script ***"
        script.compile()


#
# register command
#
import distutils.command
distutils.command.__all__.append('innosetup')
sys.modules['distutils.command.innosetup'] = sys.modules[__name__]


#
# fix a problem py2exe.mf misses some modules
#
from modulefinder import packagePathMap
class PackagePathMap(object):
    def get(self, name, default=None):
        try:
            return packagePathMap[name]
        except LookupError:
            pass
        # path from Python import system
        try:
            names = name.split('.')
            for i in range(len(names)):
                modname = '.'.join(names[:i + 1])
                __import__(modname)
            return getattr(sys.modules[name], '__path__', [])[1:]
        except ImportError:
            pass
        return default
    def __setitem__(self, name, value):
        packagePathMap[name] = value
modulefinder.packagePathMap = PackagePathMap()


if __name__ == '__main__':
    sys.modules['innosetup'] = sys.modules[__name__]
    from distutils.core import setup
    setup(
        name='innosetup',
        version='0.1.0.0',
        license='PSF',
        description=__doc__.splitlines()[0],
        long_description=__doc__,
        author='chrono-meter@gmx.net',
        author_email='chrono-meter@gmx.net',
        url='http://pypi.python.org/pypi/innosetup',
        platforms='win32, win64',
        classifiers=lines('''
            Development Status :: 4 - Beta
            Environment :: Win32 (MS Windows)
            Intended Audience :: Developers
            License :: OSI Approved :: Python Software Foundation License
            Operating System :: Microsoft :: Windows :: Windows NT/2000
            Programming Language :: Python
            Topic :: Software Development :: Build Tools
            Topic :: Software Development :: Libraries :: Python Modules
            '''),
        py_modules=['innosetup', ],
        )


