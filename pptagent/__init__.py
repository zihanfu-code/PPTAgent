"""PPTAgent: Generating and Evaluating Presentations Beyond Text-to-Slides.

This package provides tools to automatically generate presentations from documents,
following a two-phase approach of Analysis and Generation.

For more information, visit: https://github.com/zihanfu-code/PPTAgent
"""

__version__ = "0.1.0"
__author__ = "zihanfu"
__email__ = "zfuao@connect.ust.hk"


# Check the version of python and python-pptx
import sys

if sys.version_info < (3, 11):
    raise ImportError("You should use Python 3.11 or higher for this project.")

from packaging.version import Version
from pptx import __version__ as PPTXVersion

try:
    PPTXVersion, Mark = PPTXVersion.split("+")
    assert Version(PPTXVersion) >= Version("1.0.4") and Mark == "PPTAgent"
except:
    raise ImportError(
        "You should install the customized `python-pptx` for this project: zihanfu-code/python-pptx, but got %s."
        % PPTXVersion
    )

# Import main modules to make them directly accessible when importing the package
from .agent import *
from .apis import *
from .document import *
from .induct import *
from .llms import *
from .model_utils import *
from .multimodal import *
from .pptgen import *
from .presentation import *
from .utils import *

# Define the top-level exports
__all__ = [
    "agent",
    "pptgen",
    "document",
    "llms",
    "presentation",
    "utils",
    "apis",
    "model_utils",
    "multimodal",
    "induct",
]
