"""Python tools for manage system commands as replacement to bash script."""

# Namespace package
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)

from .edit import *
from .setup import *
from .shell import *
from .system import *
