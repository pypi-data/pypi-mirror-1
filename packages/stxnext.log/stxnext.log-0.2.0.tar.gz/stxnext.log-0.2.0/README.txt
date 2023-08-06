===========
stxnext.log
===========

Overview
========

This is logger written from scratch. It offers few conveniences that
helps in logging (e.g.: logging exceptions). It can also log some
messages from ZPT (Zope Page Templates). 
  
Using
=====

stxnext.log can be opened by used in python code::

    >>> from stxnext.log import log
    >>> log('log <this> text')
    >>> log('log another text', printit=True) #doctest:+ELLIPSIS
    [...] log another text
    >>> try:
    ...     1/0
    ... except ZeroDivisionError, e:
    ...     log.log_exc(e)
    ...
    >>> log.getLoggedTextAsHtml() #doctest:+ELLIPSIS, +NORMALIZE_WHITESPACE
    <pre>[...] log &lt;this&gt; text...</pre>
  
stxnext.log can be also used in ZPT templates::

    <tal:block tal:define="log context/@@STXNextLogger;
                           result python: log.setFilename('logger_filename.log');
                           result python: log.setName('logger name');">
        <tal:block tal:define="result python: log('log this text')" />
        <tal:block tal:define="result python: log('log another text', printit=True)" />  
        <pre tal:replace="structure log/getLoggedTextAsHtml" />
    </tal:block>


Installation
============

Alternatively, if you are using zc.buildout to manage your project, 
you can do this:

* Add ``stxnext.log`` to the list of eggs to install, e.g.::

    [buildout]
    ...
    eggs =
        ...
        stxnext.log
        
* If you're using plone.recipe.zope2instance recipe to manage your 
  instance add this lines to install a ZCML slug::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zcml =
        ...
        stxnext.log
      
* If you're using zc.zope3recipes:application recipe to manage your 
  instance add this lines to install a ZCML slug::

    [instance]
    recipe = zc.zope3recipes:application
    ...
    site.zcml =
        ...
        <include package="stxnext.log" />       
      
* Re-run buildout, e.g. with::

    $ ./bin/buildout
        
You can skip the ZCML slug if you are going to explicitly include the package
from another package's configure.zcml file.


References
==========

* `stxnext.log home page`_
* `stxnext.log at pypi`_

.. _stxnext.log home page: http://stxnext.pl/open-source/stxnext.log
.. _stxnext.log at pypi: http://pypi.python.org/pypi/stxnext.log/


Author & Contact
================

:Author: Wojciech Lichota <``wojciech.lichota[at]stxnext.pl``>

.. image:: http://stxnext.pl/open-source/files/stx-next-logo

**STX Next** Sp. z o.o.

http://stxnext.pl

info@stxnext.pl
