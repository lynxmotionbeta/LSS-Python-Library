from lss import LssPacket, LssBus
import math
import time
import unittest

# baud = 250000
# baud = 500000
baud = 921600

port_name = '/dev/ttyUSB0'

servos = [0]

bus = LssBus(port_name, baud, low_latency=True)  # open serial port

class LssQueryTests(unittest.TestCase):
    def test_QD(self):
        for servo in servos:
            bus.write_command(servo, 'QD')  # write a string
            p = bus.read()
            self.assertIsNotNone(p)
            self.assertTrue(p.known)
            self.assertEqual(p.command, 'D')
            #self.assertIsNot(p.value, 0)    # possibly could be zero

    def test_QC(self):
        for servo in servos:
            bus.write_command(servo, 'QC')  # write a string
            p = bus.read()
            self.assertIsNotNone(p)
            self.assertTrue(p.known)
            self.assertEqual(p.command, 'C')

    def test_QS(self):
        for servo in servos:
            bus.write_command(servo, 'QS')  # write a string
            p = bus.read()
            self.assertIsNotNone(p)
            self.assertTrue(p.known)
            self.assertEqual(p.command, 'S')



class LssActionTests(unittest.TestCase):

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

    def test_D(self):
        for servo in servos:
            bus.write_command(servo, 'D1500')
            time.sleep(1.5)
            self.assertServoQueryWithin(servo, 'D', 1500, 10)
            bus.write_command(servo, 'D500')
            time.sleep(0.8)
            self.assertServoQueryWithin(servo, 'D', 500, 10)
            bus.write_command(servo, 'D0')
            time.sleep(0.8)
            self.assertServoQueryWithin(servo, 'D', 0, 10)
            bus.write_command(servo, 'D-500')
            time.sleep(0.8)
            self.assertServoQueryWithin(servo, 'D', -500, 10)
            bus.write_command(servo, 'D-1500')
            time.sleep(0.8)
            self.assertServoQueryWithin(servo, 'D', -1500, 10)
            bus.write_command(servo, 'D0')
            time.sleep(1.2)
            self.assertServoQueryWithin(servo, 'D', 0, 10)


if __name__ == '__main__':
    unittest.main()
    bus.close()

