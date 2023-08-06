##############################################################################
# Copyright 2008, Gerhard Weis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT
##############################################################################
'''
This modules implements the full description for a upnp:rootdevice

TODO: how about upnp announce? does it always announse root devices?
      or should I also add the posibility to just instantiate descriptions for announced
      services, but this may cause problems. e.g. miniupnp announces services which are not there.
'''
from urllib2 import urlopen
from urlparse import urljoin

from zope.interface import implements

from lxml import etree

from rsl.globalregistry import lookupimpl
from rsl.interfaces import IProxyFactory
from rsl.implementations import OperationInfo, ParamInfo
from rsl.upnp.interfaces import IUPnPServiceDescription
from rsl.upnp.namespace import NS_UPNP_DEVICE, NS_UPNP_SERVICE
from rsl.misc.namespace import clark, clark2tuple
from rsl.soap11.namespace import NS_SOAP, HTTP_TRANSPORT

device_map = {'upnp:rootdevice': 'Root device',
              'urn:schemas-upnp-org:device:InternetGatewayDevice': 'Internet Gateway',
              'urn:schemas-upnp-org:device:WANDevice': 'WAN Device',
              'urn:schemas-upnp-org:device:WANConnectionDevice': 'WAN Connection Device',
              # UPnP services
              'urn:schemas-upnp-org:service:WANIPConnection': 'WAN IP Connection',
              'urn:schemas-upnp-org:service:WANCommonInterfaceConfig': 'WAN Common Interface Config',
              'urn:schemas-upnp-org:service:WANPPPConnection': 'WAN PPP Connection',
              'urn:schemas-upnp-org:service:Layer3Forwarding': 'Layer 3 Forwarding',
              # Vendor specific service
              'urn:schemas-dummy-com:service:Dummy': 'Dummy Device',
              }

class UPnPDevice(object):
    '''
    holds all information gathered from a upnp device description file.
    '''
    
    def __init__(self, deviceelem):
        '''
        initialise UPnPDevice instance from etree.
        '''
        self.deviceType = deviceelem.find(clark(NS_UPNP_DEVICE, 'deviceType')).text 
        self.deviceUDN = deviceelem.find(clark(NS_UPNP_DEVICE, 'UDN')).text
        self.usn = '%s::%s' % (self.deviceUDN, self.deviceType)
        # look for services for the top level device
        self.services = {}
        servicelist = deviceelem.findall('{%s}serviceList/{%s}service' % (NS_UPNP_DEVICE, NS_UPNP_DEVICE))
        if servicelist is not None:
            for service in servicelist:
                sinfos = {}
                for element in service:
                    _, elname = clark2tuple(element.tag)
                    sinfos[elname] = element.text
                serviceusn = '%s::%s' % (self.deviceUDN, sinfos['serviceType'])
                self.services[serviceusn] = sinfos

