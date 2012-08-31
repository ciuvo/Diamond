#!/usr/bin/python
################################################################################

from test import *

from diamond.collector import Collector
from smart import SmartCollector

################################################################################

class TestSmartCollector(CollectorTestCase):
    def setUp(self):
        config = get_collector_config('SmartCollector', {
            'interval': 10,
            'bin' : 'true',
        })

        self.collector = SmartCollector(config, None)

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data_osx_missing(self, publish_mock):
        with patch('os.listdir', Mock(return_value = ['disk0'] )):
            with patch('subprocess.Popen.communicate', Mock(return_value =
                ( self.getFixture('osx_missing').getvalue() , '')
            )):
                self.collector.collect()
    
            self.assertPublishedMany(publish_mock, {
            })
            
    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data_osx_ssd(self, publish_mock):
        with patch('os.listdir', Mock(return_value = ['disk0'] )):
            with patch('subprocess.Popen.communicate', Mock(return_value =
                ( self.getFixture('osx_ssd').getvalue() , '')
            )):
                self.collector.collect()
    
            self.assertPublishedMany(publish_mock, {
                'disk0.172' : 0,
                'disk0.Head_Amplitude' : 100,
                'disk0.Reallocated_Sector_Ct' : 0,
                'disk0.Temperature_Celsius' : 128,
                'disk0.174' : 3,
                'disk0.Reported_Uncorrect' : 0,
                'disk0.Raw_Read_Error_Rate' : 5849487,
                'disk0.Power_On_Hours' : 199389561752279,
                'disk0.Total_LBAs_Read' : 17985,
                'disk0.Power_Cycle_Count' : 381,
                'disk0.Hardware_ECC_Recovered' : 5849487,
                'disk0.171' : 0,
                'disk0.Soft_Read_Error_Rate' : 5849487,
                'disk0.234' : 2447,
                'disk0.Program_Fail_Cnt_Total' : 0,
                'disk0.Media_Wearout_Indicator' : 4881,
                'disk0.Erase_Fail_Count_Total' : 0,
                'disk0.Wear_Leveling_Count' : 2,
                'disk0.Reallocated_Event_Count' : 0,
                'disk0.Total_LBAs_Written' : 2447,
                'disk0.Soft_ECC_Correction' : 5849487,
            })

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data_centos55_hdd(self, publish_mock):
        with patch('os.listdir', Mock(return_value = ['sda'] )):
            with patch('subprocess.Popen.communicate', Mock(return_value =
                ( self.getFixture('centos5.5_hdd').getvalue() , '')
            )):
                self.collector.collect()
    
            self.assertPublishedMany(publish_mock, {
                'sda.Temperature_Celsius' : 28,
                'sda.Power_On_Hours' : 6827,
                'sda.Power_Cycle_Count' : 7,
                'sda.Power-Off_Retract_Count' : 5,
                'sda.UDMA_CRC_Error_Count' : 0,
                'sda.Load_Cycle_Count' : 2,
                'sda.Calibration_Retry_Count' : 0,
                'sda.Spin_Up_Time' : 3991,
                'sda.Spin_Retry_Count' : 0,
                'sda.Multi_Zone_Error_Rate' : 0,
                'sda.Raw_Read_Error_Rate' : 0,
                'sda.Reallocated_Event_Count' : 0,
                'sda.Start_Stop_Count' : 8,
                'sda.Offline_Uncorrectable' : 0,
                'sda.Current_Pending_Sector' : 0,
                'sda.Reallocated_Sector_Ct' : 0,
                'sda.Seek_Error_Rate' : 0,
            })

################################################################################
if __name__ == "__main__":
    unittest.main()
