#!/usr/bin/python

from collections import defaultdict


class OperationRegistry(object):
    func_map = defaultdict(dict)

    def device_operation(self,f_name,family=None):
        def func_decorator(func):
            for device_family in family.split(','): 
                OperationRegistry.func_map[f_name].update({device_family:func})
            #print OperationRegistry.func_map
            def func_wrapper(*args,**kwargs):
                return func(*args,**kwargs)
            return func_wrapper
        return func_decorator

