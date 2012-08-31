#!/usr/bin/python
################################################################################

from test import *

from diamond.collector import Collector
from kvm import KVMCollector

################################################################################

class TestKVMCollector(CollectorTestCase):
    def setUp(self):
        config = get_collector_config('KVMCollector', {
            'interval': 10,
        })

        self.collector = KVMCollector(config, None)
        self.collector.PROC = os.path.dirname(__file__)+'/fixtures/'

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_synthetic_data(self, publish_mock):
        with patch('__builtin__.open', Mock(return_value = StringIO(
            '0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n'
        ))):
            self.collector.collect()
            
        self.assertPublishedMany(publish_mock, {})
            
        self.collector.collect()

        self.assertPublishedMany(publish_mock, {
            'efer_reload' : 0.000000, 
            'exits' : 1436135848.000000, 
            'fpu_reload' : 121764903.500000, 
            'halt_exits' : 544586282.600000, 
            'halt_wakeup' : 235093451.400000, 
            'host_state_reload' : 801854250.600000, 
            'hypercalls' : 0.000000, 
            'insn_emulation' : 1314391264.700000, 
            'insn_emulation_fail' : 0.000000, 
            'invlpg' : 0.000000, 
            'io_exits' : 248822813.200000, 
            'irq_exits' : 701647108.400000, 
            'irq_injections' : 986654069.600000, 
            'irq_window' : 162240965.200000, 
            'largepages' : 351789.400000, 
            'mmio_exits' : 20169.400000, 
            'mmu_cache_miss' : 1643.300000, 
            'mmu_flooded' : 0.000000, 
            'mmu_pde_zapped' : 0.000000, 
            'mmu_pte_updated' : 0.000000, 
            'mmu_pte_write' : 11144.000000, 
            'mmu_recycled' : 0.000000, 
            'mmu_shadow_zapped' : 384.700000, 
            'mmu_unsync' : 0.000000, 
            'nmi_injections' : 0.000000, 
            'nmi_window' : 0.000000, 
            'pf_fixed' : 355636.100000, 
            'pf_guest' : 0.000000, 
            'remote_tlb_flush' : 111.200000, 
            'request_irq' : 0.000000, 
            'signal_exits' : 0.000000, 
            'tlb_flush' : 0.000000, 
        })

################################################################################
if __name__ == "__main__":
    unittest.main()
