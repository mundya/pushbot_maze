
class Dummy(object):
    def send(self, message):
        return
    def receive(self):
        return ''


class Serial(object):
    def __init__(self, port, baud):
        import serial
        self.conn = serial.Serial(port, baudrate=baud, rtscts=True, timeout=0)
    def send(self, message):
        self.conn.write(message)
    def receive(self):
        return self.conn.read(1024)
    def close(self):
        self.conn.close()

