import sys, os
import marshal
from decorator import decorator
import inspect

from mc_connection import mc


class MMcCache(object):
    def __init__(self, key_pattern):
        self.key_pattern = key_pattern

    def delete(self, *args):
        key = self.key_pattern%args
        return mc.delete(key)

    def get(self, *args):
        key = self.key_pattern%args
        return mc.get_marshal(key)

    def set(self, key, value, expire=0):
        return mc.set_marshal(self.key_pattern%key, value, expire)

    def get_list(self, args_list):
        key_pattern = self.key_pattern
        key_list = [key_pattern%i for i in args_list]
        result = mc.get_list_marshal(key_list)
        return result

    def get_multi(self, args_list):
        key_pattern = self.key_pattern
        key_list = [key_pattern%i for i in args_list]
        result = mc.get_list_marshal(key_list)

        return dict(zip(args_list, result))

    def __call__(self, key, expire=0):
        if type(key) is str:
            _key = key
            key = lambda x:_key.format(**x)

        def _func(func):
            arg_names, varargs, varkw, defaults = inspect.getargspec(func)

            if varargs or varkw:
                raise Exception("do not support varargs")

            defaults = defaults or {}
            if defaults:
                args = dict(zip(arg_names[-len(defaults):], defaults))
            else:
                args = {}

            key_pattern = self.key_pattern

            def _(f, *a, **kw):
                aa = args.copy()
                aa.update(zip(arg_names, a))
                aa.update(kw)
                mc_key = key_pattern%key(aa)

                #print mc_key
                r = mc.get_marshal(mc_key)
                if r is None:
                    r = f(*a, **kw)
                    mc.set_marshal(mc_key, r, expire)
                return r

            return decorator(_, func)
        return _func

class McCache(object):
    """
    def test_mc_cache():
        mc_xxx = McCache("XXxxx:%s")

        @mc_xxx(lambda x:x['id'])
        def xxx(id):
            return id*3

        print  xxx("123")
        
        @mc_xxx("{id}")
        def xxx(id):
            return id*3

        print  xxx("467")
        print "MC GET" 
        print mc_xxx.get("123")
        print mc_xxx.get_multi(["123","467"])
        mc_xxx.delete("123")
    """
    def __init__(self, key_pattern):
        self.key_pattern = key_pattern

    def delete(self, *args):
        key = self.key_pattern%args
        return mc.delete(key)

    def get(self, *args):
        key = self.key_pattern%args
        return mc.get(key)

    def set(self, key, value, expire=0):
        return mc.set(self.key_pattern%key, value, expire)

    def get_list(self, args_list):
        key_pattern = self.key_pattern
        key_list = [key_pattern%i for i in args_list]
        result = mc.get_list(key_list)
        return result

    def get_multi(self, args_list):
        key_pattern = self.key_pattern
        key_list = [key_pattern%i for i in args_list]
        result = mc.get_list(key_list)

        return dict(zip(args_list, result))

    def __call__(self, key, expire=0):
        if type(key) is str:
            _key = key
            key = lambda x:_key.format(**x)

        def _func(func):
            arg_names, varargs, varkw, defaults = inspect.getargspec(func)

            if varargs or varkw:
                raise Exception("do not support varargs")

            defaults = defaults or {}
            if defaults:
                args = dict(zip(arg_names[-len(defaults):], defaults))
            else:
                args = {}

            key_pattern = self.key_pattern

            def _(f, *a, **kw):
                aa = args.copy()
                aa.update(zip(arg_names, a))
                aa.update(kw)
                mc_key = key_pattern%key(aa)

                #print mc_key
                r = mc.get(mc_key)
                if r is None:
                    r = f(*a, **kw)
                    mc.set(mc_key, r, expire)
                return r

            return decorator(_, func)
        return _func

    def decr(self, *args):
        key = self.key_pattern%args
        return mc.decr(key)

    def incr(self, *args):
        key = self.key_pattern%args
        return mc.incr(key)

#TODO
#Write Mc with encode decode
ArrayMcCache = MMcCache




