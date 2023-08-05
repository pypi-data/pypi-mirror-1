import os, sys, re, imp
from distutils import util
from distutils.core import Command
from distutils.errors import DistutilsInternalError, DistutilsSetupError
from distutils.dir_util import remove_tree

_can_read_reg = False
try:
    import _winreg
    RegOpenKeyEx = _winreg.OpenKeyEx
    RegQueryValueEx = _winreg.QueryValueEx
    RegError = _winreg.error
    HKEY_LOCAL_MACHINE = _winreg.HKEY_LOCAL_MACHINE

    _can_read_reg = True

except ImportError:
    try:
        import win32api
        import win32con
        RegOpenKeyEx = win32api.RegOpenKeyEx
        RegQueryValueEx = win32api.RegQueryValueEx
        RegError = win32api.error
        HKEY_LOCAL_MACHINE = win32con.HKEY_LOCAL_MACHINE

        _can_read_reg = True

    except ImportError:
        pass

PY_SOURCE_EXTS = [ s for s,m,t in imp.get_suffixes() if t == imp.PY_SOURCE ]

ISCC_TEMPLATE = """
[Setup]
OutputDir=%(output-dir)s
OutputBaseFilename=%(name)s-%(version)s.win32-py%(target-version)s
AppName=%(name)s
AppVersion=%(version)s
AppVerName=%(name)s %(version)s for Python %(target-version)s
AppId=%(name)s %(version)s for Python %(target-version)s
AppPublisher=%(publisher)s
AppPublisherURL=%(publisher-url)s
AppSupportURL=%(support-url)s
UninstallFilesDir=%(uninstall-dir)s
DefaultDirName=ignored
DefaultGroupName={code:GetPythonGroup}
LicenseFile=%(license-file)s
UserInfoPage=no
DisableDirPage=yes
DisableReadyMemo=yes
FlatComponentsList=no

[Types]
Name: "full"; Description: "Full installation"
Name: "compact"; Description: "Compact installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
%(components)s

%(sections)s

[Code]
const
  AppName = '%(name)s';
  PythonVersion = '%(target-version)s';
  UseCustomLocation = False; { Disabled until custom locations are fixed }

var
  PythonGroup: String;
  PythonBaseDir: String;
  PythonDir: String;
  CustomDir: String;
  InstallDir: String;
  CustomRadio: TRadioButton;
  CustomBrowse: TButton;
  CustomEdit: TEdit;
  CustomPage: Integer;

function GetPythonGroup(Default: String): String;
begin
  Result := PythonGroup;
end; { GetPythonGroup }

function GetPythonDir(Default: String): String;
begin
  Result := PythonBaseDir;
end; { GetPythonDir }

function GetInstallDir(Default: String): String;
begin
  Result := InstallDir;
end; { GetInstallDir }

function EscapeBackslashes(Source: String): String;
begin
    StringChange(Source, '\\', '\\\\');
    Result := Source;
end;

procedure MutateConfigFile(Filename: String);
var
  Config: String;
  Replacement: String;
begin
  Filename := ExpandConstant(Filename);
  LoadStringFromFile(Filename, Config);
  Replacement := EscapeBackslashes(RemoveBackslashUnlessRoot(InstallDir));
  StringChange(Config, '\\\\PYTHONLIB\\\\', Replacement);
  Replacement := EscapeBackslashes(AddBackslash(PythonBaseDir));
  StringChange(Config, '\\\\PREFIX\\\\', Replacement);
  SaveStringToFile(Filename, Config, False);
end; { MutateConfigFile }

{ OnChange handler for custom edit box }
procedure CustomEditChange(Sender: TObject);
begin
  CustomRadio.Checked := True;
end; { CustomEditChange }

{ OnClick handler for custom button }
procedure BrowseClick(Sender: TObject);
var
  Directory: String;
begin
  if BrowseForFolder('Select folder for installation:', Directory, True) then
  begin
    CustomEdit.Text := Directory;
  end;
end; { BrowseClick }

procedure InitializeWizard;
var
  Page: TWizardPage;
  Top: Integer;
  Registry: TRadioButton;
  Caption, Note: TLabel;
begin
  Page := CreateCustomPage(%(custom-page)s, 'Select Destination Directory',
                           'Where should ' + AppName + ' be installed?');
  CustomPage := Page.ID;

  Caption := TLabel.Create(Page);
  Caption.Parent := Page.Surface;
  Caption.Caption := 'Select the folder where you would like ' + AppName +
                     ' to be installed, then click Next.';
  Top := Caption.Height + 8;

  if PythonDir <> '' then
  begin
    Registry := TRadioButton.Create(Page);
    Registry.Parent := Page.Surface;
    Registry.Caption := PythonDir;
    Registry.Top := Top;
    Registry.Width := Page.SurfaceWidth;
    Registry.Checked := (PythonDir = InstallDir);
    Top := Top + Registry.Height + 8;
  end;

  CustomRadio := TRadioButton.Create(Page);
  CustomRadio.Visible := UseCustomLocation;
  CustomRadio.Parent := Page.Surface;
  CustomRadio.Caption := '';
  CustomRadio.Width := 16;
  CustomRadio.Top := Top;
  CustomRadio.Checked := (CustomDir = InstallDir);
  CustomBrowse := TButton.Create(Page);
  CustomBrowse.Visible := UseCustomLocation;
  CustomBrowse.Parent := Page.Surface;
  CustomBrowse.OnClick := @BrowseClick;
  CustomBrowse.Caption := 'Browse...';
  CustomBrowse.Height := 23;
  CustomBrowse.Top := Top;
  CustomBrowse.Left := Page.SurfaceWidth - CustomBrowse.Width;
  CustomEdit := TEdit.Create(Page);
  CustomEdit.Visible := UseCustomLocation;
  CustomEdit.Parent := Page.Surface;
  CustomEdit.OnChange := @CustomEditChange;
  CustomEdit.OnClick := @CustomEditChange;
  CustomEdit.Text := CustomDir;
  CustomEdit.Top := Top;
  CustomEdit.Left := CustomRadio.Width;
  CustomEdit.Width := CustomBrowse.Left - 8 - CustomRadio.Width;
  Note := TLabel.Create(Page);
  Note.Visible := UseCustomLocation;
  Note.Parent := Page.Surface;
  Note.AutoSize := False;
  Note.WordWrap := True;
  Note.Top := Top + CustomEdit.Height + 4;
  Note.Left := CustomRadio.Width + 8;
  Note.Width := CustomEdit.Width - 16;
  Note.Height := Page.SurfaceHeight - Note.Top;
  Note.Caption := 'NOTE: Be sure to use a folder that is on the PYTHONPATH.';
end; { InitializeWizard }

function InitializeSetup(): Boolean;
var
  Key: String;
begin
  Key := 'Software\\Python\\PythonCore\\' + PythonVersion + '\\InstallPath';
  if not RegQueryStringValue(HKEY_CURRENT_USER, Key, '', PythonBaseDir) then
    RegQueryStringValue(HKEY_LOCAL_MACHINE, Key, '', PythonBaseDir);

  if (PythonBaseDir <> '') then
  begin
    PythonBaseDir := RemoveBackslashUnlessRoot(PythonBaseDir);
    if (CompareStr(PythonVersion, '2.2') >= 0) then
      PythonDir := PythonBaseDir + '\\Lib\\site-packages';
  end
  else
    PythonDir := PythonBaseDir;

  Key := Key + '\\InstallGroup';
  if not RegQueryStringValue(HKEY_CURRENT_USER, Key, '', PythonGroup) then
    RegQueryStringValue(HKEY_LOCAL_MACHINE, Key, '', PythonGroup);

  PythonGroup := AddBackslash(PythonGroup) + AppName;

  InstallDir := PythonDir;
  CustomDir := '';

  Result := True;
end; { InitializeSetup }

function NextButtonClick(CurPage: Integer): Boolean;
begin
  if CurPage = CustomPage then
  begin
    { Save the selection into InstallDir }
    if CustomRadio.Checked then
    begin
      InstallDir := RemoveBackslashUnlessRoot(CustomEdit.Text);
      CustomDir := InstallDir;
    end
    else
      InstallDir := PythonDir;
  end
  Result := True;
end; { NextButtonClick }
"""