class UPnPService(object):
    '''
    An UPnPService instance.
    
    TODO: it would be easy to implement getProxy here, but where do I get controlURL and eventURL from?
    '''
    
    def __init__(self, usn, serviceType, ctrlUrl, evtUrl):
        '''
        initialise UPnPSerivce instance with required metadata.
        '''
        self.usn = usn
        self.st = serviceType
        self.url = None
        self.controlURL = ctrlUrl
        self.eventURL = evtUrl
        self.variables = {}
        self.actions = {}
    
    def fromURL(self, url, **kw):
        '''
        initialise UPnPService from service url.
        '''
        self.url = url
        servicedescr = etree.fromstring(urlopen(url).read())
        self.parseVariables(servicedescr.findall('{%s}serviceStateTable/{%s}stateVariable' % (NS_UPNP_SERVICE, NS_UPNP_SERVICE)))
        self.parseActions(servicedescr.findall('{%s}actionList/{%s}action' % (NS_UPNP_SERVICE, NS_UPNP_SERVICE)))
        
    def parseVariables(self, variablelist):
        '''
        find all service variables in upnp service description.
        '''
        for varelem in variablelist:
            var = {}
            var['sendEvents'] = varelem.get("sendEvents")
            var['name'] = varelem.find(clark(NS_UPNP_SERVICE, "name")).text
            var['dataType'] = varelem.find(clark(NS_UPNP_SERVICE, 'dataType')).text
            avl = varelem.findall('{%s}allowedValueList/{%s}allowedValue' % (NS_UPNP_SERVICE, NS_UPNP_SERVICE))
            if avl is not None:
                var['allowedValue'] = []
                for avelem in avl:
                    var['allowedValue'].append(avelem.text)
            else:
                var['allowedValue'] = None
            avr = varelem.find(clark(NS_UPNP_SERVICE, 'allowedValueRange'))
            if avr is not None:
                minimum = avr.find(clark(NS_UPNP_SERVICE, "minimum")).text
                maximum = avr.find(clark(NS_UPNP_SERVICE, "maximum")).text
                step = avr.find(clark(NS_UPNP_SERVICE, "step")).text
                var['allowedValueRange'] = (minimum, maximum, step)
            else:
                var['allowedValueRange'] = None
            self.variables[var['name']]= var
            
    def parseActions(self, actionlist):
        '''
        find all service actions in upnp service description.
        '''
        for actionelem in actionlist:
            action = {}
            action['name'] = actionelem.find(clark(NS_UPNP_SERVICE, "name")).text
            arglist = actionelem.findall('{%s}argumentList/{%s}argument' % (NS_UPNP_SERVICE, NS_UPNP_SERVICE))
            if arglist is not None:
                action['argumentList'] = []
                for argelem in arglist:
                    arg = {}
                    for el in argelem:
                        _, name = clark2tuple(el.tag)
                        arg[name] = el.text
                    action['argumentList'].append(arg)
            else:
                action['argumentList'] = None
            self.actions[action['name']]= action
            
    def getOperationInfos(self):
        '''
        return array of IOperationInfo for all service actions.
        '''
        ret = []
        for action in self.actions.values():
            opinfo = OperationInfo()
            opinfo.name = action['name']
            opinfo.location = self.controlURL
            opinfo.serializer = 'soap:envelope:1.1'
            opinfo.soapaction = self.st + '#' + opinfo.name 
            opinfo.transport = HTTP_TRANSPORT
            opinfo.input = {}
            opinfo.input['wrapper'] = {}
            opinfo.input['wrapper']['name'] = opinfo.name
            opinfo.input['wrapper']['namespace'] = self.st
            opinfo.input['body'] = []
            opinfo.output = {}
            opinfo.output['wrapper'] = {}
            opinfo.output['wrapper']['name'] = opinfo.name + 'Response'
            opinfo.output['wrapper']['namespace'] = self.st
            opinfo.output['body'] = []
            for arg in action['argumentList']:
                pinfo = ParamInfo()
                pinfo.name = arg['name']
                pinfo.namespace = None
                var = self.variables[arg['relatedStateVariable']]
                pinfo.type = var['dataType']
                pinfo.serializer = 'UPnPParam:type'
                if arg['direction'] == 'in':
                    opinfo.input['body'].append(pinfo)
                elif arg['direction']== 'out':
                    opinfo.output['body'].append(pinfo)
            ret.append(opinfo)
        # add QueryStateVariable operation
        opinfo= OperationInfo()
        opinfo.name = 'QueryStateVariable'
        opinfo.location = self.controlURL
        opinfo.serializer = 'soap:envelope:1.1'
        opinfo.soapaction = 'urn:schemas-upnp-org:control-1.0#QueryStateVariable'
        opinfo.transport = HTTP_TRANSPORT 
        opinfo.input = {}
        opinfo.input['wrapper'] = {}
        opinfo.input['wrapper']['name'] = 'QueryStateVariable'
        opinfo.input['wrapper']['namespace'] = 'urn:schemas-upnp-org:control-1.0'
        pinfo = ParamInfo()
        pinfo.name = 'varName'
        pinfo.namespace = None
        pinfo.type = 'string'
        pinfo.serializer = 'UPnPParam:type'
        opinfo.input['body'] = [pinfo]
        opinfo.output = {}
        opinfo.output['wrapper'] = {}
        opinfo.output['wrapper']['name'] = 'QueryStateVariablResponse'
        opinfo.output['wrapper']['namespace'] = 'urn:schemas-upnp-org:control-1.0'
        pinfo = ParamInfo()
        pinfo.name = 'result'
        pinfo.namespace = None
        pinfo.type = 'any'
        pinfo.serializer = 'UPnPParam:type'
        opinfo.output['body'] = [pinfo]
        ret.append(opinfo)
        return ret
            
