# The following line MUST be the only line in this file, according to the setuptools docs:
__import__('pkg_resources').declare_namespace(__name__)

# As a temporary HACK (FIXME), add this directory to the Python path:
import sys, os.path
_path = os.path.dirname(__file__)
sys.path.insert(0, _path)
