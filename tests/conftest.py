import pytest
import os
import sys


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    
if project_root not in sys.path:
    sys.path.insert(0, project_root)

