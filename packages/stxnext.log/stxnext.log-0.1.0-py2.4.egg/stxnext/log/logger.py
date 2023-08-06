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

import os, os.path, time, traceback, StringIO, cgi
from pprint import pformat

class STXNextLogger(object):
    """
    STX Next logger
                     
    @author: Wojciech Lichota <wojciech.lichota[at]stxnext.pl>
    """
    
    def __init__(self, filename=None, name=None):
        """
        Constructor.
        """
        if filename is None:
            filename = 'stxnextlogger.log'
        self.setFilename(filename)
        
        self.name = name
        self._entries = []
    
    def setName(self, name):
        """
        Set name of log.
        """
        self.name = name        
    
    def setFilename(self, filename):
        """
        Set filename of log file.
        """
        try:
            instance_path = INSTANCE_HOME
        except NameError:
            instance_path = os.environ.get('INSTANCE_HOME', '.')
        
        if os.path.isabs(filename):
            self.filename = filename
        else:
            self.filename = os.path.join(instance_path,'log', filename)
    
    def clear(self):
        """
        clear log (doesn't clear log file, only entries avialable via getLoggedText
        """
        self._entries = []
        
    def timestamp(self):
        """
        return timestamp (YYYYMMDDhhmmss), e.g. 20070121145933
        """
        return time.strftime('%Y%m%d%H%M%S')
        
    def _logEntry(self, text, timestamp=None):
        """
        return formated log entry, e.g. [20070121145933] log message
        """
        if timestamp is None:
            timestamp = self.timestamp()
        
        if self.name:
            text = text.strip().replace('\n', '\n'+' '*(19+len(self.name)))
            return '[%s] %s: %s' % (timestamp, self.name, text)
        
        text = text.strip().replace('\n', '\n'+' '*17)
        return '[%s] %s' % (timestamp, text)        
        
    def _saveToLogFile(self, text):
        """
        save given text to log file
        """
        f = open(self.filename, 'a')
        f.write(self._logEntry(text))
        f.write('\n')
        f.close()
        
    def append(self, text, printit=False):
        """
        append text to log
        """
        if not isinstance(text, basestring):
            text = str(text)
            
        self._entries.append((self.timestamp(), text))
        self._saveToLogFile(text)
        if printit:
            print self._logEntry(text)
    
    def log_exc(self, comment=None):
        """
        append traceback to log
        """
        tb = StringIO.StringIO()
        traceback.print_exc(file=tb)
        
        if comment is not None:
            error = '%s\n\n%s' % (comment, tb.getvalue())
        else:
            error = tb.getvalue()
            
        self.append(error, printit=True)
        
    def log_args(self, *args, **kwargs):
        """
        append args and kwargs to log
        """
        result = "args:\n%s\n\nkwargs:\n%s" % (pformat(args), pformat(kwargs))
        self.append(result, printit=True)
        
    def getLoggedText(self):
        """
        return logged text
        """
        result = []
        for timestamp, text in self._entries:
            result.append(self._logEntry(text, timestamp))
        
        return '\n'.join(result)
    
    def getLoggedTextAsHtml(self):
        """
        return logged text as html
        """
        return '<pre>%s</pre>' % cgi.escape(self.getLoggedText())
        
    __call__ = append
    