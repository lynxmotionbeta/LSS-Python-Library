import re
import unittest
import array
import serial


REQUEST = '#'
REPLY = '*'

QUERY = 'Q'
ACTION = 'A'
CONFIG = 'C'

LssCommandDescription = {
    'ID': 'Device ID',
    'B': 'Baudrate',
    'D': 'Position in Degrees',
    'DT': 'Position in Degrees',
    'MD': 'Move in Degrees',
    'WD': 'Wheel mode in Degrees',
    'VT': 'Wheel mode in Degrees',
    'WR': 'Wheel mode in RPM',
    'P': 'Position in PWM',
    'M': 'Move in PWM (relative)',
    'RDM': 'Raw Duty-Cycle Move',
    'Q': 'Query Status',
    'L': 'Limp',
    'H': 'Halt & Hold',
    'EM': 'Enable Motion Profile',
    'FPC': 'Filter Position Count',
    'O': 'Origin Offset',
    'AR': 'Angular Range',
    'AS': 'Angular Stiffness',
    'AH': 'Angular Holding Stiffness',
    'AA': 'Angular Acceleration',
    'AD': 'Andular Deceleration',
    'G': 'Gyre Direction',
    'FD': 'First Position',
    'MMD': 'Maximum Motor Duty',
    'S': 'Query Speed',
    'SD': 'Maximum Speed in Degrees',
    'SD2': 'Instant Speed in Degrees',
    'SR': 'Maximum Speed in RPM',
    'SR2': 'Instant Speed in RPM',
    'V': 'Voltage',
    'T': 'Temperature',
    'C': 'Current (Amps)',
    'LED': 'LED Color',
    'LB': 'LED Blinking',
    'MS': 'Model String',
    'F': 'Firmware',
    'N': 'Serial Number',
    'HD': 'Holding Delta',
    'LN': 'Negative Direction Limit',
    'LP': 'Positive Direction Limit',
    'LE': 'First Position Limits Enabled',
    'CSL': 'Current Soft Limit Counter',
    'IPE': 'IPMS Enabled',
    'PO': 'Position Origin',
    'IS': 'Initial Sequence',
    'RIS': 'Initial Sequence RC',
    'CR': 'Command Reply',
    'TQ': 'Current Torque',
    'TQT': 'Torque Target',
    'TQM': 'Torque Maximum',
    'Y': 'Control Mode'
}

LssCommandModifier = {
    'S': 'Speed',
    'SD': 'Speed in Degrees',
    'T': 'Timed Move',
    'CH': 'Current Hold',
    'CL': 'Current Limp'
}

packet_re = re.compile('(#|\\*)(\\d+)(Q|C)?([a-z]*)([0-9-]+)?([a-z0-9\\-.]*)?', re.IGNORECASE)


class LssException(Exception):
    def __init__(self, message: str):
        self.message = message


class LssPacket(object):

    id: int
    direction: REQUEST or REPLY
    kind: ACTION or QUERY or CONFIG

    command: str
    description: str
    value: int or float or str

    known: bool

    def __init__(self, packet: str):
        self.parse(packet)

    def parse(self, packet: str):
        m = packet_re.match(packet)
        if m:
            self.direction = m[1]
            self.id = int(m[2])
            self.kind = m[3] if m[3] is not None else ACTION
            self.command = m[4]
            self.value = None
            extra = m[6]
            if self.kind == QUERY and self.command == '':
                # the lonely Q command for query status
                self.command = 'Q'
            if m[5]:
                if m[5] == '-':
                    # only minus matched, this is not an integer value
                    extra = m[5] + extra
                else:
                    self.value = int(m[5])
            # possibly we have a string command
            # m[6] may have a continuation of the response
            if len(extra) > 0:
                if self.direction == REPLY and self.kind == QUERY:
                    if self.command.startswith('MS'):
                        self.value = self.command[2:] + extra
                        self.command = 'MS'
                    elif self.command.startswith('F'):
                        self.value = self.command[1:] + extra
                        self.command = 'F'
                    elif self.command.startswith('N'):
                        self.value = self.command[1:] + extra
                        self.command = 'N'
                    elif extra is not None:
                        # garbage value after command
                        raise LssException('Garbled packet value')
                else:
                    self.value = None

            if self.command in LssCommandDescription:
                self.description = LssCommandDescription[self.command]
                self.known = True
            else:
                self.description = 'Unknown command'
                self.known = False
        else:
            raise LssException('Invalid packet')



