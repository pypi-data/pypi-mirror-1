#
#   PROGRAM:     Power Console
#   MODULE:      stdcmd.py
#   DESCRIPTION: Standard built-in commands
#
#  The contents of this file are subject to the Initial
#  Developer's Public License Version 1.0 (the "License");
#  you may not use this file except in compliance with the
#  License. You may obtain a copy of the License at
#  http://www.firebirdsql.org/index.php?op=doc&id=idpl
#
#  Software distributed under the License is distributed AS IS,
#  WITHOUT WARRANTY OF ANY KIND, either express or implied.
#  See the License for the specific language governing rights
#  and limitations under the License.
#
#  The Original Code was created by Pavel Cisar
#
#  Copyright (c) 2006 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

#---Classes---#000000#FFFFFF---------------------------------------------------

import pkg_resources
import pyparsing as pp
from pwc.base import *
from inspect import getdoc, currentframe
import os.path
import sys
import types

class cmdList(Command):
    """List information about object or sequence of objects.

    Use ObjectListDisplay with context 'list'.
    """

    def __init__(self,controller):
        super(cmdList,self).__init__(controller)
        self.display = controller.ui_provider.getListDisplay('list')
        # Grammar
        self.keyList = pp.CaselessKeyword('list')
        # LIST [expr]
        self.cmdList = self.keyList.setResultsName('cmd') + \
            self.EXPR.setResultsName('expr')
        self.cmdList.setParseAction(self._compile)

    def _getGrammar(self):
        return self.cmdList
    def _getCmdKeyword(self):
        return self.keyList

    def execute(self,expr):
        """List information about object or sequence of objects.
        
        Syntax: LIST <expression>

        'expression' has to be object or iterable containing objects to list.
        """

        if not isiterable(expr):
            expr = [expr]
        self.display.writeList(expr)


class cmdRun(Command):
    """Run script as if commands had been entered at the console."""

    def __init__(self,controller):
        super(cmdRun,self).__init__(controller)
        # Grammar
        self.keyRun = pp.CaselessKeyword('run')
        # RUN [arg]
        self.cmdRun = self.keyRun.setResultsName('cmd') + \
            self.EXPR.setResultsName('expr')
        self.cmdRun.setParseAction(self._compile)

    def _getGrammar(self):
        return self.cmdRun
    def _getCmdKeyword(self):
        return self.keyRun

    def execute(self,expr):
        """Execute sequence of commands as if they were typed into the shell.
        
        Syntax: RUN <expression> 
        
        'expression' has to be a script filename or iterable containing lines 
        to execute.
        """

        buffer = []
        lineno = 0
        script = expr

        isFile = os.path.exists(script)
        if isFile:
            source = script
            commands = file(script,"rU")
        else:
            source = str(type(script))
            try:
                commands = eval(script,self._getUserNamespace(),
                    self._getContextLocals())
            except Exception, e:
                raise pcError(str(e))
            if not isiterable(commands):
                raise pcError('File name or iterable object expected.')

        try:
            for command in commands:
                if not isinstance(command,types.StringTypes):
                    raise pcError('String expected, but %s found.' % \
                        str(type(command)))
                buffer.append(command.rstrip())
                more = self.controller.runsource("\n".join(buffer), source,
                    line_offset=lineno)
                lineno += 1
                if not more:
                    buffer = []
        finally:
            if isFile:
                commands.close()


