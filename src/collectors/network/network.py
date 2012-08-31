"""
The NetworkCollector class collects metrics on network interface usage
using /proc/net/dev.

#### Dependencies

 * /proc/net/dev

"""

import diamond.collector
import diamond.convertor
import os
import re

try:
    import psutil
except ImportError:
    psutil = None

class NetworkCollector(diamond.collector.Collector):

    PROC = '/proc/net/dev'

    MAX_VALUES = {
        'rx_bytes':      diamond.collector.MAX_COUNTER,
        'rx_packets':    diamond.collector.MAX_COUNTER,
        'rx_errors':     diamond.collector.MAX_COUNTER,
        'rx_drop':       diamond.collector.MAX_COUNTER,
        'rx_fifo':       diamond.collector.MAX_COUNTER,
        'rx_frame':      diamond.collector.MAX_COUNTER,
        'rx_compressed': diamond.collector.MAX_COUNTER,
        'rx_multicast':  diamond.collector.MAX_COUNTER,
        'tx_bytes':      diamond.collector.MAX_COUNTER,
        'tx_packets':    diamond.collector.MAX_COUNTER,
        'tx_errors':     diamond.collector.MAX_COUNTER,
        'tx_drop':       diamond.collector.MAX_COUNTER,
        'tx_fifo':       diamond.collector.MAX_COUNTER,
        'tx_frame':      diamond.collector.MAX_COUNTER,
        'tx_compressed': diamond.collector.MAX_COUNTER,
        'tx_multicast':  diamond.collector.MAX_COUNTER,
        }

    def get_default_config_help(self):
        config_help = super(NetworkCollector, self).get_default_config_help()
        config_help.update({
            'interfaces' : 'List of interface types to collect',
            'greedy' : 'Greedy match interfaces',
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(NetworkCollector, self).get_default_config()
        config.update(  {
            'path':         'network',
            'interfaces':   ['eth', 'bond'],
            'byte_unit':    ['megabit', 'megabyte'],
            'greedy':       'true',
        } )
        return config

    def collect(self):
        """
        Collect network interface stats.
        """

        # Initialize results
        results = {}
        
        if os.access(self.PROC, os.R_OK):
            
            # Open File
            file = open(self.PROC)
            # Build Regular Expression
            greed = ''
            if self.config['greedy'].lower() == 'true' :
                greed = '[0-9]+'
            
            exp = '^(?:\s*)((?:%s)%s):(?:\s*)(?P<rx_bytes>\d+)(?:\s*)(?P<rx_packets>\w+)(?:\s*)(?P<rx_errors>\d+)(?:\s*)(?P<rx_drop>\d+)(?:\s*)(?P<rx_fifo>\d+)(?:\s*)(?P<rx_frame>\d+)(?:\s*)(?P<rx_compressed>\d+)(?:\s*)(?P<rx_multicast>\d+)(?:\s*)(?P<tx_bytes>\d+)(?:\s*)(?P<tx_packets>\w+)(?:\s*)(?P<tx_errors>\d+)(?:\s*)(?P<tx_drop>\d+)(?:\s*)(?P<tx_fifo>\d+)(?:\s*)(?P<tx_frame>\d+)(?:\s*)(?P<tx_compressed>\d+)(?:\s*)(?P<tx_multicast>\d+)(?:.*)$' % (( '|'.join(self.config['interfaces']) ), greed)
            reg = re.compile(exp)
            # Match Interfaces
            for line in file:
                match = reg.match(line)
                if match:
                    device = match.group(1)
                    results[device] = match.groupdict()
            # Close File
            file.close()
        elif psutil:
            network_stats = psutil.network_io_counters(True)
            for device in network_stats.keys():
                results[device] = {}
                results[device]['rx_bytes'] = network_stats[device].bytes_recv
                results[device]['tx_bytes'] = network_stats[device].bytes_sent
                results[device]['rx_packets'] = network_stats[device].packets_recv
                results[device]['tx_packets'] = network_stats[device].packets_sent
    
        for device in results:
            stats = results[device]
            for s,v in stats.items():
                # Get Metric Name
                metric_name = '.'.join([device, s])
                # Get Metric Value
                metric_value = self.derivative(metric_name, long(v), self.MAX_VALUES[s])

                # Convert rx_bytes and tx_bytes
                if s == 'rx_bytes' or s == 'tx_bytes':
                    convertor = diamond.convertor.binary(value = metric_value, unit = 'byte')

                    for u in self.config['byte_unit']:
                        # Public Converted Metric
                        self.publish(metric_name.replace('bytes', u), convertor.get(unit = u))
                else:
                    # Publish Metric Derivative
                    self.publish(metric_name, metric_value)
            
                    
        return None
