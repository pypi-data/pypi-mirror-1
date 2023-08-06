# -*- coding: utf-8 -*-
"""stack -- stack implementation for owyl



Copyright 2008 David Eyk. All rights reserved.

$Author: david.eyk $\n
$Rev: 27 $\n
$Date: 2009-01-07 13:46:38 -0600 (Wed, 07 Jan 2009) $
"""

__author__ = "$Author: david.eyk $"[9:-2]
__revision__ = "$Rev: 27 $"[6:-2]
__date__ = "$Date: 2009-01-07 13:46:38 -0600 (Wed, 07 Jan 2009) $"[7:-2]

__all__ = "EmptyError Stack".split()

EmptyError = IndexError

class Stack(list):
    """A list with a push method.
    """
    push = list.append
