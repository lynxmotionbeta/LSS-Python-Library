from lss import LssPacket, LssBus
import math
import os
import time
import yaml
import unittest

port_name = 'COM4'
baud = 921600
low_latency = False
servos = [0]

def find_config_file(config_basefile: str):
    config_path_search = ['~', '~/etc', '/etc/config', '.']
    if os.getenv('APPDATA'):
        config_path_search.append(os.getenv('APPDATA')+'/lynxmotion')
    for path_prefix in config_path_search:
        config_file = os.path.expanduser(os.path.join(path_prefix, config_basefile))
        if os.path.isfile(config_file):
            print('using config at ' + config_file)
            return config_file
    print(f'Cannot find {config_basefile} in paths  ' + '  '.join(config_path_search))
    exit(-2)


#
# Loads test configuration from a yaml file
#
# Copy the lss-tests.yml into one of the following directories and modify it:
# Linux/Mac:
#    ~/lss-testing.yml (home dir)
#    ~/etc/lss-testing.yml
#    /etc/config/lss-testing.yml   (system config dir)
#
# Windows:
#    %APPDATA%/lynxmotion/lss-testing.yml   (user application data dir)
#
config = yaml.safe_load(
    open(find_config_file('lss-testing.yml')))
if config:
    # load port details
    if 'port' in config:
        port = config['port']
        port_name = port['name'] if 'name' in port else '/dev/ttyUSB0'
        baud = port['baud'] if 'baud' in port else 921600
        low_latency = port['low_latency'] if 'low_latency' in port else False

    # load servo profiles
    servos = config['servos'] if 'servos' in config else [0]

# now open the LSS bus
bus = LssBus(
    port_name,
    baud,
    low_latency=low_latency)


def get_servos(category: str):
    return servos[category] \
        if category in servos \
        else servos['default']
    

#
#  UNIT TESTS
#
#

class LssTestCase(unittest.TestCase):

    def assertQuery(self, servo: int, parameter: str):
        bus.write_command(servo, f'Q{parameter}')
        p = bus.read()
        self.assertIsNotNone(p)
        self.assertTrue(p.known)
        self.assertEqual(p.command, parameter)

    def assertQueryEqual(self, servo: int, parameter: str, value: int):
        bus.write_command(servo, f'Q{parameter}')
        p = bus.read()
        self.assertIsNotNone(p)
        self.assertTrue(p.known)
        self.assertEqual(p.value, value)
        self.assertEqual(p.command, parameter)

    def assertQueryBetween(self, servo: int, parameter: str, min: int, max: int):
        bus.write_command(servo, f'Q{parameter}')
        p = bus.read()
        self.assertIsNotNone(p)
        self.assertTrue(p.known)
        self.assertEqual(p.command, parameter)
        self.assertGreaterEqual(p.value, min)
        self.assertLessEqual(p.value, max)

    def assertQueryWithin(self, servo: int, parameter: str, value: int, precision: int = 5):
        bus.write_command(servo, f'Q{parameter}')
        p = bus.read()
        self.assertIsNotNone(p)
        self.assertTrue(p.known)
        self.assertEqual(p.command, parameter)
        self.assertBetween(p.value, value - precision, value + precision)


    def assertBetween(self, v: int, min_value: int, max_value: int):
        self.assertGreaterEqual(v, min_value)
        self.assertLessEqual(v, max_value)


class LssSelfTests(LssTestCase):

    # Configure & Verify LED
    def test_LED(self):
        for servo in get_servos('query'):
            bus.write_command(servo, 'CLED2')
            time.sleep(0.25)
            self.assertQueryEqual(servo, 'LED', 2)
            bus.write_command(servo, 'CLED0')

    # Configure & Verify Stiffnesses
    def test_STIFF(self):
        for servo in get_servos('query'):
            bus.write_command(servo, 'AH')


