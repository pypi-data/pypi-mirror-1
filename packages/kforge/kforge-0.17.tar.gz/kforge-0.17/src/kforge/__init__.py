# Copyright (C) 2009 Approriate Software Foundation, Open Knowledge Foundation.
#
# Contributors are listed in the AUTHORS file in the root of the distribution.
# For license details see the COPYING file in the root of the distribution.

__version__ = '0.17'

def get():
    import kforge.soleInstance
    return kforge.soleInstance.application
