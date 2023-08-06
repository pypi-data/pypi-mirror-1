# -*- coding: utf-8 -*-

###
### $Release: 0.0.3 $
### copyright(c) 2008-2009 kuwata-lab.com all rights reserved.
### MIT License
###

#from kook import KookRecipeError
#from kook.kitchen import IfExists
from kook.utils import flatten

__all__ = ('recipe', 'product', 'ingreds', 'byprods', 'coprods', 'priority', 'spices', 'cmdopts', )


def recipe(func):
    func._kook_recipe = True
    return func

#def recipe(func=None, kind=None):
#    if func is not None:
#        func._kook_recipe = True
#        return func
#    elif kind is not None:
#        if kind not in ('task', 'file'):
#            raise TypeError("@recipe(): kind should be 'task' or 'file'.")
#        def deco(f):
#            f._kook_recipe = True
#            f._kook_kind = kind
#            return f
#        return deco
#    else:
#        def deco(f):
#            f._kook_recipe = True
#            return f
#        return deco


def product(name):
    def deco(f):
        #f._kook_recipe  = True
        f._kook_product = name
        return f
    return deco


def ingreds(*names):
    def deco(f):
        f._kook_ingreds = tuple(flatten(names))
        return f
    return deco


def byprods(*names):
    def deco(f):
        f._kook_byprods = tuple(flatten(names))
        return f
    return deco


def coprods(*names):
    def deco(f):
        f._kook_coprods = tuple(flatten(names))
        return f
    return deco


def priority(level):     # not used yet
    if not isinstance(level, int):
        import kook
        raise kook.KookRecipeError("priority requires integer.")  # TODO: change backtrace
    def deco(f):
        f._kook_priority = level
        return f
    return deco


def spices(*names):
    def deco(f):
        f._kook_spices = tuple(flatten(names))
        return f
    return deco


def cmdopts(*names):
    import sys
    sys.stderr.write("[pykook] ERROR: '@cmdopts()' is obsolete. Use '@spices()' instead.\n")
    sys.stderr.write("[pykook]        See http://www.kuwata-lab.com/kook/pykook-CHANGES.txt for details.\n")
    sys.exit(1)
