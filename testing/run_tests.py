"""
Runs all tests.
"""
import unittest

loader = unittest.TestLoader()
suite = loader.discover("")

runner = unittest.TextTestRunner()
print("All unit tests are going to be run.")
runner.run(suite)