# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 STX Next Sp. z o.o. and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import sys, re, os
from pdb import Pdb

class STXNextPdb(Pdb):
    """
    Improved python debugger.
    
    @author: Wojciech Lichota <wojciech.lichota[at]stxnext.pl>
    """
    
    def __init__(self):
        Pdb.__init__(self)
        
        #self.prompt = '(\033[01;34mSTX Next\033[00m pdb) '
        self.prompt = '(STX Next pdb) '
       
    def _getTerminalWidth(self):
        """
        Return estimated terminal width.
        see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440694
        """
        width = 0
        try:
            import struct, fcntl, termios
            s = struct.pack('HHHH', 0, 0, 0, 0)
            x = fcntl.ioctl(1, termios.TIOCGWINSZ, s)
            width = struct.unpack('HHHH', x)[1]
        except IOError:
            pass
        if width <= 0:
            try:
                width = int(os.environ['COLUMNS'])
            except:
                pass
        if width <= 0:
            width = 80
    
        return width

    def _variableDir(self, variable, filter):
        """
        Return nice formated output of dir function.
        """
        result = []
        
        pattern = re.compile('.*%s.*' % filter)
        elements = [i for i in dir(variable) if pattern.match(i)]
        
        width = self._getTerminalWidth()
        columns = width / 40 
        
        column_width = int(width/columns)
        column_height = len(elements)/columns + 1
        
        elements.extend(['']*(column_width*column_height-len(elements)))
                
        format = ' '.join(['%-' + str(column_width) + 's ']*(columns-1)+['%s '])
    
        columns_data = []
        for column_number in range(columns):
            slice_start = column_number * column_height
            slice_end  = column_number * column_height + column_height
            columns_data.append(elements[slice_start:slice_end])
        
        for i in range(column_height):
            args = [columns_data[j][i] for j in range(columns)]
            result.append(format % tuple(args))
            
        return '\n'.join(result)
    
    def do_dir(self, arg):
        args = arg.split()
        
        if len(args) > 0:
            try:
                variable = self._getval(args[0])
            except:
                return
        else:
            return self.help_dir()
        
        filter = ''
        if len(args) > 1:
            filter = args[1]
            
        colorize = True
        if len(args) > 2:
            colorize = args[2] != 'False'
        
        result = self._variableDir(variable, filter)
        if colorize:
            result = result.replace(filter, '\033[01;32m%s\033[00m' % filter)
        
        print result
        
    def help_dir(self):
        print 'dir variable [filter] [colorize]\nreplacement for dir(variable)'
   
    def _variableInfo(self, variable):
        """
        Return nice formated informations about variable.
        """
        def _shorten(text):
            text = str(text)
            width = self._getTerminalWidth() - 20
            if len(text) > width:
                return text[:width] + '...'
            return text
        
        kwargs = {'type': str(type(variable)),
                  'class': _shorten(str(getattr(variable, '__class__', ''))),
                  'id':   id(variable),
                  'str':  _shorten(str(variable)),
                  'repr': _shorten(repr(variable)),
                  'doc':  str(variable.__doc__),
                  }
        return """
type:        %(type)s
class:       %(class)s
id:          %(id)i
str:         %(str)s
repr:        %(repr)s
docstring:   %(doc)s
""" % kwargs

    def do_info(self, arg):
        args = arg.split()
        
        if len(args) == 0:
            return self.help_info()
        
        try:
            variable = self._getval(args[0])
        except:
            return
        
        print self._variableInfo(variable)
        
    def help_info(self):
        print 'info variable \ndetailed information about variable'
    
    def do_update_locals(self, arg):
        args = arg.strip().split()
        
        if len(args) > 0:
            try:
                cx = self._getval(args[0])
            except:
                cx = None
        else:
            try:
                cx = self._getval('self.context')
            except NameError:
                if 'context' in self.curframe.f_locals:
                    cx = self.curframe.f_locals['context']
                elif 'self' in self.curframe.f_locals:
                    cx = self.curframe.f_locals['self']
                else:
                    cx = None
        
        import sys, re, os
        try:
            from transaction import commit
            from AccessControl import getSecurityManager, Permissions
            
            from zope import schema
            from zope.component import getUtility, queryUtility, getAdapter, queryAdapter, getMultiAdapter, \
                                       queryMultiAdapter, getSiteManager, getGlobalSiteManager
            from zope.event import notify
            from zope.interface import implements, Interface, Attribute, providedBy, implementedBy, \
                                       alsoProvides, directlyProvides, noLongerProvides
            IN_ZOPE = True
        except ImportError:
            IN_ZOPE = False
        
        try:
            from Products.CMFPlone import utils
            from Products.CMFCore.utils import getToolByName
            IN_PLONE = True
        except ImportError:
            IN_PLONE = False

        TOOL_NAMES = ['portal_setup', 'MailHost', 'plone_utils', 'portal_actions', 'portal_catalog',
                      'portal_membership', 'portal_properties', 'portal_registration', 'portal_skins',
                      'portal_types', 'portal_url','portal_workflow', 'reference_catalog', 'uid_catalog',
                      'portal_languages']

        FUNCTION_NAMES = ['getSecurityManager', 'Permissions', 'schema', 'getUtility', 'queryUtility', 
                          'getAdapter', 'queryAdapter', 'getMultiAdapter', 'queryMultiAdapter', 
                          'getSiteManager', 'getGlobalSiteManager', 'notify', 'implements', 'Interface', 
                          'Attribute', 'providedBy', 'implementedBy', 'alsoProvides', 'directlyProvides', 
                          'noLongerProvides', 'commit', 'sys', 'os', 're']

        new_locals = {'cx' : cx}
        
        try:
            from stxnext.log.logger import STXNextLogger
            new_locals['log'] = STXNextLogger(name='STX Next pdb')
        except ImportError:
            pass

        if IN_PLONE and cx is not None:
            for tool_name in TOOL_NAMES:
                new_locals[tool_name] = getToolByName(cx, tool_name, default=None)
            
            new_locals['getToolByName'] = getToolByName
            if new_locals.get('portal_url'):
                new_locals['portal'] = new_locals['portal_url'].getPortalObject()

            if hasattr(cx, 'getSwordSubsiteRoot'):
                new_locals['subsite'] = cx.getSwordSubsiteRoot()             

        if IN_ZOPE:
            if hasattr(cx, 'REQUEST'):
                new_locals['req'] = cx.REQUEST
            elif hasattr(cx, 'request'):
                new_locals['req'] = cx.request
            elif 'REQUEST' in self.curframe.f_locals:
                new_locals['req'] = self.curframe.f_locals['REQUEST']
            elif 'request' in self.curframe.f_locals:
                new_locals['req'] = self.curframe.f_locals['request']   
                
            local_variables = locals()
            for function_name in FUNCTION_NAMES:
                new_locals[function_name] = local_variables[function_name]
        
        print 'New locals:'
        for name in sorted(new_locals.keys()):
            value = new_locals[name]
            if name not in self.curframe.f_locals and value is not None:
                print '    ' + name
                self.curframe.f_locals[name] = value
    
    do_ul = do_update_locals
        
    def help_update_locals(self):
        print 'update_locals [context]\n'
    
    def do_help(self, arg):
        if not arg:
            import zlib, base64
            logotyp =   'eJy1l7+OgzAMxvd7BZbbqm5XHapO6sArkCkD6sDSoRJSO/L2d3CE2LHj/MXdqo98PxwTO83wM33aaIav23c7NcNlGrNjX4Rb+sP' \
                        '+vf3zXt3UEjrz9xfG9UXW3x3hy82qQlzdV3UcgSH067vEaKEntsSOjGHP70ZigIVbFgRxALXBPlXBQCBnva0Nl7Ycl+leMwO+PD' \
                        'wYxwd1RLUeBkqUU7q7n45ZznmQ1LXsc6WfXgivhG4J3yGTIT+ADqbQTQovH33yY+jg9/uKkGv2fC2nw98zOuf4pCC5CspL6VzHL' \
                        'uiY+D6ldMRTWzsdTjkE5OXldP4cRqQc9r6D6NDI81QhOiSfRXkxHfLa5hyBTphvatPB/jT/F88ePe31rhwG356z6VDnfGKrriNo' \
                        'vt1X65gWUaFJdP7TmJJJ8p6VH0PHbKck9+asPp1/f3h5zAyaQgePcWwnlA4nZ+pSgnvLdMz0mR2BidK0m/gRNcFw3CrqZB3x3cJ' \
                        '0ktj5M856za45CdA2Ig62jQrX32SEZSnlpIC5a/HtHzeL2NDaPOXUo+Moz2EZQc8Y4ohNnUtxWnTs12kcfwGvxA8b'
    
            print zlib.decompress(base64.b64decode(logotyp)).strip()
            print
            print " "*26 + "Python Debugger improved by:"
            print " "*30 + "STX Next Sp. z o.o."
            print " "*31 + "http://stxnext.pl\033[00m"
            
        Pdb.do_help(self, arg)
            
    
# Simplified interface

def run(statement, globals=None, locals=None):
    STXNextPdb().run(statement, globals, locals)

def runeval(expression, globals=None, locals=None):
    return STXNextPdb().runeval(expression, globals, locals)

def runctx(statement, globals, locals):
    # B/W compatibility
    run(statement, globals, locals)

def runcall(*args, **kwds):
    return STXNextPdb().runcall(*args, **kwds)

def set_trace():
    STXNextPdb().set_trace(sys._getframe().f_back)

# Post-Mortem interface

def post_mortem(t):
    p = STXNextPdb()
    p.reset()
    while t.tb_next is not None:
        t = t.tb_next
    p.interaction(t.tb_frame, t)

def pm():
    post_mortem(sys.last_traceback)
    
    STXNextPdb().set_trace()