#            soapAction: ns#opname
#            {urn:schemas-upnp-org:control-1.0}QueryStateVariable 
#              param: <varName>string</varName>
#              
#            return:
#              QueryStateVariableResponse<return>value</return>
        

class UPnPDeviceDescr(object):
    '''
    IServiceDescription for UPnP Devices.
    '''
    
    implements(IUPnPServiceDescription)
    
    url = None
    
    descname = NS_UPNP_DEVICE
    
    def __init__(self):
        '''
        init empty service description.
        '''
        super(UPnPDeviceDescr, self).__init__()
        self.devices = {}
        self.services = {}
        
    def fromHeaders(self, headers):
        '''
        use http headers from UPnP announce message to initialise service
        description.
        '''
        self.fromURL(headers['location'])
        
        self.headers = headers
        self.stateVariables = {}
        self.callables = {}
        self.actions = {}
        self.controlURL = self.eventSubURL = self.scpdURL = None
        
        self._readSDP()
        
    def fromURL(self, url, **kw):
        '''
        parse upnp service description document at url.
        '''
        self.url = url
        devicedescr = etree.fromstring(urlopen(url).read()) # read device description
        # we can have on device with multiple subdevices with multiple subdevices ......
        # every device is identified by the combination of UDN and devicetype
        # the identifier for this Service is the top-level device. 
        deviceelem = devicedescr.find(clark(NS_UPNP_DEVICE,'device'))
        device = UPnPDevice(deviceelem)
        self.devices[device.usn] = device
        # ok, we have our top level device.... let's go for subdevices.
        self.parseSubDevices(deviceelem)
        # good... we know all devices and their services.... let's flatten the service list
        for device in self.devices.values():
            for usn, servicedict in device.services.items():
                service = UPnPService(usn, servicedict['serviceType'], urljoin(self.url, servicedict['controlURL']), urljoin(self.url, servicedict['eventSubURL']))
                service.fromURL(urljoin(self.url, servicedict['SCPDURL']))
                self.services[service.usn] = service
        
    def parseSubDevices(self, deviceelem):
        '''
        look for sub device and services.
        '''
        devicelist = deviceelem.findall('{%s}deviceList/{%s}device' % (NS_UPNP_DEVICE,NS_UPNP_DEVICE))
        if devicelist is not None:
            for subdeviceelem in devicelist:
                device = UPnPDevice(subdeviceelem)
                self.devices[device.usn] = device
                # there may be subdevices here :)
                self.parseSubDevices(subdeviceelem)
                                        
    def getProxy(self, **kw):
        '''
        return IProxy instance for given service.
        
        if no name is given return a service from the top level device
        '''
        name = kw.get('name', None)
        # find service for name
        service = self.services[name]
        proxyfac = lookupimpl(IProxyFactory, NS_SOAP)
        proxy = proxyfac(service.controlURL)
        for opinfo in service.getOperationInfos():
            proxy.addOperation(opinfo.name, opinfo)
        return proxy
    
    def getServices(self):
        '''
        return list of service names.
        '''
        return [{'name': name} for name in self.services.keys()] 
    
    def getHRType(self):
        ''' return human readable device/service Type if possbile '''
        for key, value in device_map.items():
            if self.headers['st'].startswith(key):
                return value
        return self.headers['st']
 
    def subscribe(self):
        '''
        subscribe for UPnP notification events.
        '''
#        subscriberequest1 = '''SUBSCRIBE /upnp/control/WANCommonIFC1 HTTP/1.1\r
#HOST: 192.168.1.1:49152\r
#CALLBACK: <http://192.168.1.10:49000>\r
#NT: upnp:event\r
#TIMEOUT: Second-180\r
#\r
#'''
        payload =  ""
        #print payload
        headers = {'CALLBACK': '<http://10.1.1.10:6633>', #FIXME: hard coded response address
                   'NT': 'upnp:event',
                   'TIMEOUT': 'Second-180'}
        code, res = self._send(self.eventSubURL, payload, headers, "SUBSCRIBE")
        print code, res