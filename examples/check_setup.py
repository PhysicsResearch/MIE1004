"""Check that the mie1004 environment is set up correctly.

Run it in VS Code with the "Run Python File" button, or from a terminal:

    python check_setup.py

The first line should be a path that contains "mie1004".
If you get a ModuleNotFoundError, the wrong environment is selected.
"""

import sys

import matplotlib
import numpy
import pandas
import pydicom

print(sys.executable)
print("pydicom", pydicom.__version__)
print("numpy", numpy.__version__)
print("pandas", pandas.__version__)
print("matplotlib", matplotlib.__version__)
