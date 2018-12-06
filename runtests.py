import unittest
import os

import colour_runner.runner

from ion.files import get_dirname


loader = unittest.TestLoader()
start_dir = os.path.join(get_dirname(), 'tests')
suite = loader.discover(start_dir)
runner = colour_runner.runner.ColourTextTestRunner()
runner.run(suite)