class LssQueryTests(LssTestCase):

    # Query Motor ID
    def test_QID(self):
        for servo in get_servos('query'):
            self.assertQueryBetween(servo, 'ID', 0, 254)

    # Query Baud Rate
    def test_QB(self):
        for servo in get_servos('query'):
            self.assertQueryBetween(servo, 'B', 9600, 921600)

    # Query Current Position
    def test_QD(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'D')

    # Query Target Position
    def test_QDT(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'DT')

    # Query RC Position
    def test_QP(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'P')

    # Query Wheel Speed
    def test_QWD(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'WD')

    # Query Wheel RPM Speed
    def test_QWR(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'WR',)

    # Query Speed Target
    def test_QVT(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'VT')

    # Query Duty Cycle
    def test_QMD(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'MD')

    # # Query Status
    # def test_Q(self):
    #     for servo in get_servos('query'):
    #         self.assertQuery(servo, '')

    # Query Current RC Speed
    def test_QS(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'S')

    # Query Motion Control
    def test_QEM(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'EM')

    # Query Origin Offset
    def test_QO(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'O')

    # Query RC Angular Range
    def test_QAR(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'AR')

    # Query Stiffness
    def test_QAS(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'AS')

    # Query Holding Stiffness
    def test_QAH(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'AH')

    # Query Holding Delta
    def test_QHD(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'HD')

    # Query Acceleration
    def test_QAA(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'AA')

    # Query Deceleration
    def test_QAD(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'AD')

    # Query Gyre Direction
    def test_QG(self):
        for servo in get_servos('query'):
            self.assertQueryBetween(servo, 'G', -1, 1)

    # # Query First Position *** Return DIS
    # def test_QFD(self):
    #     for servo in get_servos('query'):
    #         self.assertQuery(servo, 'FD')

    # Query Position Limits Enabled
    def test_QLE(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'LE')

    # Query Positive Direction Limit
    def test_QLP(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'LP')

    # Query Negative Direction Limit
    def test_QLN(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'LN')

    # Query Current Soft Limit Counter (PRIVATE)
    def test_QCSL(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'CSL')

    # Query Position Filtering
    def test_QFPC(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'FPC')

    # Query Maximum Motor Duty
    def test_QMMD(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'MMD')

    # Query IPMS Enabled (PRIVATE)
    def test_QIPE(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'IPE')

    # Query Maximum Speed in Degrees
    def test_QSD(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'SD')

    # Query Maximum Speed in RPM
    def test_QSR(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'SR')

    # Query Voltage
    def test_QV(self):
        for servo in get_servos('query'):
            self.assertQueryBetween(servo, 'V', 0, 14000)

    # Query Temperature
    def test_QT(self):
        for servo in get_servos('query'):
            self.assertQueryBetween(servo, 'T', 0, 1000)

    # Query Current
    def test_QC(self):
        for servo in get_servos('query'):
            self.assertQueryBetween(servo, 'T', 0, 10000)

    # Query Model String
    def test_QMS(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'MS')

    # Query Firmware Version
    def test_QF(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'F')

    # Query Serial Number
    def test_QN(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'N')

    # (PRIVATE) Query Model Code
    def test_QM(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'M')

    # Query LED
    def test_QLED(self):
        for servo in get_servos('query'):
            self.assertQueryBetween(servo, 'LED', 0, 7)

    # Query LED Blink
    def test_QLB(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'LB')

    # (PRIVATE) Query Position Origin
    def test_QPO(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'PO')

    # (PRIVATE) Query Initial Sequence
    def test_QIS(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'IS')

    # (PRIVATE) Query Initial Sequence RC
    def test_QRIS(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'RIS')

    # (PRIVATE) Query Command Reply
    def test_QCR(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'CR')

    # # (PRIVATE) Query Current Torque
    # def test_QTQ(self):
    #     for servo in get_servos('query'):
    #         self.assertQuery(servo, 'TQ')

    # # (PRIVATE) Query Torque Target
    # def test_QTQT(self):
    #     for servo in get_servos('query'):
    #         self.assertQuery(servo, 'TQT')

    # (PRIVATE) Query Torque Maximum
    def test_QTQM(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'TQM')

    # (PRIVATE) Query Control Mode
    def test_QY(self):
        for servo in get_servos('query'):
            self.assertQuery(servo, 'Y')


class LssActionTests(LssTestCase):

    # Action Move in Degree
    def test_D(self):
        for servo in get_servos('action'):
            bus.write_command(servo, 'D0')
            time.sleep(0.8)
            self.assertQueryWithin(servo, 'D', 0, 10)
            bus.write_command(servo, 'D900')
            time.sleep(0.8)
            self.assertQueryWithin(servo, 'D', 900, 10)
            bus.write_command(servo, 'D0')
            time.sleep(0.8)
            self.assertQueryWithin(servo, 'D', 0, 10)
            time.sleep(1)

    # # Action Wheel in Degree
    # # Error when the servo answer to QSD2 it does with *QSD without the "2" and we have a parsing error
    # def test_WD(self):
    #     for servo in get_servos('action'):
    #         bus.write_command(servo, 'WD100')
    #         time.sleep(0.5)
    #         self.assertQueryWithin(servo, 'SD2', 100, 5)
    #         time.sleep(0.5)
    #         bus.write_command(servo, 'D0')
    #         time.sleep(0.5)
    #         bus.write_command(servo, 'L')
    #         time.sleep(1)
    #
    # # Action Wheel in RPM
    # # Error when the servo answer to QSR2 it does with *QSR without the "2" and we have a parsing error
    # def test_WR(self):
    #     for servo in get_servos('action'):
    #         bus.write_command(servo, 'WR10')
    #         time.sleep(0.5)
    #         self.assertQueryWithin(servo, 'SR2', 10, 1)
    #         time.sleep(0.5)
    #         bus.write_command(servo, 'D0')
    #         time.sleep(0.5)
    #         bus.write_command(servo, 'L')
    #         time.sleep(1)

if __name__ == '__main__':
    unittest.main()
    bus.close()

