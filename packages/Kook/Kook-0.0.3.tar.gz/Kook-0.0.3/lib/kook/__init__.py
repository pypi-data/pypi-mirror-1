# -*- coding: utf-8 -*-

###
### $Release: 0.0.3 $
### copyright(c) 2008-2009 kuwata-lab.com all rights reserved.
### MIT License
###

__RELEASE__ = "$Release: 0.0.3 $".split(' ')[1]
__all__ = ('KookError', 'KookRecipeError', 'KookCommandError', )


class KookError(Exception):  # StandardError is not available in Python 3.0
    pass


class KookRecipeError(KookError):
    pass


class KookCommandError(KookError):
    pass