class Section(object):
    section_name = None
    required_parameters = None
    optional_parameters = ['Languages', 'MinVersion', 'OnlyBelowVersion',
                           'BeforeInstall', 'AfterInstall']

    def __init__(self):
        assert self.section_name is not None, \
            "'section_name' must be defined"
        assert self.required_parameters is not None, \
            "'required_parameters' must be defined"
        self.entries = []

    def addEntry(self, **parameters):
        entry = []
        # Add the required parameters
        for parameter in self.required_parameters:
            try:
                value = parameters[parameter]
            except KeyError:
                raise DistutilsInternalError(
                    "missing required parameter '%s'" % parameter)
            else:
                del parameters[parameter]
            entry.append('%s: %s' % (parameter, value))
        # Add any optional parameters.
        for parameter in self.optional_parameters:
            if parameter in parameters:
                entry.append('%s: %s' % (parameter, parameters[parameter]))
                del parameters[parameter]
        # Any remaining parameters are errors.
        for parameter in parameters:
            raise DistutilsInternalError(
                "unsupported parameter '%s'" % parameter)
        # Create the entry string and store it.
        self.entries.append('; '.join(entry))
        return

class DirsSection(Section):
    section_name = 'Dirs'
    required_parameters = ['Name']
    optional_parameters = Section.optional_parameters + [
        'Attribs', 'Permissions', 'Flags']

