# encoding: utf-8

'''exceptions
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2009. All rights reserved.'
__id__ = '$Id$'
__url__ = '$URL$'


# ---- Exceptions ----

class SchemaBotError(Exception):
    pass

class ChangeAlreadyDefinedError(SchemaBotError):
    pass

