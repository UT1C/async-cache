import unittest

from . import cases


suite = unittest.TestSuite(
    unittest.defaultTestLoader.loadTestsFromTestCase(case)
    for case in cases
)
runner = unittest.TextTestRunner()
runner.run(suite)
