"""\
PYthon PreProcessor
===================

A directive .pypp must be found following a comment hash
for the file to be preprocessed.

Usage
-----
    import pypp
    

    @author: Jean-Lou Dupont
"""
__all__ = []

import sys
from importer import *
from controller import *
from loader import *

_controller = Controller()
_importer   = Importer()

# Hook-up a loader to the controller
_controller._loader = Loader

# I'd rather not have the Importer module handle the chain of events
_importer.callback_import_module = _controller.handle_import_module

# Hook-up our Importer following PEP302
sys.meta_path.append(_importer)
