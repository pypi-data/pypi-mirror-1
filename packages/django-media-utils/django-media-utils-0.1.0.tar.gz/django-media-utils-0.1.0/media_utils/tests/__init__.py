def suite():
    from unittest import TestSuite, TestLoader

    suite = TestSuite()
    import test_cases
    suite.addTest(TestLoader().loadTestsFromModule(test_cases))
    return suite
