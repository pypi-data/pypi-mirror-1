# -*- coding: utf-8 -*-

from cubicweb.entities import AnyEntity

class Application(AnyEntity):
    __regid__ = 'Application'


class Service(AnyEntity):
    __regid__ = 'Service'


class Device(AnyEntity):
    __regid__ = 'Device'


class Host(AnyEntity):
    __regid__ = 'Host'

