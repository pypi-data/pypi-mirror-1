import sys
import os
# Force the path:
ZPT_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ZPT_dir)
import ZPTKit
assert ZPTKit.__file__ == os.path.join(ZPT_dir, 'ZPTKit', '__init__.pyc')