class FilesSection(Section):
    section_name = 'Files'
    required_parameters = ['Source', 'DestDir']
    optional_parameters = Section.optional_parameters + [
        'DestName', 'Excludes', 'CopyMode', 'Attribs', 'Permissions',
        'FontInstall', 'Flags']

class IconsSection(Section):
    section_name = 'Icons'
    required_parameters = ['Name', 'Filename']
    optional_parameters = Section.optional_parameters + [
        'Parameters', 'WorkingDir', 'HotKey', 'Comment', 'IconFilename',
        'IconIndex', 'Flags']

class RunSection(Section):
    section_name = 'Run'
    required_parameters = ['Filename']
    optional_parameters = Section.optional_parameters + [
        'Description', 'Parameters', 'WorkingDir', 'StatusMsg', 'RunOnceId',
        'Flags']

class UninstallDeleteSection(Section):
    section_name = 'UninstallDelete'
    required_parameters = ['Type', 'Name']

class Component:
    section_mapping = {
        'Dirs' : DirsSection,
        'Files' : FilesSection,
        'Icons' : IconsSection,
        'Run' : RunSection,
        'UninstallDelete' : UninstallDeleteSection,
        }

    def __init__(self, name, description, types):
        self.name = name
        self.description = description
        self.types = types
        self.sections = {}

    def getEntry(self):
        return 'Name: "%s"; Description: "%s"; Types: %s' % (
            self.name, self.description, self.types)

    def hasEntries(self):
        for section in self.sections.itervalues():
            if section.entries:
                return True
        return False

    def getSection(self, name):
        if name not in self.sections:
            try:
                section_class = self.section_mapping[name]
            except KeyError:
                raise DistutilsInternalError("unknown section '%s'" % name)
            self.sections[name] = section_class()
        return self.sections[name]

    def getSectionEntries(self, name):
        return [ '%s; Components: %s' %(entry, self.name)
                 for entry in self.getSection(name).entries ]

