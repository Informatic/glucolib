import serial
from serial.tools.list_ports import comports
import datetime
import locale

# FIXME RTFM
readingTypes = {
    'G': 'Glucose',
    }


class GlucometerException(Exception): pass
class DeviceNotConnected(GlucometerException): pass
class DeviceInvalid(GlucometerException): pass

# Abbott Optium Xido glucometer
class OptiumXido(object):
    def __init__(self, path='/dev/ttyUSB0'):
        try:
            self.ser = serial.Serial(path, 19200, timeout=0.1,
                                     interCharTimeout=0.1)
        except Exception, ex:
            raise DeviceNotConnected(ex)

    def fetch_data(self):
        """Returns glucometer readings in form of list of tuples:
            [(value, readingType, datetime)]

            value
                saved measurement

            readingType
                str('G') - Glucose

            datetime
                datetime.datetime object containing date of measurement
        """

        resp = self.command('$xmem')

        # First line of response is empty, we check it to distinguish invalid
        # devices
        if resp[0] != '':
            raise DeviceInvalid()

        readings_count = resp[4]
        raw_dataset = resp[5:5 + int(readings_count)]
        readings = []

        for reading in raw_dataset:
            value, month, day, year, time, reading_type, _ = reading.split()

            saved = locale.setlocale(locale.LC_ALL, 'C')
            try:
                parsed_datetime = datetime.datetime.strptime(
                    ' '.join([month, day, year, time]), '%b %d %Y %H:%M')
            finally:
                locale.setlocale(locale.LC_ALL, saved)

            readings.append((reading_type, int(value), parsed_datetime))

        return readings

    def device_info(self):
        """Return dict containing different system-specific values, including:

            S/N
                Device serial number

            Ver
                Software version

            Clock
                Current date and time set on device

        """
        resp = self.command('$colq')

        if resp[-1] != 'CMD OK':
            raise DeviceInvalid()

        return dict((n.partition(':')[0], n.split('\t')[1:])
                    for n in resp[:-1])

    def close(self):
        if self.ser:
            self.ser.close()

    def command(self, cmd):
        self.ser.write(cmd + "\r\n")

        # FIXME readlines fails when packet is split into multiple buffers (eg.
        # in $colq response)
        #time.sleep(1)

        resp = [l.strip() for l in self.ser.readlines()]

        # If no data received then device is not connected or sleeping (data
        # cable connector replug is needed)
        if not resp:
            raise DeviceNotConnected('Device not responding')

        return resp


supported_devices = {
    ('1a61', '3420'): OptiumXido
    }


def list_devices():
    """Return list of tuples depicting connected devices found and apropriate
    classes to use for communication."""
    results = list()

    for port, desc, hwids in comports():
        for (pid, vid), cls in supported_devices.items():
            if pid in hwids.lower() and vid in hwids.lower():
                # FIXME yield?
                results.append((port, cls))
                break

    return results
