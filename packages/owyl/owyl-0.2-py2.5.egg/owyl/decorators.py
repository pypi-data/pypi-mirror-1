# -*- coding: utf-8 -*-
"""decorators -- decorators for owyl behavior trees.



Copyright 2008 David Eyk. All rights reserved.

$Author: david.eyk $\n
$Rev: 16 $\n
$Date: 2009-01-05 21:04:19 -0600 (Mon, 05 Jan 2009) $
"""

__author__ = "$Author: david.eyk $"[9:-2]
__revision__ = "$Rev: 16 $"[6:-2]
__date__ = "$Date: 2009-01-05 21:04:19 -0600 (Mon, 05 Jan 2009) $"[7:-2]

from core import task

@task
def identity(child):
    """Transparent decorator. Pass yielded values from child unchanged.
    """
    while True:
        yield child.next()
