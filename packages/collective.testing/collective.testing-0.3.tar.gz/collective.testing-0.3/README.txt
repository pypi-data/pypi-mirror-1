====================
 collective.testing
====================

Overview
--------

general package for testing and debugging aids for CMF, Plone, Zope2 and Zope3

 * includes a layer for ZCML integratin testing

 * zcml for a default page for test objects (useful in zope 2.9)

 * postmortem helper:

    >>> from collective.testing.debug import autopsy
    >>> @autopsy
    >>> def problem_func():
    ...     raise Exception('Trouble!')

 * some profiling tools

 * some logging and printing subscribers for zope.events

 * some fake response and request objects for zope