class cmdHelp(Command):
    """Show list of help topics or help text for requested topic.

    Uses LineDisplay with context 'help'.
    """

    ruler = '='
    doc_leader = """To get help about specific topic, PowerConsole command
or Python object/function/expression, type help <topic>.
"""
    doc_header = "PowerConsole commands:"
    misc_header = "Miscellaneous help topics:"
    nohelp = "*** No help on %s"
    
    def __init__(self,controller):
        super(cmdHelp,self).__init__(controller)
        import __builtin__
        self._help = __builtin__.help
        __builtin__.help = self.execute
        self.display = controller.ui_provider.getLineDisplay('help')
        # Find and instantiate help topics
        self.help_providers = []
        for provider in pkg_resources.iter_entry_points("powerconsole.help_providers"):
            try:
                obj = provider.load()(self._help)
            except:
                ## ToDo: Handle exceptions in provider initialization
                raise
            else:
                self.help_providers.append(obj)
        # Grammar
        self.keyHelp = pp.CaselessKeyword('help')
        # HELP [arg]
        self.cmdHelp = self.keyHelp.setResultsName('cmd') + \
            pp.Optional(self.ARG.setResultsName('arg'))
        self.cmdHelp.setParseAction(self._compile)

    def __findProvider(self, topic):
        for provider in self.help_providers:
            if provider.canHandle(topic): 
                return provider
        return None
    def __showHelp(self,help):
        if callable(help):
            help()
        elif help:
            self.display.writeLine(help)
    def __printTopics(self, header, cmds, cmdlen, maxcol):
        if cmds:
            self.display.writeLine("%s" % str(header))
            if self.ruler:
                self.display.writeLine("%s" % str(self.ruler * len(header)))
            for line in columnize(cmds, maxcol-1):
                self.display.writeLine(line)
            self.display.writeLine()

    def _getGrammar(self):
        return self.cmdHelp
    def _getCmdKeyword(self):
        return self.keyHelp

    def execute(self,arg=''):
        """Show list of help topics or help text for requested topic.
        
        Without argument, it will list all internal commands that have help 
        text and all registered special help topics. With argument, it will try 
        to show help for topic or object specified by argument.

        Syntax: HELP [<argument>]
        """

        self.display.open()
        try:
            if arg:
                if self.controller.commands.has_key(arg) and (
                    hasattr(self.controller.commands[arg], 'getHelp') or 
                    getdoc(getattr(self.controller.commands[arg], 'execute'))):
                    # Help for PowerConsole command
                    cmd = self.controller.commands[arg]
                    try:
                        self.__showHelp(getattr(cmd, 'getHelp'))
                    except AttributeError:
                        # There is not separate help provider function
                        # we'll look for docstring in 'execute' method
                        doc = getdoc(getattr(cmd, 'execute'))
                        if doc:
                            self.__showHelp(str(doc))
                        else:
                            self.__showHelp("%s" % str(self.nohelp % arg))
                else:
                    # It's not a PowerConsole command or it doesn' directly
                    # provide documentation, we'll look for help provider
                    provider = self.__findProvider(arg)
                    if provider:
                        self.__showHelp(provider.getHelp(arg))
                    else:
                        # No provider found, we'll show help for Python object/topic
                        try:
                            self._help(eval(arg,self._getUserNamespace(),self._getContextLocals()))
                        except Exception:
                            self.__showHelp("%s" % str(self.nohelp % arg))
            else:
                # Show list of documented internal commands and help topics
                cmds_doc = []
                for cmd in self.controller.commands.values():
                    if hasattr(cmd, 'getHelp') or getdoc(getattr(cmd, 'execute')):
                        cmds_doc.append(cmd.getName())
                helptopics = []
                for provider in self.help_providers:
                    helptopics.extend(provider.getTopics())
                cmds_doc.sort()
                helptopics.sort()
                self.display.writeLine("%s" % str(self.doc_leader))
                self.__printTopics(self.doc_header, cmds_doc, 15,80)
                self.__printTopics(self.misc_header, helptopics, 15,80)
        finally:
            self.display.close()
    
class helpBuiltin(HelpProvider):
    """Help Provider for built-in commands and other general topics"""

    help_terminator = """Help on SET TERM
    """

    topics = [x[len(HELP_PREFIX):] for x in dir() if x.startswith(HELP_PREFIX)]
    
    def canHandle(self,topic):
        """Return True if 'topic' is 'terminator'."""

        return topic in self.topics

    def getTopics(self):
        """Return list of topics handled by provider."""

        return self.topics

    def getHelp(self, topic):
        print "Help on topic '%s'" % topic

class helpPython(HelpProvider):
    """Help Provider that give access to standard Python help system."""

    def canHandle(self,topic):
        """Return True if 'topic' starts with 'python'."""

        return topic.startswith('python')

    def getTopics(self):
        """Return list of topics handled by provider."""

        return ['python']

    def getHelp(self, topic):
        """Return python help for 'topic'."""

        topic = topic[6:].strip()
        if topic != '':
            self._help(topic)
        else:
            self._help()


##class cmdXXX(Command):
##    """description of command XXX"""
##
##    def __init__(self,controller):
##        super(cmdXXX,self).__init__(controller)
##        # Grammar
##        self.keyXXX = pp.CaselessKeyword('XXX')
##        # XXX [arg]
##        self.cmdXXX = self.keyXXX.setResultsName('cmd')
##        self.cmdXXX.setParseAction(self._compile)
##
##    def _getGrammar(self):
##        return self.cmdXXX
##    def _getCmdKeyword(self):
##        return self.keyXXX
##
##    def execute(self,script):
##        """Help text for command XXX.
##
##        Syntax: XXX
##
##        """
##
##        print "Command %s not implemented" % self.__class__.__name__
##
