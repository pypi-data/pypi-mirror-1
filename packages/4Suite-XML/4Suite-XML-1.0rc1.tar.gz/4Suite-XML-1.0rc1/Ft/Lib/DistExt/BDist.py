import os
import sys
from distutils.command import bdist

from Ft.Lib.DistExt import Util

class BDist(bdist.bdist):
    """
    Extended 'bdist' command that adds support for InnoSetup Windows installers
    and Python Egg files.
    """

    command_name = 'bdist'

    default_format = bdist.bdist.default_format.copy()
    default_format['nt'] = 'inno'

    format_commands = bdist.bdist.format_commands + ['inno', 'egg']

    format_command = bdist.bdist.format_command.copy()
    format_command['inno'] = ('bdist_inno', 'Windows InnoSetup installer')
    format_command['egg'] = ('bdist_egg', 'Python Egg file')

    if sys.version < '2.3':
        user_options = bdist.bdist.user_options + [
            ('skip-build', None,
             "skip rebuilding everything (for testing/debugging)"),
            ]

        def initialize_options(self):
            bdist.bdist.initialize_options(self)
            self.skip_build = False
            return

    def finalize_options(self):
        self.set_undefined_options('config', ('plat_name', 'plat_name'))

        bdist.bdist.finalize_options(self)

        for format in self.formats:
            if format not in self.format_command:
                raise DistutilsOptionError("invalid format '%s'" % format)
        return

    sub_commands = []
    for format in format_commands:
        command, description = format_command[format]
        if command not in dict(sub_commands):
            sub_commands.append((command, lambda self: False))
