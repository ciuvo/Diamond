#!/usr/bin/python
################################################################################

from test import *

from diamond.collector import Collector

from elasticsearch import ElasticSearchCollector

################################################################################

class TestElasticSearchCollector(CollectorTestCase):
    def setUp(self):
        config = get_collector_config('ElasticSearchCollector', {})

        self.collector = ElasticSearchCollector(config, None)

    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data(self, publish_mock):
        with patch('urllib2.urlopen', Mock(return_value = self.getFixture('stats'))):
            self.collector.collect()
            
        self.assertPublishedMany(publish_mock, {
            'http.current' : 1, 
            
            'indices.docs.count' : 11968062, 
            'indices.docs.deleted' : 2692068, 
            'indices.datastore.size': 22724243633,

            'process.cpu.percent' : 58, 
            
            'process.mem.resident' : 5192126464, 
            'process.mem.share' : 11075584, 
            'process.mem.virtual' : 7109668864, 

            'disk.reads.count': 55996, 
            'disk.reads.size': 1235387392,
            'disk.writes.count': 5808198,
            'disk.writes.size': 23287275520,

            
        })

    @patch.object(Collector, 'publish')
    def test_should_fail_gracefully(self, publish_mock):
        with patch('urllib2.urlopen', Mock(return_value = self.getFixture('stats_blank'))):
            self.collector.collect()
          
        self.assertPublishedMany(publish_mock, {})

################################################################################
if __name__ == "__main__":
    unittest.main()
