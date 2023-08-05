########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Lib/_4xupdate.py,v 1.16 2006/08/11 15:39:13 jkloth Exp $
"""
Implementation of '4xupdate' command
(functions defined here are used by the Ft.Lib.CommandLine framework)

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys, cStringIO

from Ft import GetConfigVars
from Ft.Lib import UriException, CloseStream
from Ft.Lib.CommandLine.CommandLineUtil import SourceArgToInputSource
from Ft.Xml import Domlette, XUpdate
from Ft.Xml.InputSource import DefaultFactory

def Run(options, args):

    out_file = options.has_key('outfile') \
               and open(options['outfile'], 'wb') or sys.stdout

    source_arg = args['source-uri']
    xupdate_arg = args['xupdate-uri']

    try:
        source_isrc = SourceArgToInputSource(source_arg, factory=DefaultFactory)
        xupdate_isrc = SourceArgToInputSource(xupdate_arg, factory=DefaultFactory)
    except Exception, e:
        sys.stderr.write(str(e)+'\n')
        sys.stderr.flush()
        return

    try:
        xml_reader = Domlette.NonvalidatingReader
        xupdate_reader = XUpdate.Reader()
        processor = XUpdate.Processor()

        source_doc = xml_reader.parse(source_isrc)
        CloseStream(source_isrc, quiet=True)
        compiled_xupdate = xupdate_reader.fromSrc(xupdate_isrc)
        CloseStream(xupdate_isrc, quiet=True)

        processor.execute(source_doc, compiled_xupdate)

        Domlette.Print(source_doc, stream=out_file)

    except Exception, e:
        import traceback
        traceback.print_exc(1000, sys.stderr)
        raise

    try:
        if out_file.isatty():
            out_file.flush()
            sys.stderr.write('\n')
        else:
            out_file.close()
    except (IOError, ValueError):
        pass

    return


from Ft.Lib.CommandLine import Options, CommandLineApp, Arguments, Command

class XUpdateCommandLineApp(CommandLineApp.CommandLineApp):

    project_name, project_version, project_url = \
        GetConfigVars('NAME', 'VERSION', 'URL')

    def __init__(self):
        CommandLineApp.CommandLineApp.__init__(
            self,
            '4xupdate',
            'command-line tool for performing XUpdates on XML documents',
            """4XUpdate command-line application""",
            [],
            ourOptions = Options.Options([
                Options.Option('o',
                               'outfile=FILE',
                               'Write the result to the given output file',
                               ),
                ]),

            enableShowCommands = 0
            )

        self.function = Run
        self.arguments = [
            Arguments.RequiredArgument('source-uri',
                                       'The URI of the XML document to which to apply the XUpdate, or "-" to indicate standard input.',
                                       str),
            Arguments.RequiredArgument('xupdate-uri',
                                       'The URI of the XML document containing XUpdate instructions, or "-" to indicate standard input.',
                                       str),
            ]

    def validate_arguments(self, args):
        msg = ''
        if len(args) < 2:
            msg = 'A source URI argument and an XUpdate URI argument are required.'
        elif len(filter(lambda arg: arg=='-', args)) > 1:
                msg = 'Standard input may be used for only 1 document.'
        if msg:
            raise SystemExit('%s\nSee "4xupdate -h" for usage info.' % msg)
        else:
            return Command.Command.validate_arguments(self, args)
