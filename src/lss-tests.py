from lss import LssPacket, LssBus
import math
import time
import unittest

# baud = 250000
# baud = 500000
baud = 921600

port_name = 'COM4'

servos = [0, 100]

bus = LssBus(port_name, baud, low_latency=True)  # open serial port

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
        self.assertGreaterEqual(p.value, value - precision)
        self.assertLessEqual(p.value, value + precision)

    def assertBetween(self, v: int, min: int, max: int):
        self.assertGreaterEqual(v, min)
        self.assertLessEqual(v, max)

    def assertServoQueryWithin(self, servo: int, parameter: str, value: int, precision: int = 5):
        bus.write_command(servo, f'Q{parameter}')
        p = bus.read()
        self.assertIsNotNone(p)
        self.assertTrue(p.known)
        self.assertEqual(p.command, 'D')
        self.assertBetween(p.value, value - precision, value + precision)

class LssSelfTests(LssTestCase):

    # Configure & Verify LED
    #def test_LED(self):
        for servo in servos:
            bus.write_command(servo, 'CLED2')
            time.sleep(0.25)
            self.assertQueryEqual(servo, 'LED', 2)
            bus.write_command(servo, 'CLED0')

    # Configure & Verify Stiffnesses
        #def test_STIFF(self):
            for servo in servos:
                bus.write_command(servo, 'AH')

class LssQueryTests(LssTestCase):

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
        self.assertGreaterEqual(p.value, value - precision)
        self.assertLessEqual(p.value, value + precision)

    # Query Motor ID
    def test_QID(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'ID', 0, 254)
    # Query Baud Rate
    def test_QB(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'B', 9600, 921600)
    # Query Current Position
    def test_QD(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'D', -1800, 1800)
    # Query RC Position
    def test_QP(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'P', -1800, 1800)
    # Query Wheel Speed
    def test_QWD(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'WD', -1800, 1800)
    # Query Wheel RPM Speed
    def test_QWR(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'WR', -1800, 1800)
    # Query Speed Target
    def test_QVT(self):
        for servo in servos:
            self.assertQuery(servo, 'VT')
    # Query Duty Cycle
    def test_QMD(self):
        for servo in servos:
            self.assertQuery(servo, 'MD')
#    # Query Status
#    def test_Q(self):
#        for servo in servos:
#            self.assertQuery(servo, '')
    # Query Current RC Speed
    def test_QS(self):
        for servo in servos:
            self.assertQuery(servo, 'S')
    # Query Motion Control
    def test_QEM(self):
        for servo in servos:
            self.assertQuery(servo, 'EM')
    # Query Origin Offset
    def test_QO(self):
        for servo in servos:
            self.assertQuery(servo, 'O')
    # Query RC Angular Range
    def test_QAR(self):
        for servo in servos:
            self.assertQuery(servo, 'AR')
    # Query Stiffness
    def test_QAS(self):
        for servo in servos:
            self.assertQuery(servo, 'AS')
    # Query Holding Stiffness
    def test_QAH(self):
        for servo in servos:
            self.assertQuery(servo, 'AH')
    # Query Holding Delta
    def test_QHD(self):
        for servo in servos:
            self.assertQuery(servo, 'HD')
    # Query Acceleration
    def test_QAA(self):
        for servo in servos:
            self.assertQuery(servo, 'AA')
    # Query Deceleration
    def test_QAD(self):
        for servo in servos:
            self.assertQuery(servo, 'AD')
    # Query Gyre Direction
    def test_QG(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'G', -1, 1)
#    # Query First Position *** Return DIS
#    def test_QFD(self):
#        for servo in servos:
#            self.assertQuery(servo, 'FD')
    # Query Position Limits Enabled
    def test_QLE(self):
        for servo in servos:
            self.assertQuery(servo, 'LE')
    # Query Positive Direction Limit
    def test_QLP(self):
        for servo in servos:
            self.assertQuery(servo, 'LP')
    # Query Negative Direction Limit
    def test_QLN(self):
        for servo in servos:
            self.assertQuery(servo, 'LN')
    # Query Current Soft Limit Counter (PRIVATE)
    def test_QCSL(self):
        for servo in servos:
            self.assertQuery(servo, 'CSL')
    # Query Position Filtering
    def test_QFPC(self):
        for servo in servos:
            self.assertQuery(servo, 'FPC')
    # Query Maximum Motor Duty
    def test_QMMD(self):
        for servo in servos:
            self.assertQuery(servo, 'MMD')
    # Query IPMS Enabled (PRIVATE)
    def test_QIPE(self):
        for servo in servos:
            self.assertQuery(servo, 'IPE')
    # Query Speed
    def test_QSD(self):
        for servo in servos:
            self.assertQuery(servo, 'SD')
    # Query Speed in RPM
    def test_QSR(self):
        for servo in servos:
            self.assertQuery(servo, 'SR')
    # Query Voltage
    def test_QV(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'V', 0, 14000)
    # Query Temperature
    def test_QT(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'T', 0, 1000)
    # Query Current
    def test_QC(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'T', 0, 10000)
    # Query Model String
    def test_QMS(self):
        for servo in servos:
            self.assertQuery(servo, 'MS')
    # Query Firmware Version
    def test_QF(self):
        for servo in servos:
            self.assertQuery(servo, 'F')
    # Query Serial Number
    def test_QN(self):
        for servo in servos:
            self.assertQuery(servo, 'N')
    # (PRIVATE) Query Model Code
    def test_QM(self):
        for servo in servos:
            self.assertQuery(servo, 'M')
    # Query LED
    def test_QLED(self):
        for servo in servos:
            self.assertQueryBetween(servo, 'LED', 0, 7)
    # Query LED Blink
    def test_QLB(self):
        for servo in servos:
            self.assertQuery(servo, 'LB')
    # (PRIVATE) Query Position Origin
    def test_QPO(self):
        for servo in servos:
            self.assertQuery(servo, 'PO')
    # (PRIVATE) Query Initial Sequence
    def test_QIS(self):
        for servo in servos:
            self.assertQuery(servo, 'IS')
    # (PRIVATE) Query Initial Sequence RC
    def test_QRIS(self):
        for servo in servos:
            self.assertQuery(servo, 'RIS')
    # (PRIVATE) Query Command Reply
    def test_QCR(self):
        for servo in servos:
            self.assertQuery(servo, 'CR')
#    # (PRIVATE) Query Current Torque
#    def test_QTQ(self):
#        for servo in servos:
#            self.assertQuery(servo, 'TQ')
#    # (PRIVATE) Query Torque Target
#    def test_QTQT(self):
#        for servo in servos:
#            self.assertQuery(servo, 'TQT')
    # (PRIVATE) Query Torque Maximum
    def test_QTQM(self):
        for servo in servos:
            self.assertQuery(servo, 'TQM')
    # (PRIVATE) Query Control Mode
    def test_QY(self):
        for servo in servos:
            self.assertQuery(servo, 'Y')

class LssActionTests(LssTestCase):

    #def test_D(self):
        for servo in servos:
            bus.write_command(servo, 'D0')
            time.sleep(0.8)
            self.assertServoQueryWithin(servo, 'D', 0, 10)
            bus.write_command(servo, 'D900')
            time.sleep(0.8)
            self.assertServoQueryWithin(servo, 'D', 900, 10)
            bus.write_command(servo, 'D0')
            time.sleep(0.8)
            self.assertServoQueryWithin(servo, 'D', 0, 10)

if __name__ == '__main__':
    unittest.main()
    bus.close()

