# -*- coding: utf-8 -*-
try:
    import AccessControl
    AccessControl.ModuleSecurityInfo('pdb').declarePublic('set_trace')
    AccessControl.ModuleSecurityInfo('stxnext.pdb').declarePublic('set_trace')
except ImportError:
    pass

from debugger import set_trace