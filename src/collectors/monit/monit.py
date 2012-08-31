"""
Collect the monit stats and report on cpu/memory for monitored processes

#### Dependencies

 * monit serving up /_status

"""

import urllib2
import base64

from xml.dom.minidom import parseString

import diamond.collector

class MonitCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        config_help = super(MonitCollector, self).get_default_config_help()
        config_help.update({
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(MonitCollector, self).get_default_config()
        config.update(  {
            'host':         '127.0.0.1',
            'port':         2812,
            'user':         'monit',
            'passwd':       'monit',
            'path':         'monit',
            'byte_unit':    ['byte'],
        } )
        return config


    def collect(self):
        try:
            request = urllib2.Request('http://%s:%i/_status?format=xml' % (self.config['host'], int(self.config['port'])))

            #
            # shouldn't need to check this
            base64string = base64.encodestring('%s:%s' % (self.config['user'], self.config['passwd'])).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)   
            response = urllib2.urlopen(request)
        except Exception, e:
            self.log.error("Unable to open http://%s:%i/_status?format=xml" % (self.config['host'], int(self.config['port'])))
            return

        metrics = {}
        
        try:
            dom = parseString("".join(response.readlines()))
        except:
            self.log.error("Got an empty response from the monit server")
            return

        for service in dom.getElementsByTagName('service'):
            if int(service.getAttribute('type')) == 3:
                name = service.getElementsByTagName('name')[0].firstChild.data
                cpu = service.getElementsByTagName('cpu')[0].getElementsByTagName('percent')[0].firstChild.data
                mem = int(service.getElementsByTagName('memory')[0].getElementsByTagName('kilobyte')[0].firstChild.data)

                metrics["%s.cpu.percent" % name] = cpu
                for unit in self.config['byte_unit']:
                    metrics["%s.memory.%s_usage" % (name, unit)] = diamond.convertor.binary.convert(value = mem, oldUnit = 'kilobyte', newUnit = unit)

        for key in metrics:
            self.publish(key, metrics[key])

