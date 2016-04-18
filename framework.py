#!/usr/bin/python

from pymongo import MongoClient
from operations import registry,NetconfConnector,SSHXRConnector
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
            self._method = NetconfConnector(self)
        if connect_type == 'cli_xr':
            self._method = SSHXRConnector(self)
        #return self._method.get_connection()
        return self._method.connect()

    #def __getattr__(self,name):
    #    return getattr(self._method,name)

    def get_operation(self,check,*args,**kwargs):
        device_family = self.info['family']
        func_to_run = registry.func_map[check][device_family]
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
        def wrap(*args,**kwargs):               
            # The first argument MUST be 'target'
            target = args[0]
            with self.get_db_connection():
                device_info = self.get_context(target)
                self.device_context.info = device_info
            #os_match = [device_info['version'] for item in self.versions[device_info['family']] if re.search(device_info['version'],item)]
            #if os_match:
            return func(self.device_context,*args,**kwargs)
            #else:
	    #    raise OSNotSupported(device_info['family'],device_info['version'],target)
        return wrap

