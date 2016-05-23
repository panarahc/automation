#!/usr/bin/python

from pymongo import MongoClient
from auto_operations.operation_registry import OperationRegistry
from contextlib import contextmanager
import re
import ios
import junos


class OSNotSupported:
    def __init__(self,family,os,target):
        print "Current {} version {} on device {} is not supported.".format(family.capitalize(),os,target)


class DeviceContext(object):

    def get_connection(self,connect_type):
        #print self.__dict__
        if connect_type == 'cli':
            if self.info['family'] == 'ios' or self.info['family'] == 'iosxe':
                self._method = ios.CLI(self.info['_id'])
            if self.info['family'] == 'junos':
                self._method = junos.CLI(self.info['_id'])
        if connect_type == 'netconf':
            self._method = junos.Netconf(self.info['_id'])
        return self._method.connect()

    def get_operation(self,check):
        device_family = self.info['family']
        func_to_run = OperationRegistry.func_map[check][device_family]
        args = self.args
        kwargs = self.kwargs
        result = func_to_run(self,*args,**kwargs)
        return result


class CheckOperation(object):

    def __init__(self):
        #self.versions = versions
        self.device_context = DeviceContext() 

    @contextmanager
    def get_db_connection(self):
        try:
            self.connection = MongoClient('mongodb://localhost',port=27017)
            self.db = self.connection.inventory
            yield
        finally:
            self.connection.close()

    def get_context(self,target):
        self.device = self.db.devices
        query = {"_id":target}
        result = self.device.find_one(query)
        return result

    def __call__(self,func):
        def wrap(target,*args,**kwargs):               
            # The first argument MUST be 'target'
            self.device_context.args = args
            self.device_context.kwargs = kwargs
            #target = args[0]
            with self.get_db_connection():
                #device_info = self.get_context(target)
                self.device_context.info = self.get_context(target)
            #os_match = [device_info['version'] for item in self.versions[device_info['family']] if re.search(device_info['version'],item)]
            #if os_match:
            return func(self.device_context,target,*args,**kwargs)
            #else:
	    #    raise OSNotSupported(device_info['family'],device_info['version'],target)
        return wrap


