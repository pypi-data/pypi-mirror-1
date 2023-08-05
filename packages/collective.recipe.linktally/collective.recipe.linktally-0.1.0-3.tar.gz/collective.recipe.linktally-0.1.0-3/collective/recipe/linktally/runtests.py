def test_suite():
    import unittest
    import doctest

    return unittest.TestSuite((
        doctest.DocTestSuite('collective.recipe.linktally',
                             optionflags=doctest.ELLIPSIS)
        ))

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite', argv=[sys.argv[0]] + args)
