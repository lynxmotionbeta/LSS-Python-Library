from lss import LssPacket, LssBus
import math
import os
import re
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

    def assertQueryBetween(self, servo: int, parameter: str, min_value: int, max_value: int):
        bus.write_command(servo, f'Q{parameter}')
        parameter = re.match('[a-zA-Z]*', parameter)[0]    # remove any number from the parameter
        p = bus.read()
        self.assertIsNotNone(p)
        self.assertTrue(p.known)
        self.assertEqual(p.command, parameter)
        self.assertBetween(p.value, min_value, max_value)

    def assertQueryNear(self, servo: int, parameter: str, value: int, precision: int = 5):
        bus.write_command(servo, f'Q{parameter}')
        parameter = re.match('[a-zA-Z]*', parameter)[0]    # remove any number from the parameter
        p = bus.read()
        self.assertIsNotNone(p)
        self.assertTrue(p.known)
        self.assertEqual(p.command, parameter)
        self.assertBetween(p.value, value - precision, value + precision)

    def assertBetween(self, v: int, min_value: int, max_value: int):
        self.assertGreaterEqual(v, min_value)
        self.assertLessEqual(v, max_value)


#@unittest.SkipTest
class LssProtocolTests(LssTestCase):

    # LED
    def test_LED_LED(self):
        for servo in get_servos('protocol'):
            bus.write_command(servo, 'LED0')
            time.sleep(0.5)
            self.assertQueryEqual(servo, 'LED', 0)
            bus.write_command(servo, 'LED1')
            time.sleep(0.25)
            self.assertQueryEqual(servo, 'LED', 1)
            bus.write_command(servo, 'LED2')
            time.sleep(0.25)
            self.assertQueryEqual(servo, 'LED', 2)
            bus.write_command(servo, 'LED3')
            time.sleep(0.25)
            self.assertQueryEqual(servo, 'LED', 3)
            bus.write_command(servo, 'LED4')
            time.sleep(0.25)
            self.assertQueryEqual(servo, 'LED', 4)
            bus.write_command(servo, 'LED5')
            time.sleep(0.25)
            self.assertQueryEqual(servo, 'LED', 5)
            bus.write_command(servo, 'LED6')
            time.sleep(0.25)
            self.assertQueryEqual(servo, 'LED', 6)
            bus.write_command(servo, 'LED7')
            time.sleep(0.25)
            self.assertQueryEqual(servo, 'LED', 7)
            bus.write_command(servo, 'CLED0')
            self.assertQueryEqual(servo, 'LED', 0)


    # Motor ID
    def test_MotorId_ID(self):
        for servo in get_servos('protocol'):
            self.assertQueryBetween(servo, 'ID', 0, 254)

    # Baud Rate
    def test_BaudRate_B(self):
        for servo in get_servos('protocol'):
            # we are only testing that a CB write and read-back
            # are equal. Which is ok. If we were to test a baud
            # rate change over a reset we'd need to update the
            # baud rate of the 'bus' object's serial port.
            self.assertQueryBetween(servo, 'B', 9600, 921600)
            bus.write_command(servo, 'CB9600')
            self.assertQueryEqual(servo, 'B', 9600)
            # Revert back to baud rate given in configuration
            bus.write_command(servo, f'CB{baud}')
            self.assertQueryEqual(servo, 'B', baud)
            #bus.write_command(servo, 'RESET')
            #time.sleep(1.5)

    # Query Current Position
    def test_CurrentPosition_QD(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'D')

    # Query Target Position
    def test_PositionTarget_QDT(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'DT')

    # Query RC Position
    def test_CurrentRCPosition_QP(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'P')

    # Query Wheel Speed
    def test_WheelSpeed_QWD(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'WD')

    # Query Wheel RPM Speed
    def test_WheelRPMSpeed_QWR(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'WR',)

    # Query Speed Target
    def test_SpeedTarget_QVT(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'VT')

    # # Query Status
    # def test_Status_Q(self):
    #     for servo in get_servos('protocol'):
    #         self.assertQuery(servo, '')

    # Query Current RC Speed
    def test_CurrentRCSpeed_QS(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'S')

    # Query Motion Control
    def test_MotionControl_EM(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'EM')
            bus.write_command(servo, 'EM0')
            self.assertQueryEqual(servo, 'EM', 0)
            bus.write_command(servo, 'CEM1')
            self.assertQueryEqual(servo, 'EM', 1)
            bus.write_command(servo, 'RESET')
            time.sleep(1.5)

    # Query Origin Offset
    def test_OriginOffset_O(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'O')
            bus.write_command(servo, 'O1000')
            self.assertQueryEqual(servo, 'O', 1000)
            bus.write_command(servo, 'CO0')
            self.assertQueryEqual(servo, 'O', 0)

    # Query RC Angular Range
    def test_RCAngularRange_AR(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'AR')
            bus.write_command(servo, 'AR3600')
            self.assertQueryEqual(servo, 'AR', 3600)
            bus.write_command(servo, 'CAR1800')
            self.assertQueryEqual(servo, 'AR', 1800)

    # Query Stiffness
    def test_AngularStiffness_AS(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'AS')
            bus.write_command(servo, 'AS4')
            self.assertQueryEqual(servo, 'AS', 4)
            bus.write_command(servo, 'CAS0')
            self.assertQueryEqual(servo, 'AS', 0)

    # Query Holding Stiffness
    def test_HoldStiffness_AH(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'AH')
            bus.write_command(servo, 'AH0')
            self.assertQueryEqual(servo, 'AH', 0)
            bus.write_command(servo, 'CAH4')
            self.assertQueryEqual(servo, 'AH', 4)

    # Query Holding Delta
    def test_HoldingDelta_HD(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'HD')
            bus.write_command(servo, 'CHD10')
            self.assertQueryEqual(servo, 'HD', 10)
            bus.write_command(servo, 'CHD30')
            self.assertQueryEqual(servo, 'HD', 30)

    # Query Acceleration
    def test_Acceleration_AA(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'AA')
            bus.write_command(servo, 'AA0')
            self.assertQueryEqual(servo, 'AA', 0)
            bus.write_command(servo, 'CAA100')
            self.assertQueryEqual(servo, 'AA', 100)

    # Query Deceleration
    def test_Deceleration_AD(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'AD')
            bus.write_command(servo, 'AD0')
            self.assertQueryEqual(servo, 'AD', 0)
            bus.write_command(servo, 'CAD100')
            self.assertQueryEqual(servo, 'AD', 100)

    # Query Gyre Direction
    def test_GyreDirection_G(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'G')
            bus.write_command(servo, 'G-1')
            self.assertQueryEqual(servo, 'G', -1)
            bus.write_command(servo, 'CG1')
            self.assertQueryEqual(servo, 'G', 1)

    # # Query First Position *** Return DIS
    # def test_FirstPosition_QFD(self):
    #     for servo in get_servos('protocol'):
    #         self.assertQuery(servo, 'FD')

    # Query Position Limits Enabled
    def test_PositionLimitsEnabled_LE(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'LE')
            bus.write_command(servo, 'CLE1')
            self.assertQueryEqual(servo, 'LE', 1)
            bus.write_command(servo, 'CLE0')
            self.assertQueryEqual(servo, 'LE', 0)
            bus.write_command(servo, 'RESET')
            time.sleep(1.5)

    # Query Positive Direction Limit
    def test_PositiveDirectionLimit_LP(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'LP')
            bus.write_command(servo, 'CLP500')
            self.assertQueryEqual(servo, 'LP', 500)
            bus.write_command(servo, 'CLP1200')
            self.assertQueryEqual(servo, 'LP', 1200)
            bus.write_command(servo, 'RESET')
            time.sleep(1.5)

    # Query Negative Direction Limit
    def test_NegativeDirectionLimit_LN(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'LN')
            bus.write_command(servo, 'CLN-500')
            self.assertQueryEqual(servo, 'LN', -500)
            bus.write_command(servo, 'CLN-1200')
            self.assertQueryEqual(servo, 'LN', -1200)
            bus.write_command(servo, 'RESET')
            time.sleep(1.5)

    # Query Current Soft Limit Counter (PRIVATE)
    def test_CurrentSoftLimitCounter_CSL(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'CSL')
            bus.write_command(servo, 'SCSL100')
            self.assertQueryEqual(servo, 'CSL', 100)
            bus.write_command(servo, 'SCSL500')
            self.assertQueryEqual(servo, 'CSL', 500)

    # Query Position Filtering
    def test_PositionFiltering_FPC(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'FPC')
            bus.write_command(servo, 'FPC10')
            self.assertQueryEqual(servo, 'FPC', 10)
            bus.write_command(servo, 'CFPC5')
            self.assertQueryEqual(servo, 'FPC', 5)

    # Query Maximum Motor Duty
    def test_MaximumMotorDuty_MMD(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'MMD')
            bus.write_command(servo, 'MMD500')
            self.assertQueryEqual(servo, 'MMD', 500)
            bus.write_command(servo, 'MMD1023')
            self.assertQueryEqual(servo, 'MMD', 1023)

    # Query IPMS Enabled (PRIVATE)
    def test_IPMSEnabled_IPE(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'IPE')
            bus.write_command(servo, 'IPE0')
            self.assertQueryEqual(servo, 'IPE', 0)
            bus.write_command(servo, 'IPE1')
            self.assertQueryEqual(servo, 'IPE', 1)

    # Query Maximum Speed in Degrees
    def test_SpeedDeg_SD(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'SD')
            bus.write_command(servo, 'SD100')
            self.assertQueryEqual(servo, 'SD', 100)
            bus.write_command(servo, 'CSD200')
            self.assertQueryEqual(servo, 'SD', 200)
            bus.write_command(servo, 'CSD500')

    # Query Maximum Speed in RPM
    def test_SpeedRPM_SR(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'SR')
            bus.write_command(servo, 'SR10')
            self.assertQueryEqual(servo, 'SR', 10)
            bus.write_command(servo, 'CSR20')
            self.assertQueryEqual(servo, 'SR', 20)
            bus.write_command(servo, 'CSR100')

    # Query Voltage
    def test_Voltage_QV(self):
        for servo in get_servos('protocol'):
            self.assertQueryBetween(servo, 'V', 0, 14000)

    # Query Temperature
    def test_Temperature_QT(self):
        for servo in get_servos('protocol'):
            self.assertQueryBetween(servo, 'T', 0, 1000)

    # Query Current
    def test_Current_QC(self):
        for servo in get_servos('protocol'):
            self.assertQueryBetween(servo, 'T', 0, 10000)

    # Query Model String
    def test_ModelString_QMS(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'MS')

    # Query Firmware Version
    def test_FirmwareVersion_QF(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'F')

    # Query Serial Number
    def test_SerialNumber_QN(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'N')

    # (PRIVATE) Query Model Code
    def test_ModelCode_QM(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'M')

    # Query LED Blink
    def test_LEDBlink_LB(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'LB')
            bus.write_command(servo, 'CLB1')
            self.assertQueryEqual(servo, 'LB', 1)
            bus.write_command(servo, 'CLB2')
            self.assertQueryEqual(servo, 'LB', 2)
            bus.write_command(servo, 'CLB4')
            self.assertQueryEqual(servo, 'LB', 4)
            bus.write_command(servo, 'CLB8')
            self.assertQueryEqual(servo, 'LB', 8)
            bus.write_command(servo, 'CLB16')
            self.assertQueryEqual(servo, 'LB', 16)
            bus.write_command(servo, 'CLB32')
            self.assertQueryEqual(servo, 'LB', 32)
            bus.write_command(servo, 'CLB63')
            self.assertQueryEqual(servo, 'LB', 63)
            bus.write_command(servo, 'CLB0')
            self.assertQueryEqual(servo, 'LB', 0)
            bus.write_command(servo, 'RESET')
            time.sleep(1.5)

    # (PRIVATE) Query Position Origin
    def test_PositionOrigin_PO(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'PO')
            bus.write_command(servo, 'CPO1')
            self.assertQueryEqual(servo, 'PO', 1)
            bus.write_command(servo, 'CPO0')
            self.assertQueryEqual(servo, 'PO', 0)
            bus.write_command(servo, 'RESET')
            time.sleep(1.5)

    # (PRIVATE) Query Initial Sequence
    @unittest.SkipTest
    def test_InitialSequence_QIS(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'IS')

    # (PRIVATE) Query Initial Sequence RC
    @unittest.SkipTest
    def test_RCInitialSequence_QRIS(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'RIS')

    # (PRIVATE) Query Command Reply
    def test_CommandReply_QCR(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'CR')

    # # (PRIVATE) Query Current Torque
    # def test_CurrentTorque_QTQ(self):
    #     for servo in get_servos('query'):
    #         self.assertQuery(servo, 'TQ')

    # # (PRIVATE) Query Torque Target
    # def test_TorqueTarget_QTQT(self):
    #     for servo in get_servos('query'):
    #         self.assertQuery(servo, 'TQT')

    # (PRIVATE) Query Torque Maximum
    def test_TorqueMaximum_TQM(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'TQM')
            bus.write_command(servo, 'CGM500')
            self.assertQueryEqual(servo, 'TQM', 500)
            bus.write_command(servo, 'CGM1000')
            self.assertQueryEqual(servo, 'TQM', 1000)

    # (PRIVATE) Query Control Mode
    def test_ControlMode_QY(self):
        for servo in get_servos('protocol'):
            self.assertQuery(servo, 'Y')
            bus.write_command(servo, 'Y1')
            self.assertQueryEqual(servo, 'Y', 1)
            bus.write_command(servo, 'Y0')
            self.assertQueryEqual(servo, 'Y', 0)


