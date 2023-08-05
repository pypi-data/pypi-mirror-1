import doctest
flags = doctest.ELLIPSIS | doctest.REPORT_ONLY_FIRST_FAILURE
    
def test_suite():
    import collective.testing.debug as debug
    def debug_setup(self):
        debug._test = True
    
    def debug_teardown(self):
        debug._test = False

    unit_suite = doctest.DocTestSuite(module='collective.testing.debug',
                                      globs=dict(pdbator=debug.pdbator,
                                                 test_func=lambda : 1,
                                                 ),
                                      setUp=debug_setup,
                                      tearDown=debug_teardown,
                                      optionflags=flags)
    return unit_suite