class LssBus(object):
    def __init__(self, port, baud, low_latency=True):
        self.ser = serial.Serial(port, baud, timeout=1)  # open serial port
        if low_latency:
            self.set_low_latency(True, True)
        self.eol = b'\r'
        self.revert_low_latency = False

    def baudrate(self, baudrate: int):
        self.ser.baudrate = baudrate

    def close(self):
        if self.revert_low_latency:
            self.set_low_latency(False, True)
        self.ser.close()
        self.ser = None

    def set_low_latency(self, enable_low_latency: bool, ignore_error=False):
        buf = array.array('i', [0] * 32)
        try:
            import fcntl
            import termios
            fcntl.ioctl(self.ser.fd, termios.TIOCGSERIAL, buf)

            # set or unset ASYNC_LOW_LATENCY flag
            if enable_low_latency:
                buf[4] |= 0x2000
                self.revert_low_latency = True
            else:
                buf[4] &= ~0x2000

            # set serial_struct
            fcntl.ioctl(self.ser.fd, termios.TIOCSSERIAL, buf)

        except ModuleNotFoundError as e:
            pass   # probably on windows
        except IOError as e:
            if ignore_error:
                if enable_low_latency:
                    print('warning: failed to set ASYNC_LOW_LATENCY on serial bus, communication will be slow.')
                return False
            else:
                raise ValueError('Failed to update ASYNC_LOW_LATENCY flag to {}: {}'.format(enable_low_latency, e))
        return True

    def write(self, packet: LssPacket or str):
        if not isinstance(packet, str):
            packet = str(packet)
        data = packet.encode('utf8') + self.eol
        self.ser.write(data)

    def write_command(self, id, command: str):
        data = f'#{id}{command}\r'.encode('utf8') + self.eol
        self.ser.write(data)

    def read_raw(self):
        leneol = len(self.eol)
        line = bytearray()
        while True:
            c = self.ser.read(1)
            if c:
                line += c
                if line[-leneol:] == self.eol:
                    line = line[0:len(line) - leneol]
                    break
            else:
                break
        return bytes(line)

    def read(self):
        raw = self.read_raw()
        if raw:
            return LssPacket(raw.decode())
        else:
            raise TimeoutError("no data available")

class LssPacketTests(unittest.TestCase):
    def assert_packet(self, p: LssPacket):
        self.assertIsNotNone(p)
        self.assertGreater(p.id, 0)
        self.assertLess(p.id, 50)
        self.assertIn(p.direction, [REQUEST, REPLY])
        self.assertIn(p.kind, [ACTION, QUERY, CONFIG])
        self.assertTrue(p.known)

    def test_command_position(self):
        self.assert_packet(LssPacket('#12D521'))

    def test_reply_model(self):
        p = LssPacket('*12QMSLSS-HT1')
        self.assert_packet(p)
        self.assertEqual(p.value, 'LSS-HT1')

    def test_reply_position(self):
        p = LssPacket('*12QD980')
        self.assert_packet(p)
        self.assertEqual(p.value, 980)

    def test_reply_neg_position(self):
        p = LssPacket('*19QD-1190')
        self.assert_packet(p)
        self.assertEqual(p.value, -1190)

    def test_reply_QS0(self):
        p = LssPacket('*19QS900')
        self.assert_packet(p)
        self.assertEqual(p.value, 900)

if __name__ == '__main__':
    unittest.main()