@unittest.SkipTest
class LssActionTests(LssTestCase):

    # Action Move in Degree
    def test_MoveTo_D(self):
        for servo in get_servos('action'):
            bus.write_command(servo, 'D0')
            time.sleep(0.5)
            self.assertQueryNear(servo, 'D', 0, 10)
            bus.write_command(servo, 'D450')
            time.sleep(0.5)
            self.assertQueryEqual(servo, 'DT', 450)
            self.assertQueryNear(servo, 'D', 450, 10)
            bus.write_command(servo, 'D-450')
            time.sleep(0.8)
            self.assertQueryEqual(servo, 'DT', -450)
            self.assertQueryNear(servo, 'D', -450, 10)
            bus.write_command(servo, 'D0')
            time.sleep(0.5)
            self.assertQueryEqual(servo, 'DT', 0)
            self.assertQueryNear(servo, 'D', 0, 10)

    # Action Move in Degree Relative
    def test_MoveBy_MD(self):
        for servo in get_servos('action'):
            bus.write_command(servo, 'D0')
            time.sleep(0.5)
            self.assertQueryNear(servo, 'D', 0, 10)
            bus.write_command(servo, 'MD450')
            time.sleep(0.5)
            self.assertQueryNear(servo, 'D', 450, 10)
            bus.write_command(servo, 'MD-900')
            time.sleep(0.8)
            self.assertQueryNear(servo, 'D', -450, 10)
            bus.write_command(servo, 'MD450')
            time.sleep(0.5)
            self.assertQueryNear(servo, 'D', 0, 10)

    # Action Wheel in Degree
    def test_WheelSpeed_WD(self):
        for servo in get_servos('action'):
            bus.write_command(servo, 'WD100')
            time.sleep(0.5)
            self.assertQueryNear(servo, 'WD', 100, 10)
            bus.write_command(servo, 'WD-100')
            time.sleep(1)
            self.assertQueryNear(servo, 'WD', -100, 10)
            bus.write_command(servo, 'D0')
            time.sleep(0.5)
            bus.write_command(servo, 'L')

    # Action Wheel in RPM
    def test_WheelSpeedRPM_WR(self):
        for servo in get_servos('action'):
            bus.write_command(servo, 'WR20')
            time.sleep(0.5)
            self.assertQueryNear(servo, 'WR', 20, 1)
            bus.write_command(servo, 'WR-20')
            time.sleep(1)
            self.assertQueryNear(servo, 'WR', -20, 1)
            bus.write_command(servo, 'D0')
            time.sleep(0.5)
            bus.write_command(servo, 'L')

    # Action Position in PWM
    def test_RCMoveTo_P(self):
        for servo in get_servos('action'):
            bus.write_command(servo, 'P1500')
            time.sleep(0.5)
            self.assertQueryNear(servo, 'P', 1500, 100)
            bus.write_command(servo, 'P2000')
            time.sleep(0.5)
            self.assertQueryNear(servo, 'P', 2000, 100)
            bus.write_command(servo, 'P1000')
            time.sleep(0.8)
            self.assertQueryNear(servo, 'P', 1000, 100)
            bus.write_command(servo, 'P1500')
            time.sleep(0.5)
            self.assertQueryNear(servo, 'P', 1500, 100)

    # Action Raw Duty Cycle Move
    def test_FreeMove_RDM(self):
        for servo in get_servos('action'):
            bus.write_command(servo, 'RDM250')
            time.sleep(0.5)
            self.assertQueryEqual(servo, 'MD', 250)
            bus.write_command(servo, 'RDM-250')
            time.sleep(0.5)
            self.assertQueryEqual(servo, 'MD', -250)
            time.sleep(0.5)
            bus.write_command(servo, 'D0')
            time.sleep(0.5)

if __name__ == '__main__':
    unittest.main()
    bus.close()

