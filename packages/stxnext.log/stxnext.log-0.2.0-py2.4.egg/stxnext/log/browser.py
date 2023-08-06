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

from logger import STXNextLogger

try:
    from Products.Five import BrowserView
    IN_ZOPE = True
except ImportError:
    IN_ZOPE = False
    BrowserView = object

class STXNextLoggerView(BrowserView):
    """
    View class for STXNextLogger

    @author: Wojciech Lichota <wojciech.lichota[at]stxnext.pl>
    """
    def __call__(self):
        """
        Get STXNextLogger instance.
        
        @return: logger object
        @rtype: STXNextLogger
        
        <tal:block tal:define="log context/@@STXNextLogger;
                               result python: log.setFilename('logger_filename.log');
                               result python: log.setName('logger name');">
            <tal:block tal:define="result python: log('log this text')" />
            <tal:block tal:define="result python: log('log another text', printit=True)" />  
            <pre tal:replace="structure log/getLoggedTextAsHtml" />
        </tal:block>
        """
        return STXNextLogger()
     
