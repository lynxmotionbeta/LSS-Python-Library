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


if __name__ == '__main__':
    unittest.main()
    bus.close()

