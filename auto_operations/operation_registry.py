#!/usr/bin/python

class OperationRegistry(object):
    func_map = {}

    def device_operation(self,f_name,family=None):
        def func_decorator(func):
            try:
                OperationRegistry.func_map[f_name].update({family:func})
            except:
                OperationRegistry.func_map[f_name] = {family:func}
            print OperationRegistry.func_map
            def func_wrapper(*args,**kwargs):
                return func(*args,**kwargs)
            return func_wrapper
        return func_decorator