class BDistInno(Command):

    command_name = 'bdist_inno'

    description = "create an executable installer for MS Windows"

    user_options = [('bdist-dir=', None,
                     "temporary directory for creating the distribution"),
                    ('keep-temp', 'k',
                     "keep the pseudo-installation tree around after " +
                     "creating the distribution archive"),
                    ('dist-dir=', 'd',
                     "directory to put final built distributions in"),
                    ('skip-build', None,
                     "skip rebuilding everything (for testing/debugging)"),
                   ]

    boolean_options = ['keep-temp', 'skip-build']

    def initialize_options(self):
        self.bdist_dir = None
        self.keep_temp = None
        self.dist_dir = None
        self.skip_build = None
        return

    def finalize_options(self):
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'inno')

        self.set_undefined_options('bdist',
                                   ('keep_temp', 'keep_temp'),
                                   ('dist_dir', 'dist_dir'),
                                   ('skip_build', 'skip_build'))

        self.license_file = self.distribution.license_file
        if self.license_file:
            self.license_file = util.convert_path(self.license_file)
        return

    def run(self):
        if sys.platform != 'win32':
            raise DistutilsPlatformError("InnoSetup distributions must be"
                                         " created on a Windows platform")

        if not self.skip_build:
            self.run_command('build')

        self.mkpath(self.bdist_dir)

        config = self.reinitialize_command('config')
        config.cache_filename = None
        config.prefix = 'PREFIX'
        config.ensure_finalized()

        install = self.reinitialize_command('install')
        install.root = self.bdist_dir
        install.skip_build = self.skip_build
        install.install_lib = 'PYTHONLIB'

        # Always include "compiled" py-files
        install.compile = 1
        install.optimize = 1

        # don't warn about installing into a directory not in sys.path
        install.warn_dir = False

        # always include documentation
        install.with_docs = True

        self.announce("installing to %s" % self.bdist_dir, 2)
        install.ensure_finalized()
        install.run()

        if self.license_file:
            self.copy_file(self.license_file, self.bdist_dir)

        # create the InnoSetup script
        iss_file = self.build_iss_file()
        iss_path = os.path.join(self.bdist_dir,
                                '%s.iss' % self.distribution.get_name())
        self.announce("writing %r" % iss_path)
        if not self.dry_run:
            f = open(iss_path, "w")
            f.write(iss_file)
            f.close()

        # build distribution using the Inno Setup 5 Command-Line Compiler
        self.announce("creating Inno Setup", 2) # log.info
        compiler = 'iscc.exe'
        if _can_read_reg:
            try:
                key = RegOpenKeyEx(HKEY_LOCAL_MACHINE,
                                   'SOFTWARE\\Microsoft\\Windows\\'
                                   'CurrentVersion\\Uninstall\\'
                                   'Inno Setup 5_is1')
                install_dir = RegQueryValueEx(key, 'InstallLocation')[0]
            except RegError:
                pass
            else:
                compiler = os.path.join(install_dir, compiler)
        self.spawn([compiler, iss_path])

        if not self.keep_temp:
            remove_tree(self.bdist_dir, self.verbose, self.dry_run)
        return

    def build_iss_file(self):
        """Generate the text of an InnoSetup iss file and return it as a
        list of strings (one per line).
        """
        # [Icons]
        filespec = 'Source: "%s"; DestDir: "%s"; Components: %s'
        dirspec = 'Name: "%s"; Components: %s'
        uninstallspec = 'Type: files; Name: "%s"'
        iconspec = 'Name: "%s"; Filename: "%s"; Components: %s'
        runspec = ('Description: "%s"; Filename: "%s"; Components: %s; '
                   'Flags: %s')

        main_component = Component('Main',
                                   self.distribution.get_name() + ' Library',
                                   'full compact custom')
        docs_component = Component('Main\\Documentation', 'Documentation',
                                   'full')
        test_component = Component('Main\\Testsuite', 'Test suite', 'full')

        install = self.get_finalized_command('install')
        for command_name in install.get_sub_commands():
            command = self.get_finalized_command(command_name)
            # Get the mutated outputs split by type.
            dirs, files, uninstall = self._mutate_outputs(command)
            # Perform any command-specific processing
            if command_name == 'install_html':
                component = docs_component
                for document in command.documents:
                    flags = getattr(document, 'flags', ())
                    if 'postinstall' in flags:
                        section = component.getSection('Run')
                        filename = command.get_output_filename(document)
                        filename = self._mutate_filename(filename)[1]
                        section.addEntry(
                            Description='"View %s"' % document.title,
                            Filename='"%s"' % filename,
                            Flags='postinstall shellexec skipifsilent')
                    if 'shortcut' in flags:
                        section = component.getSection('Icons')
                        filename = command.get_output_filename(document)
                        filename = self._mutate_filename(filename)[1]
                        section.addEntry(
                            Name='"{group}\\%s"' % document.title,
                            Filename='"%s"' % filename)
            elif command_name == 'install_text':
                component = docs_component
            elif command_name == 'install_devel':
                component = test_component
            elif command_name == 'install_config':
                component = main_component
                section = component.getSection('Files')
                source, dest = self._mutate_filename(command.config_filename)
                section.addEntry(Source='"%s"' % source,
                                 DestDir='"%s"' % os.path.dirname(dest),
                                 AfterInstall="MutateConfigFile('%s')" % dest)
                # The only output *should* be the config filename
                assert len(files) == 1
                files = ()
            else:
                component = main_component

            if dirs:
                section = component.getSection('Dirs')
                for name in dirs:
                    section.addEntry(Name='"%s"' % name)
            if files:
                section = component.getSection('Files')
                for source, destdir in files:
                    section.addEntry(Source='"%s"' % source,
                                     DestDir='"%s"' % destdir)
            if uninstall:
                section = component.getSection('UninstallDelete')
                for name in uninstall:
                    section.addEntry(Type='files',
                                     Name='"%s"' % name)

        components = []
        sections = {}
        for component in (main_component, docs_component, test_component):
            has_entries = False
            for section in component.sections:
                entries = component.getSectionEntries(section)
                if entries:
                    has_entries = True
                    if section not in sections:
                        sections[section] = ['[%s]' % section]
                    sections[section].extend(entries)
            if has_entries:
                components.append(component.getEntry())
        components = '\n'.join(components)

        for name in sections:
            sections[name] = '\n'.join(sections[name])
        sections = '\n'.join(sections.values())

        uninstall_dir = os.path.join(install.install_localstate, 'Uninstall')
        _, uninstall_dir = self._mutate_filename(uninstall_dir)
        subst = {
            'output-dir' : os.path.abspath(self.dist_dir),
            'name' : self.distribution.get_name(),
            'version' : self.distribution.get_version(),
            'publisher' : self.distribution.get_author(),
            'publisher-url' : self.distribution.get_author_email(),
            'support-url' : self.distribution.get_url(),
            'uninstall-dir' : uninstall_dir,
            'license-file' : os.path.basename(self.license_file or ''),
            'target-version' : sys.version[:3],
            'custom-page' : self.license_file and 'wpLicense' or 'wpWelcome',
            'components' : components,
            'sections' : sections,
            }

        return ISCC_TEMPLATE % subst

    def _mutate_filename(self, filename):
        # Strip the bdist_dir from the filename as the files will be
        # relative to the setup script which is in bdist_dir.  This
        # is to make the setup script more readable.
        source = filename[len(self.bdist_dir) + len(os.sep):]

        # Translate the filename to what is used in the setup script
        if source.startswith('PREFIX'):
            dest = '{code:GetPythonDir}' + source[6:]
        elif source.startswith('PYTHONLIB'):
            dest = '{code:GetInstallDir}' + source[9:]
        else:
            raise ValueError('bad filename: ' + filename)

        return source, dest

    def _mutate_outputs(self, command):
        dirs = []
        files = []
        uninstall = []
        for filename in command.get_outputs():
            try:
                source, dest = self._mutate_filename(filename)
            except ValueError:
                raise DistutilsInternalError, \
                    'bad filename from %s: %s' % (command.get_command_name(),
                                                  filename)
            if os.path.isdir(filename):
                # An empty directory
                dirs.append(dest)
            else:
                files.append((source, os.path.dirname(dest)))
                # Add uninstall entries for possible bytecode files
                for extension in PY_SOURCE_EXTS:
                    if dest.endswith(extension):
                        barename = dest[:-len(extension)]
                        uninstall.append(barename + '.pyc')
                        uninstall.append(barename + '.pyo')
        return dirs, files, uninstall
