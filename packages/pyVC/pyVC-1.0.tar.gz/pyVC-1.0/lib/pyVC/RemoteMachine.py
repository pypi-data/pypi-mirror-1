"""Package containing the class for a Remote Machine object"""
__revision__ = "$Revision$"

import Pyro.core
from pyVC.Machine import Machine

class RemoteMachine(Machine, Pyro.core.ObjBase):
    """This object defines a Pyro Real Machine"""
    __revision__ = "$Revision$"

    def __init__(self):
        Pyro.core.ObjBase.__init__(self)
        Machine.__init__(self)
