Overview
========

The zc.testbrowser package provides web user agents (browsers) with
programmatic interfaces designed to be used for testing web applications,
especially in conjunction with doctests.

There are currently two type of testbrowser provided.  One for accessing web
sites via HTTP (zc.testbrowser.browser) and one that controls a Firefox web
browser (zc.testbrowser.real).  All flavors of testbrowser have the same API.

This project originates in the Zope 3 community, but is not Zope-specific (the
zc namespace package stands for "Zope Corporation").


Changes
=======

1.0a1 (2007-09-28)
------------------

First release under new name (non Zope-specific code extracted from
zope.testbrowser)
