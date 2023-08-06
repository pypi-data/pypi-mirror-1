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

try:
    from ZPublisher.HTTPRequest import _filterPasswordFields, hide_key
    IN_ZOPE = True
except ImportError:
    IN_ZOPE = False
    
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
        
        ## if instance use buildout write log in correct folder
        if instance_path.endswith('parts/instance'):
            instance_path = instance_path.replace('parts/instance', 'var')
        
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
        entry = self._logEntry(text)
        if isinstance(entry, unicode):
            entry = entry.encode('ascii', 'replace')
            
        f = open(self.filename, 'a')
        f.write(entry)
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
        
    def log_request(self, req):
        """
        append data from zope's request to log
        """
        if not IN_ZOPE:
            self.append(repr(req))
        
        result = {
            'form': {},
            'cookies': {},
            'lazy items': {},
            'other': {},
            'environ': {}
            }
        
        for k,v in _filterPasswordFields(req.form.items()):
            result['form'][k] = repr(v)
            
        for k,v in _filterPasswordFields(req.cookies.items()):
            result['cookies'][k] = repr(v)
            
        for k,v in _filterPasswordFields(req._lazies.items()):
            result['lazy items'][k] = repr(v)
            
        for k,v in _filterPasswordFields(req.other.items()):
            if k in ('PARENTS','RESPONSE'): continue
            result['other'][k] = repr(v)

        for n in "0123456789":
            key = "URL%s"%n
            try: result['other'][key] = req[key]
            except KeyError: pass
            
        for n in "0123456789":
            key = "BASE%s"%n
            try: result['other'][key] = req[key]
            except KeyError: pass

        for k,v in req.environ.items():
            if not hide_key(k):
                result['environ'][k] = repr(v)
        
        result = pformat(result)
        self.append(result, printit=False)
        
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
