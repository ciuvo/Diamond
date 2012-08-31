#!/usr/bin/python
################################################################################

from test import *

from diamond.collector import Collector

from nginx import NginxCollector

################################################################################

class TestNginxCollector(CollectorTestCase):
    def setUp(self):
        config = get_collector_config('NginxCollector', {})

        self.collector = NginxCollector(config, None)

    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data(self, publish_mock):
        with patch('urllib2.urlopen', Mock(return_value = self.getFixture('status'))):
            self.collector.collect()
            
        self.assertPublishedMany(publish_mock, {
            'active_connections' : 3, 
            'conn_accepted' : 396396, 
            'conn_handled' : 396396, 
            'req_handled' : 396396, 
            'act_reads' : 2, 
            'act_writes' : 1, 
            'act_waits' : 0, 
        })

    @patch.object(Collector, 'publish')
    def test_should_fail_gracefully(self, publish_mock):
        with patch('urllib2.urlopen', Mock(return_value = self.getFixture('status_blank'))):
            self.collector.collect()
            
        self.assertPublishedMany(publish_mock, {})

################################################################################
if __name__ == "__main__":
    unittest.main()
